"""引用格式化 · 确定性逻辑 · 不让 LLM 做。

支持 6 种格式:BibTeX / GB/T 7714 / APA / IEEE / MLA / Chicago。
"""

import re
from app.models.schemas import Paper


def _safe(s: str | None) -> str:
    return s.strip() if s else ""


def _authors_short(authors: list[str], max_n: int = 3) -> str:
    if not authors:
        return ""
    if len(authors) <= max_n:
        return ", ".join(authors)
    return ", ".join(authors[:max_n]) + ", et al."


def _bibtex_key(paper: Paper) -> str:
    """生成简单稳定的 BibTeX key。"""
    first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
    year = paper.year or "ND"
    word = re.sub(r"[^a-zA-Z0-9]", "", paper.title.split()[0])[:10] if paper.title else "X"
    return f"{first_author}{year}{word}".replace(" ", "")


def to_bibtex(paper: Paper) -> str:
    key = _bibtex_key(paper)
    entry_type = "article" if paper.venue else "misc"
    fields = [
        f"  title = {{{_safe(paper.title)}}}",
        f"  author = {{{ ' and '.join(paper.authors)}}}",
    ]
    if paper.year:
        fields.append(f"  year = {{{paper.year}}}")
    if paper.venue:
        fields.append(f"  journal = {{{_safe(paper.venue)}}}")
    if paper.doi:
        fields.append(f"  doi = {{{paper.doi}}}")
    if paper.url:
        fields.append(f"  url = {{{paper.url}}}")
    body = ",\n".join(fields)
    return f"@{entry_type}{{{key},\n{body}\n}}"


def to_gb7714(paper: Paper) -> str:
    """国标 · GB/T 7714"""
    a = _authors_short(paper.authors)
    parts = [a]
    parts.append(f"{_safe(paper.title)}[J]")
    if paper.venue:
        parts.append(_safe(paper.venue))
    if paper.year:
        parts.append(str(paper.year))
    if paper.doi:
        parts.append(f"DOI: {paper.doi}")
    return ". ".join(p for p in parts if p) + "."


def to_apa(paper: Paper) -> str:
    a = _authors_short(paper.authors)
    year = f"({paper.year})" if paper.year else ""
    return f"{a} {year}. {_safe(paper.title)}. {_safe(paper.venue) or ''}." + (f" doi:{paper.doi}" if paper.doi else "")


def to_ieee(paper: Paper) -> str:
    a = _authors_short(paper.authors)
    return f"{a}, \"{_safe(paper.title)},\" {_safe(paper.venue) or ''}, {paper.year or ''}." + (f" doi: {paper.doi}" if paper.doi else "")


def to_mla(paper: Paper) -> str:
    a = paper.authors[0] if paper.authors else ""
    if len(paper.authors) > 1:
        a += ", et al."
    return f"{a}. \"{_safe(paper.title)}.\" {_safe(paper.venue) or ''}, {paper.year or ''}."


def to_chicago(paper: Paper) -> str:
    a = _authors_short(paper.authors)
    return f"{a}. \"{_safe(paper.title)}.\" {_safe(paper.venue) or ''} ({paper.year or 'n.d.'})." + (f" https://doi.org/{paper.doi}" if paper.doi else "")


_FORMATTERS = {
    "bibtex": to_bibtex,
    "gb7714": to_gb7714,
    "apa": to_apa,
    "ieee": to_ieee,
    "mla": to_mla,
    "chicago": to_chicago,
}


def format_citation(paper: Paper, style: str) -> str:
    fn = _FORMATTERS.get(style.lower())
    if not fn:
        raise ValueError(f"Unknown citation style: {style}")
    return fn(paper)
