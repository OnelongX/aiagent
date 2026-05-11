"""答辩 Q&A 模拟 · POST /api/defense · 3 persona"""

from fastapi import APIRouter
from app.models.schemas import DefenseRequest, DefenseResponse, DefenseQuestion
from app.services.llm import chat_json

router = APIRouter(prefix="/api", tags=["defense"])


PERSONAS = {
    "critic": {
        "name": "严厉派",
        "prompt": """你扮演一个严厉的答辩委员。看完论文后,
针对方法漏洞、实验设计不足、对照实验缺失、统计意义不显著等
角度提出 N 个尖锐问题。
不要友好,要挑刺。""",
    },
    "friendly": {
        "name": "友好派",
        "prompt": """你扮演一个友好的答辩委员。看完论文后,
针对扩展应用、未来工作、其他可能性等
角度提出 N 个建设性问题。
不要挑刺,而是好奇式提问。""",
    },
    "outsider": {
        "name": "跨学科派",
        "prompt": """你扮演来自其他学科的答辩委员(比如统计学家看 CS 论文)。
针对方法 generalizability、跨学科可比性、术语跨界含义等
角度提出 N 个挑战 generalizability 的问题。""",
    },
}


SYSTEM_TEMPLATE = """{persona_prompt}

严格 JSON 输出:
{{
  "questions": [
    {{"question": "问题正文", "hint": "提示作者怎么思考(可选)"}}
  ]
}}"""


@router.post("/defense", response_model=DefenseResponse)
async def simulate_defense(req: DefenseRequest):
    user = f"""论文摘要:
{req.thesis_abstract}

论文大纲:
{chr(10).join('- ' + s for s in req.thesis_outline) if req.thesis_outline else '(未提供)'}

请提出 {req.questions_per_persona} 个问题。"""

    all_questions = []
    for persona_key, persona_info in PERSONAS.items():
        system = SYSTEM_TEMPLATE.format(persona_prompt=persona_info["prompt"])
        data = chat_json(system, user, temperature=0.85, max_tokens=2000)
        for q in data.get("questions", [])[: req.questions_per_persona]:
            all_questions.append(DefenseQuestion(
                persona=persona_key,
                question=q.get("question", ""),
                hint=q.get("hint"),
            ))

    return DefenseResponse(questions=all_questions)
