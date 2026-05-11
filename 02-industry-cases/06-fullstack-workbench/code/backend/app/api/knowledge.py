"""Knowledge API — 文档 ingest + 查询。"""

from fastapi import APIRouter
from app.models.schemas import IngestRequest
from app.services.rag import ingest_document, search_knowledge, list_documents

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/ingest")
async def ingest(req: IngestRequest):
    """Ingest 一篇文档。
    
    关键纪律:doc_id 在首次创建时生成 UUID,
    后续 rebuild / 改分类时复用,避免文档身份漂移。
    """
    doc_id = ingest_document(
        title=req.title,
        content=req.content,
        doc_id=req.doc_id,
        category=req.category,
    )
    return {"doc_id": doc_id, "status": "ingested"}


@router.get("/search")
async def search(q: str, top_k: int = 5):
    hits = search_knowledge(q, top_k=top_k)
    return {"hits": hits}


@router.get("/list")
async def list_all():
    return {"documents": list_documents()}
