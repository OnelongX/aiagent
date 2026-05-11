"""Tree-based retrieval using PageIndex structures + LLM reasoning (Chinese)."""

import json
import os
import time
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("CHATGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE") or None
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


def _read_pdf_pages(pdf_path: str, start_page: int, end_page: int) -> str:
    """Read specific pages from a PDF file."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        texts = []
        for i in range(max(0, start_page - 1), min(end_page, len(doc))):
            texts.append(doc[i].get_text())
        doc.close()
        return "\n\n".join(texts)
    except Exception:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        texts = []
        for i in range(max(0, start_page - 1), min(end_page, len(reader.pages))):
            texts.append(reader.pages[i].extract_text() or "")
        return "\n\n".join(texts)


def _find_doc_path(doc_name: str) -> tuple[str | None, str]:
    """Find the document file path and type for a given document name."""
    for ext in (".pdf", ".PDF", ".md", ".markdown"):
        for p in KNOWLEDGE_DIR.glob(f"*{ext}"):
            if p.stem.lower() == doc_name.lower() or doc_name.lower() in p.stem.lower():
                file_type = "markdown" if ext.lower() in (".md", ".markdown") else "pdf"
                return str(p), file_type
    return None, ""


def _read_md_section(md_path: str, start_line: int, end_line: int) -> str:
    """Read specific line range from a Markdown file."""
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        start = max(0, start_line - 1)
        end = min(end_line, len(lines))
        return "".join(lines[start:end])
    except Exception:
        return ""


def _build_spec_context(doc_structure: dict) -> str:
    """Build extra context from spec sheet data — optimized for solar/storage products."""
    # Use dedicated spec_text if available (from spec_parser)
    spec_text = doc_structure.get("spec_text", "")
    if spec_text:
        return spec_text

    # Fallback to basic parameter extraction
    params = doc_structure.get("parameters", [])
    key_specs = doc_structure.get("key_specs", [])
    product_name = doc_structure.get("product_name", "")
    product_model = doc_structure.get("product_model", "")
    if not params and not key_specs:
        return ""
    parts = []
    if product_name:
        parts.append(f"产品：{product_name}")
    if product_model:
        parts.append(f"型号：{product_model}")
    if key_specs:
        parts.append("核心规格：" + " | ".join(str(s) for s in key_specs))

    # Temperature coefficients
    tc = doc_structure.get("temperature_coefficients", {})
    if tc and any(tc.values()):
        parts.append(f"温度系数：Pmpp={tc.get('pmpp','')} Voc={tc.get('voc','')} Isc={tc.get('isc','')}")

    # STC electrical specs
    if isinstance(params, list) and params:
        parts.append("STC 电气参数：")
        for p in params[:10]:
            if isinstance(p, dict):
                parts.append(f"  {p.get('model','')}: Pmpp={p.get('pmpp','')} Vmpp={p.get('vmpp','')} Impp={p.get('impp','')}")

    # Warranty
    warranty = doc_structure.get("warranty", {})
    if warranty:
        parts.append(f"质保：产品={warranty.get('product_warranty','')} 功率={warranty.get('power_warranty','')}")

    return "\n".join(parts)


def _build_tree_repr(structure: list) -> str:
    """Build a rich tree representation using enhanced semantic fields."""
    nodes = []
    for c in structure:
        node_info = {
            "node_id": c.get("node_id", ""),
            "标题": c.get("title_zh", c.get("title", "")),
            "页码": f"{c.get('start_index', 0)}-{c.get('end_index', 0)}",
        }
        # Add enhanced fields if available
        if c.get("summary_zh"):
            node_info["摘要"] = c["summary_zh"][:200]
        elif c.get("summary"):
            node_info["摘要"] = c["summary"][:200]
        if c.get("keywords"):
            node_info["关键词"] = c["keywords"]
        if c.get("entities"):
            node_info["实体"] = c["entities"]
        if c.get("semantic_tags"):
            node_info["标签"] = c["semantic_tags"]
        nodes.append(node_info)
    return json.dumps(nodes, ensure_ascii=False, indent=2)


def tree_search(query: str, doc_structure: dict, model: str = "gpt-4o-mini") -> dict:
    """
    Use LLM to reason through the tree index and find relevant sections.
    Uses enhanced semantic fields (Chinese) for better matching.
    """
    structure = doc_structure.get("structure", [])
    doc_name = doc_structure.get("doc_name", "Unknown")
    doc_desc = doc_structure.get("doc_description_zh", doc_structure.get("doc_description", ""))
    doc_keywords = doc_structure.get("keywords", [])
    doc_type = doc_structure.get("doc_type", "")

    tree_repr = _build_tree_repr(structure)
    spec_context = _build_spec_context(doc_structure)

    prompt = f"""你是一个专业的文档检索专家。根据用户查询和文档的层级树索引，
通过推理找到最相关的章节。

文档：{doc_name}
类型：{doc_type}
描述：{doc_desc}
关键词：{', '.join(doc_keywords) if doc_keywords else '无'}

树索引结构（包含语义增强信息）：
{tree_repr}
{('产品规格参数：' + chr(10) + spec_context) if spec_context else ''}

用户查询：{query}

检索指引：
1. 分析树索引结构，从整体到局部
2. 利用每个节点的关键词、实体和语义标签进行语义匹配
3. 不要仅做关键词匹配，要理解查询意图与节点内容的语义关联
4. 返回最相关的节点（最多3个），按相关度排序

请用 JSON 格式返回：
{{
    "reasoning": "逐步推理过程（中文），说明你如何分析查询意图并在树中定位",
    "search_path": ["根节点", "子节点", "目标节点"],
    "matched_nodes": [
        {{
            "title": "原始英文标题",
            "title_zh": "中文标题",
            "node_id": "节点ID",
            "start_index": 起始页码,
            "end_index": 结束页码,
            "relevance_score": 0.0到1.0的相关度分数,
            "reason": "中文说明为什么此节点与查询相关"
        }}
    ]
}}"""

    response = _get_client().chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def retrieve_context(query: str, all_doc_structures: list[dict], model: str = "gpt-4o-mini") -> dict:
    """
    Search across all indexed documents and retrieve relevant content.
    Returns matched sources with extracted text.
    """
    start_time = time.time()
    all_results = []

    for doc_structure in all_doc_structures:
        doc_name = doc_structure.get("doc_name", "Unknown")
        try:
            search_result = tree_search(query, doc_structure, model)
            matched_nodes = search_result.get("matched_nodes", [])

            doc_path, file_type = _find_doc_path(doc_name)
            for node in matched_nodes:
                node["doc_name"] = doc_name
                node["search_path"] = search_result.get("search_path", [])
                node["reasoning"] = search_result.get("reasoning", "")

                if doc_path:
                    start_idx = node.get("start_index", 1)
                    end_idx = node.get("end_index", start_idx)
                    if file_type == "markdown":
                        node["text"] = _read_md_section(doc_path, start_idx, end_idx)
                    else:
                        node["text"] = _read_pdf_pages(doc_path, start_idx, end_idx)
                else:
                    node["text"] = ""

            all_results.extend(matched_nodes)
        except Exception as e:
            print(f"检索 {doc_name} 出错: {e}")

    all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    top_results = all_results[:3]
    elapsed = time.time() - start_time

    return {
        "sources": top_results,
        "search_time": round(elapsed, 2),
        "total_docs_searched": len(all_doc_structures),
    }


def generate_answer(query: str, context: dict, chat_history: list[dict],
                    model: str = "gpt-4o-mini") -> str:
    """Generate a customer service answer based on retrieved context (Chinese)."""
    sources = context.get("sources", [])

    context_text = ""
    for i, source in enumerate(sources, 1):
        title = source.get("title_zh", source.get("title", "未知"))
        reason = source.get("reason", "")
        context_text += f"\n--- 来源 {i}：{source['doc_name']} - {title}（第 {source.get('start_index', '?')}-{source.get('end_index', '?')} 页）---\n"
        if reason:
            context_text += f"相关原因：{reason}\n"
        context_text += source.get("text", "无可用文本")[:3000]
        context_text += "\n"

    system_prompt = f"""你是一个专业、友好的智能客服 AI 助手。
你的回答基于 PageIndex RAG 树索引文档检索系统提供的知识。

回答规范：
- 使用中文回答用户问题
- 基于下方检索到的文档内容进行回答
- 如果文档中包含相关信息，请引用来源文档名和页码
- 如果文档内容不足以回答，请诚实告知并建议用户提供更多信息
- 使用项目编号或列表让回答更清晰
- 保持专业、简洁、有帮助的语气
- 如果原文是英文，请翻译成中文后回答

检索到的文档内容：
{context_text if context_text.strip() else "知识库中未找到相关文档。"}"""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in chat_history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": query})

    response = _get_client().chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
    )

    return response.choices[0].message.content
