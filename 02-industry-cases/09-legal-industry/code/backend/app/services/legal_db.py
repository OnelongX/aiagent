"""法条 / 判例数据库接入。

⚠️ 关键纪律:任何法条引用必须通过这里验真,绝不让 LLM 编。

实际生产接入(本仓库提供接口约定 + mock 实现):
- 国家法律法规数据库 https://flk.npc.gov.cn/(免费 · 限速)
- 北大法宝(付费 API)
- 威科先行(付费 API)
- 裁判文书网(免费 · 限速 · 需爬取)
"""

import httpx
from typing import Optional
from app.models.schemas import LegalArticle, JudicialCase


HTTP_TIMEOUT = httpx.Timeout(15.0)


# ============ 法条验真 ============
async def verify_article(statute: str, article_number: str) -> Optional[LegalArticle]:
    """验证一条法条是否真实存在。

    生产接入:调国家法律法规数据库 / 北大法宝。
    本 demo 用 mock(返回固定几条常用法条以便测试)。
    """
    # === Mock 数据(生产环境替换为真 API)===
    mock_db = {
        ("民法典", "第 675 条"): LegalArticle(
            statute="中华人民共和国民法典",
            article_number="第 675 条",
            text="借款人应当按照约定的期限返还借款。",
            effective_date="2021-01-01",
            verified=True,
        ),
        ("民法典", "第 676 条"): LegalArticle(
            statute="中华人民共和国民法典",
            article_number="第 676 条",
            text="借款人未按照约定的期限返还借款的,应当按照约定或者国家有关规定支付逾期利息。",
            effective_date="2021-01-01",
            verified=True,
        ),
        ("劳动合同法", "第 39 条"): LegalArticle(
            statute="中华人民共和国劳动合同法",
            article_number="第 39 条",
            text="劳动者有下列情形之一的,用人单位可以解除劳动合同 ...",
            effective_date="2013-07-01",
            verified=True,
        ),
    }

    key = (statute.replace("中华人民共和国", "").strip(), article_number.strip())
    if key in mock_db:
        return mock_db[key]

    # 真实接入示例(伪代码):
    # async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
    #     r = await client.get("https://flk.npc.gov.cn/api/...",
    #                          params={"statute": statute, "article": article_number})
    #     if r.status_code == 200 and r.json().get("found"):
    #         return LegalArticle(..., verified=True)

    # 未找到 → 返回 None(不验真)
    return None


async def search_articles(keywords: list[str], jurisdiction: str = "中国大陆") -> list[LegalArticle]:
    """按关键词搜索相关法条。

    生产环境接入:北大法宝全文检索。
    本 demo 返回与关键词相关的 mock 数据。
    """
    # Mock:基于简单关键词匹配
    all_mock = [
        ("民法典", "第 675 条"),
        ("民法典", "第 676 条"),
        ("劳动合同法", "第 39 条"),
    ]

    results = []
    for statute, art_num in all_mock:
        article = await verify_article(statute, art_num)
        if article:
            results.append(article)
    return results


# ============ 判例检索 ============
async def search_cases(
    keywords: list[str],
    claim_type: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    limit: int = 10,
) -> list[JudicialCase]:
    """判例检索。

    生产环境:接裁判文书网 / 北大法宝 / 威科先行。
    本 demo 返回 mock 数据(实际生产必须接真实数据库)。
    """
    # === Mock 判例 ===
    mock_cases = [
        JudicialCase(
            case_number="(2023) 京 01 民终 1234 号",
            title="张某诉李某民间借贷纠纷一案",
            court="北京市第一中级人民法院",
            court_level="中院",
            judgment_date="2023-08-15",
            claim_type="民间借贷",
            summary="(本案系 mock 数据 · 生产环境请接真实判例库)",
            url="https://wenshu.court.gov.cn/...(mock)",
            source="mock",
        ),
        JudicialCase(
            case_number="(2022) 沪 0115 民初 5678 号",
            title="(脱敏案例 · mock)",
            court="上海市浦东新区人民法院",
            court_level="基层",
            judgment_date="2022-11-20",
            claim_type="民间借贷",
            summary="(mock 数据)",
            source="mock",
        ),
    ]

    return mock_cases[:limit]


# ============ 法规追踪 ============
async def fetch_recent_regulations(days: int = 7) -> list[dict]:
    """获取最近 N 天的新法规。

    生产接入:
    - 国家法律法规数据库 RSS
    - 证监会 / 银保监会 / 税务总局 公告
    - 国务院政策文件库
    """
    # Mock(生产环境替换)
    return [
        {
            "title": "(示例)《XX 行业数据安全合规指引(2026)》",
            "source": "国家网信办",
            "publish_date": "2026-03-15",
            "effective_date": "2026-07-01",
            "source_url": "https://www.cac.gov.cn/...(mock)",
            "affected_industries": ["互联网", "数据服务", "云计算"],
            "summary": "(本预警为 mock 数据 · 实际接入需要订阅官方 RSS / 公告。)",
        }
    ]
