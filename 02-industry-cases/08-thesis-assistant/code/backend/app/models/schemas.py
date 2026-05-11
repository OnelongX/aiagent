"""Pydantic schemas — 前后端字段契约的唯一来源。"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# === 大纲生成 ===
class OutlineRequest(BaseModel):
    topic: str = Field(..., description="论文题目")
    discipline: str = Field(..., description="学科 · 如 'CS / 化学 / 经济学'")
    paper_type: Literal["实验型", "综述型", "工程型", "理论型"] = "实验型"
    target_words: int = Field(8000, description="目标字数")
    key_points: list[str] = Field(default_factory=list, description="关键论点")
    n_versions: int = Field(3, description="生成几套大纲")


class OutlineChapter(BaseModel):
    chapter: str
    words: int = 0
    subsections: list[str] = Field(default_factory=list)


class OutlineResponse(BaseModel):
    versions: list[list[OutlineChapter]]
    note: str = "请挑选最适合的一套大纲 · AI 生成的结构需要作者审阅修改"


# === 章节起草 ===
class SectionRequest(BaseModel):
    chapter: str
    key_points: list[str]
    target_words: int = 1000
    paper_type: str = "实验型"


class SectionResponse(BaseModel):
    draft: str
    placeholders: list[str] = Field(
        default_factory=list,
        description="[作者填入] 占位符列表 · 用户需亲自补",
    )
    ai_assist_marker: str = "[本节由 AI 协助起草,核心论证由作者完成]"


# === 学术润色 ===
class PolishRequest(BaseModel):
    text: str
    style: Literal["academic_zh", "academic_en"] = "academic_zh"


class PolishDiff(BaseModel):
    original: str
    polished: str
    reason: str = ""


class PolishResponse(BaseModel):
    diffs: list[PolishDiff]
    summary: str = ""


# === 文献检索 ===
class CitationSearchRequest(BaseModel):
    query: str
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    limit: int = 10


class Paper(BaseModel):
    title: str
    authors: list[str]
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    abstract: Optional[str] = None
    url: Optional[str] = None
    source: str = ""  # arxiv / crossref / openalex / semantic_scholar
    doi_verified: bool = False


class CitationSearchResponse(BaseModel):
    papers: list[Paper]
    total: int = 0


# === BibTeX 格式化 ===
class CitationFormatRequest(BaseModel):
    paper: Paper
    style: Literal["bibtex", "gb7714", "apa", "ieee", "mla", "chicago"] = "bibtex"


class CitationFormatResponse(BaseModel):
    formatted: str
    style: str


# === 相似度检测 ===
class DedupeRequest(BaseModel):
    text: str
    compare_against: list[str] = Field(
        default_factory=list,
        description="对比语料 · 比如用户自己之前写过的段落",
    )
    threshold: float = 0.85


class SimilarityHit(BaseModel):
    user_chunk: str
    similar_chunk: str
    similarity: float
    suggestion: str = "建议改写或加引用"


class DedupeResponse(BaseModel):
    issues: list[SimilarityHit]
    notice: str = (
        "本工具只做相似度提示 · 真实查重请用知网 / Turnitin / iThenticate · "
        "不能用于伪装抄袭"
    )


# === 答辩 Q&A ===
class DefenseRequest(BaseModel):
    thesis_abstract: str
    thesis_outline: list[str] = Field(default_factory=list)
    questions_per_persona: int = 3


class DefenseQuestion(BaseModel):
    persona: Literal["critic", "friendly", "outsider"]
    question: str
    hint: Optional[str] = None


class DefenseResponse(BaseModel):
    questions: list[DefenseQuestion]


# === 健康检查 ===
class HealthResponse(BaseModel):
    status: str
    components: dict[str, str]
