"""真实学术 API 接入 · 严禁 LLM 编文献。

接入的 4 个公开 API:
- arXiv:预印本 · 公开 · 无 key
- Crossref:DOI 元数据 · 公开 · 无 key · 是 DOI 校验的权威源
- OpenAlex:开放学术图谱 · 公开 · 无 key
- Semantic Scholar:语义检索 · 可选 key(无 key 也能用,限速更严)

关键工程纪律:
- 任何引用必须有 DOI 或 arxiv_id
- 进入正文前必须 DOI 校验(Crossref verify)
- 没有 DOI 的 → 标 doi_verified=False → 前端警告
"""

import asyncio
from typing import Optional
import httpx
from urllib.parse import quote
from app.models.schemas import Paper
from app.config import settings


HTTP_TIMEOUT = httpx.Timeout(30.0)


# ============ arXiv ============
async def arxiv_search(query: str, limit: int = 10) -> list[Paper]:
    """arXiv API · ATOM feed → 解析。"""
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
    }
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
        except Exception as e:
            print(f"[arxiv] error: {e}")
            return []

    # 简单解析 ATOM(避免引 feedparser)
    import re
    text = r.text
    entries = re.findall(r"<entry>(.*?)</entry>", text, re.DOTALL)
    papers = []
    for entry in entries[:limit]:
        title = _xml_extract(entry, "title")
        summary = _xml_extract(entry, "summary")
        published = _xml_extract(entry, "published")
        arxiv_id_match = re.search(r"<id>http://arxiv\.org/abs/([^<]+)</id>", entry)
        arxiv_id = arxiv_id_match.group(1) if arxiv_id_match else None
        authors = re.findall(r"<name>([^<]+)</name>", entry)
        doi_match = re.search(r"<arxiv:doi[^>]*>([^<]+)</arxiv:doi>", entry)
        doi = doi_match.group(1) if doi_match else None

        year = int(published[:4]) if published else None

        papers.append(Paper(
            title=title.strip(),
            authors=authors,
            year=year,
            doi=doi,
            arxiv_id=arxiv_id,
            abstract=summary.strip()[:500] if summary else None,
            url=f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None,
            source="arxiv",
        ))
    return papers


def _xml_extract(text: str, tag: str) -> str:
    import re
    m = re.search(rf"<{tag}[^>]*>([^<]+)</{tag}>", text)
    return m.group(1) if m else ""


# ============ Crossref ============
async def crossref_search(query: str, limit: int = 10) -> list[Paper]:
    """Crossref Works API."""
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": limit}
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            r = await client.get(url, params=params, headers={
                "User-Agent": "ThesisAssistant/0.1 (https://github.com/OnelongX/aiagent)"
            })
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[crossref] error: {e}")
            return []

    papers = []
    for item in data.get("message", {}).get("items", []):
        year = None
        date_parts = item.get("issued", {}).get("date-parts", [])
        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        authors = []
        for a in item.get("author", []):
            given = a.get("given", "")
            family = a.get("family", "")
            name = f"{given} {family}".strip()
            if name:
                authors.append(name)

        papers.append(Paper(
            title=(item.get("title") or [""])[0],
            authors=authors,
            year=year,
            venue=(item.get("container-title") or [""])[0] if item.get("container-title") else None,
            doi=item.get("DOI"),
            url=item.get("URL"),
            source="crossref",
        ))
    return papers


async def crossref_verify_doi(doi: str) -> bool:
    """DOI 校验 · 关键纪律 · 引用进正文前必须验真。"""
    if not doi:
        return False
    url = f"https://api.crossref.org/works/{quote(doi)}"
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            r = await client.get(url)
            return r.status_code == 200
        except Exception:
            return False


# ============ OpenAlex ============
async def openalex_search(query: str, limit: int = 10) -> list[Paper]:
    """OpenAlex Works API."""
    url = "https://api.openalex.org/works"
    params = {"search": query, "per-page": limit}
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[openalex] error: {e}")
            return []

    papers = []
    for item in data.get("results", []):
        authors = [
            a.get("author", {}).get("display_name", "")
            for a in item.get("authorships", [])
        ]
        authors = [a for a in authors if a]

        doi = item.get("doi", "")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")

        papers.append(Paper(
            title=item.get("title") or item.get("display_name", ""),
            authors=authors,
            year=item.get("publication_year"),
            venue=item.get("primary_location", {}).get("source", {}).get("display_name") if item.get("primary_location") else None,
            doi=doi if doi else None,
            url=item.get("doi") or item.get("id"),
            abstract=_reconstruct_abstract(item.get("abstract_inverted_index")),
            source="openalex",
        ))
    return papers


def _reconstruct_abstract(inverted_index: Optional[dict]) -> Optional[str]:
    """OpenAlex 返回 inverted_index,需要重组成正常文本。"""
    if not inverted_index:
        return None
    positions = {}
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions[i] = word
    if not positions:
        return None
    max_pos = max(positions.keys())
    words = [positions.get(i, "") for i in range(max_pos + 1)]
    return " ".join(words).strip()[:500]


# ============ 融合检索 ============
async def search_papers(
    query: str,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    limit: int = 10,
) -> list[Paper]:
    """多源融合检索 · 并发请求 · 去重。"""
    results = await asyncio.gather(
        arxiv_search(query, limit),
        crossref_search(query, limit),
        openalex_search(query, limit),
        return_exceptions=True,
    )

    all_papers: list[Paper] = []
    for r in results:
        if isinstance(r, Exception):
            print(f"[search_papers] source error: {r}")
            continue
        all_papers.extend(r)

    # 按 DOI / title 去重
    seen_dois = set()
    seen_titles = set()
    deduped = []
    for p in all_papers:
        if p.doi and p.doi in seen_dois:
            continue
        title_norm = p.title.lower().strip()
        if title_norm in seen_titles:
            continue
        if p.doi:
            seen_dois.add(p.doi)
        seen_titles.add(title_norm)

        # 年份过滤
        if year_from and p.year and p.year < year_from:
            continue
        if year_to and p.year and p.year > year_to:
            continue

        deduped.append(p)

    # DOI 校验(并发)· 标 doi_verified
    async with asyncio.TaskGroup() as tg:
        tasks = {}
        for p in deduped[:limit]:
            if p.doi:
                tasks[p.doi] = tg.create_task(crossref_verify_doi(p.doi))
    for p in deduped[:limit]:
        if p.doi and p.doi in tasks:
            p.doi_verified = tasks[p.doi].result()

    return deduped[:limit]
