"""文献检索 · POST /api/cite/search + /api/cite/format

关键纪律:
- 文献必须来自真实学术 API
- DOI 必须 Crossref 验真
- LLM 不参与文献内容生成(只参与 query 改写,可选)
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    CitationSearchRequest, CitationSearchResponse,
    CitationFormatRequest, CitationFormatResponse,
)
from app.services.academic_api import search_papers, crossref_verify_doi
from app.services.citation import format_citation

router = APIRouter(prefix="/api/cite", tags=["citation"])


@router.post("/search", response_model=CitationSearchResponse)
async def search(req: CitationSearchRequest):
    """搜索真实文献 · arXiv + Crossref + OpenAlex 多源融合 · 自动 DOI 校验"""
    papers = await search_papers(
        query=req.query,
        year_from=req.year_from,
        year_to=req.year_to,
        limit=req.limit,
    )
    return CitationSearchResponse(papers=papers, total=len(papers))


@router.post("/format", response_model=CitationFormatResponse)
async def format(req: CitationFormatRequest):
    """格式化引用 · 6 种格式 · 不让 LLM 做"""
    if not req.paper.doi and not req.paper.arxiv_id:
        raise HTTPException(
            status_code=400,
            detail="paper 必须含 DOI 或 arxiv_id 才能格式化为正式引用",
        )

    # 如果有 DOI,二次校验
    if req.paper.doi and not req.paper.doi_verified:
        verified = await crossref_verify_doi(req.paper.doi)
        if not verified:
            raise HTTPException(
                status_code=400,
                detail=f"DOI {req.paper.doi} 未通过 Crossref 校验,拒绝格式化",
            )

    formatted = format_citation(req.paper, req.style)
    return CitationFormatResponse(formatted=formatted, style=req.style)
