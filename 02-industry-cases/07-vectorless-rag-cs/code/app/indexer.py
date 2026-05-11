"""PageIndex integration for document indexing with semantic enhancement.
Supports PDF and Markdown files. Optimized spec sheet parsing."""

import os
import sys
import json
import asyncio
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Add PageIndex to path
sys.path.insert(0, str(Path(__file__).parent.parent / "PageIndex"))

from pageindex import page_index_main
from pageindex.page_index_md import md_to_tree
from pageindex.utils import ConfigLoader, structure_to_list, get_leaf_nodes
from app.spec_parser import parse_spec_sheet, format_spec_for_retrieval, is_solar_storage_spec, extract_full_text

INDEXES_DIR = Path(__file__).parent / "indexes"
KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("CHATGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE") or None
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


def get_config(model: str = "gpt-4o-mini"):
    """Get PageIndex configuration."""
    config_loader = ConfigLoader()
    opt = config_loader.load({
        "model": model,
        "if_add_node_summary": "yes",
        "if_add_doc_description": "yes",
        "if_add_node_text": "no",
        "max_page_num_each_node": 10,
        "max_token_num_each_node": 20000,
    })
    return opt


# === Spec Sheet PDF Optimization ===

def extract_tables_from_pdf(pdf_path: str) -> list[dict]:
    """Extract tables from PDF pages using PyMuPDF for spec sheets."""
    tables = []
    try:
        import fitz
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Extract tables using PyMuPDF's built-in table detection
            try:
                page_tables = page.find_tables()
                for table in page_tables:
                    # Convert table to structured format
                    rows = []
                    for row in table.extract():
                        rows.append([cell if cell else "" for cell in row])
                    if rows and len(rows) > 1:  # At least header + 1 data row
                        tables.append({
                            "page": page_num + 1,
                            "header": rows[0],
                            "rows": rows[1:],
                            "text": format_table_as_text(rows),
                        })
            except Exception:
                pass  # Table detection not available in older PyMuPDF
        doc.close()
    except Exception as e:
        print(f"Table extraction failed: {e}")
    return tables


def format_table_as_text(rows: list[list[str]]) -> str:
    """Format table rows into readable text for indexing."""
    if not rows:
        return ""
    lines = []
    header = rows[0]
    lines.append(" | ".join(str(h) for h in header))
    lines.append("-" * 40)
    for row in rows[1:]:
        lines.append(" | ".join(str(c) for c in row))
    return "\n".join(lines)


def is_spec_sheet(pdf_path: str) -> bool:
    """Heuristic to detect if a PDF is a product spec/datasheet."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        if len(doc) > 10:
            doc.close()
            return False  # Spec sheets are usually short
        text = ""
        for i in range(min(3, len(doc))):
            text += doc[i].get_text().lower()
        doc.close()
        spec_keywords = ["specification", "datasheet", "data sheet", "technical data",
                         "dimensions", "weight", "voltage", "power", "efficiency",
                         "规格", "参数", "技术数据", "尺寸", "功率", "电压",
                         "model", "rated", "max", "min", "typ", "unit"]
        matches = sum(1 for kw in spec_keywords if kw in text)
        return matches >= 3
    except Exception:
        return False


def enhance_spec_sheet(result: dict, pdf_path: str, model: str = "gpt-4o-mini") -> dict:
    """Extra processing for spec/datasheet PDFs: extract tables, parameters."""
    tables = extract_tables_from_pdf(pdf_path)
    if not tables:
        return result

    # Add table data to the index structure
    result["tables"] = []
    for t in tables:
        result["tables"].append({
            "page": t["page"],
            "header": t["header"],
            "row_count": len(t["rows"]),
        })

    # Use LLM to extract structured parameters from tables
    table_texts = "\n\n".join(t["text"] for t in tables[:5])  # Limit to 5 tables
    if table_texts:
        try:
            resp = _get_client().chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": f"""从以下产品规格书的表格数据中提取结构化参数，返回 JSON：

表格数据：
{table_texts[:3000]}

要求：
1. "parameters": 数组，每个元素包含 "name"(参数名，中文), "value"(值), "unit"(单位)
2. "product_name": 产品名称
3. "product_model": 产品型号
4. "key_specs": 3-5个核心规格的中文简述

仅返回 JSON。"""}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            spec_data = json.loads(resp.choices[0].message.content)
            result["parameters"] = spec_data.get("parameters", [])
            result["product_name"] = spec_data.get("product_name", "")
            result["product_model"] = spec_data.get("product_model", "")
            result["key_specs"] = spec_data.get("key_specs", [])
            result["doc_type"] = "产品规格书"
        except Exception as e:
            print(f"Spec parameter extraction failed: {e}")

    return result


# === Markdown Indexing ===

def index_markdown(md_path: str, model: str = "gpt-4o-mini") -> dict:
    """Index a Markdown file using PageIndex md_to_tree."""
    result = asyncio.run(md_to_tree(
        md_path,
        if_thinning=True,
        min_token_threshold=50,
        if_add_node_summary="yes",
        summary_token_threshold=500,
        model=model,
        if_add_doc_description="yes",
        if_add_node_text="no",
        if_add_node_id="yes",
    ))

    # Flatten tree structure for consistency with PDF index format
    result["structure"] = flatten_md_tree(result.get("structure", []))
    return result


def flatten_md_tree(tree: list, depth: int = 0) -> list:
    """Flatten nested MD tree into flat list with start/end line as indices."""
    flat = []
    for node in tree:
        flat_node = {
            "title": node.get("title", ""),
            "node_id": node.get("node_id", ""),
            "summary": node.get("summary", ""),
            "start_index": node.get("line_num", 0),
            "end_index": node.get("line_num", 0),
            "depth": depth,
        }
        if node.get("text"):
            flat_node["text"] = node["text"]
        flat.append(flat_node)
        if node.get("nodes"):
            flat.extend(flatten_md_tree(node["nodes"], depth + 1))
    # Update end_index based on next node's start
    for i in range(len(flat) - 1):
        flat[i]["end_index"] = flat[i + 1]["start_index"] - 1
    if flat:
        flat[-1]["end_index"] = flat[-1]["start_index"] + 10  # Estimate
    return flat


# === Semantic Enhancement ===

def semantic_enhance(result: dict, model: str = "gpt-4o-mini") -> dict:
    """Post-process index with LLM for semantic enhancement."""
    doc_name = result.get("doc_name", "")
    doc_desc = result.get("doc_description", "")
    structure = result.get("structure", [])

    # Step 1: Enhance document-level metadata
    if doc_desc:
        try:
            resp = _get_client().chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": f"""请对以下文档描述进行语义增强处理，返回 JSON 格式：

原始描述：{doc_desc}
文档名：{doc_name}

要求：
1. "description_zh": 将描述翻译成简洁准确的中文（2-3句话）
2. "keywords": 提取 5-8 个核心关键词（中文），用于检索匹配
3. "doc_type": 判断文档类型（如：产品手册、用户指南、技术规格、FAQ、政策文件、API文档、技术文章等）
4. "domain": 所属领域

仅返回 JSON，不要其他内容。"""}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            doc_meta = json.loads(resp.choices[0].message.content)
            result["doc_description_zh"] = doc_meta.get("description_zh", doc_desc)
            result["keywords"] = doc_meta.get("keywords", [])
            if not result.get("doc_type"):
                result["doc_type"] = doc_meta.get("doc_type", "")
            result["domain"] = doc_meta.get("domain", "")
        except Exception as e:
            print(f"Doc-level enhancement failed: {e}")
            result["doc_description_zh"] = doc_desc

    # Step 2: Enhance each chunk in batches
    if structure:
        batch_size = 5
        for i in range(0, len(structure), batch_size):
            batch = structure[i:i + batch_size]
            batch_info = json.dumps([{
                "node_id": c.get("node_id", ""),
                "title": c.get("title", ""),
                "summary": (c.get("summary", "") or "")[:500],
                "start_index": c.get("start_index", 0),
                "end_index": c.get("end_index", 0),
            } for c in batch], ensure_ascii=False)

            try:
                resp = _get_client().chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": f"""请对以下文档分块进行语义增强。为每个分块返回：

分块数据：
{batch_info}

要求为每个分块生成：
1. "title_zh": 中文标题
2. "summary_zh": 中文摘要（1-2句话）
3. "keywords": 3-5个中文关键词
4. "entities": 关键实体
5. "semantic_tags": 2-3个语义标签

返回 JSON 数组格式，用 node_id 标识。"""}],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )
                enhanced = json.loads(resp.choices[0].message.content)
                items = enhanced if isinstance(enhanced, list) else enhanced.get("chunks", enhanced.get("nodes", enhanced.get("data", [])))
                if isinstance(items, list):
                    for item in items:
                        nid = item.get("node_id", "")
                        for chunk in batch:
                            if chunk.get("node_id") == nid:
                                chunk["title_zh"] = item.get("title_zh", "")
                                chunk["summary_zh"] = item.get("summary_zh", "")
                                chunk["keywords"] = item.get("keywords", [])
                                chunk["entities"] = item.get("entities", [])
                                chunk["semantic_tags"] = item.get("semantic_tags", [])
                                break
            except Exception as e:
                print(f"Chunk enhancement failed for batch {i}: {e}")
                for chunk in batch:
                    chunk.setdefault("title_zh", chunk.get("title", ""))
                    chunk.setdefault("summary_zh", chunk.get("summary", ""))
                    chunk.setdefault("keywords", [])
                    chunk.setdefault("entities", [])
                    chunk.setdefault("semantic_tags", [])

    result["enhanced"] = True
    return result


# === Main Index Functions ===

def index_pdf(pdf_path: str, model: str = "gpt-4o-mini") -> dict:
    """Index a PDF file, with solar/storage spec sheet deep parsing + semantic enhancement."""
    opt = get_config(model)
    result = page_index_main(pdf_path, opt)

    # Check if this is a solar/storage spec sheet
    full_text = extract_full_text(pdf_path)
    if is_solar_storage_spec(full_text):
        print(f"检测到光储产品规格书: {Path(pdf_path).name}，执行深度参数提取...")
        spec_data = parse_spec_sheet(pdf_path, model)
        if spec_data:
            result["spec_data"] = spec_data
            product_type = spec_data.get("product_info", {}).get("product_type", "")
            result["doc_type"] = product_type or "光储产品规格书"
            result["product_info"] = spec_data.get("product_info", {})
            # Store type-specific specs
            result["parameters"] = spec_data.get("electrical_specs_stc", [])
            result["spec_table"] = spec_data.get("spec_table", {})
            result["battery_specs"] = spec_data.get("battery_specs", {})
            result["battery_specs_list"] = spec_data.get("battery_specs_list", [])
            result["inverter_specs"] = spec_data.get("inverter_specs", {})
            result["inverter_specs_list"] = spec_data.get("inverter_specs_list", [])
            result["backup_specs"] = spec_data.get("backup_specs", {})
            result["controller_specs"] = spec_data.get("controller_specs", {})
            result["protection_specs"] = spec_data.get("protection_specs", {})
            result["temperature_coefficients"] = spec_data.get("temperature_coefficients", {})
            result["mechanical_specs"] = spec_data.get("mechanical_specs", {})
            result["warranty"] = spec_data.get("warranty", {})
            result["key_features"] = spec_data.get("key_features", [])
            result["key_specs"] = spec_data.get("key_features", [])[:5]
            result["product_name"] = spec_data.get("product_info", {}).get("series", "")
            result["product_model"] = spec_data.get("product_info", {}).get("model", "")
            # Add formatted spec text to retrieval index
            result["spec_text"] = format_spec_for_retrieval(spec_data)
            if spec_data.get("summary_zh"):
                result["doc_description_zh"] = spec_data["summary_zh"]
    elif is_spec_sheet(pdf_path):
        # Generic spec sheet (non solar/storage)
        print(f"检测到通用规格书: {Path(pdf_path).name}")
        result = enhance_spec_sheet(result, pdf_path, model)

    # Apply semantic enhancement
    print(f"语义增强索引: {Path(pdf_path).name}...")
    result = semantic_enhance(result, model)

    # Save index
    filename = Path(pdf_path).stem
    index_path = INDEXES_DIR / f"{filename}_structure.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def index_file(file_path: str, model: str = "gpt-4o-mini") -> dict:
    """Index any supported file (PDF or Markdown)."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return index_pdf(file_path, model)
    elif ext in (".md", ".markdown"):
        return index_md(file_path, model)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def index_md(md_path: str, model: str = "gpt-4o-mini") -> dict:
    """Index a Markdown file + semantic enhancement."""
    print(f"Indexing Markdown: {Path(md_path).name}...")
    result = index_markdown(md_path, model)

    # Apply semantic enhancement
    print(f"Enhancing index for {Path(md_path).name}...")
    result = semantic_enhance(result, model)

    # Save index
    filename = Path(md_path).stem
    index_path = INDEXES_DIR / f"{filename}_structure.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    result["file_type"] = "markdown"
    return result


def load_index(doc_name: str) -> dict | None:
    """Load a previously built index."""
    index_path = INDEXES_DIR / f"{doc_name}_structure.json"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def list_indexes() -> list[dict]:
    """List all available document indexes."""
    indexes = []
    for f in INDEXES_DIR.glob("*_structure.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        indexes.append({
            "filename": f.stem.replace("_structure", ""),
            "doc_name": data.get("doc_name", f.stem),
            "doc_description": data.get("doc_description_zh", data.get("doc_description", "")),
            "doc_type": data.get("doc_type", ""),
            "domain": data.get("domain", ""),
            "keywords": data.get("keywords", []),
            "sections": len(data.get("structure", [])),
            "enhanced": data.get("enhanced", False),
            "has_tables": bool(data.get("tables")),
            "has_parameters": bool(data.get("parameters")),
            "path": str(f),
        })
    return indexes


def get_tree_structure(doc_name: str) -> list | None:
    """Get the tree structure for a document."""
    data = load_index(doc_name)
    if data:
        return data.get("structure", [])
    return None


def get_all_structures(filenames: list[str] = None) -> list[dict]:
    """Load document structures, optionally filtered by filenames."""
    all_docs = []
    for f in INDEXES_DIR.glob("*_structure.json"):
        stem = f.stem.replace("_structure", "")
        if filenames is not None and stem not in filenames:
            continue
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        all_docs.append(data)
    return all_docs
