"""用药审查 · 相互作用 + 剂量 + 特殊人群 · 接真实药品数据库"""

import logging
from fastapi import APIRouter

from app.models.schemas import (
    MedicationCheckRequest, MedicationCheckResponse, DrugIssue
)
from app.services.drug_db import lookup, batch_check_interactions
from app.services.doctor_block import (
    detect_commercial_drug, COMMERCIAL_DRUG_BLOCKLIST, ai_disclaimer
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/medication", tags=["medication"])


@router.post("/check", response_model=MedicationCheckResponse)
async def check(req: MedicationCheckRequest) -> MedicationCheckResponse:
    issues: list[DrugIssue] = []
    drugs_resolved = []

    # 1. 通用名/商品名识别
    for d in req.drugs:
        if d in COMMERCIAL_DRUG_BLOCKLIST:
            issues.append(DrugIssue(
                type="commercial_name",
                severity="low",
                drugs=[d],
                description=f"{d} 是商品名 · AI 不识别商品名",
                advice="请改用通用名(INN)输入,如 立普妥 → 阿托伐他汀",
            ))
            continue

        info = lookup(d)
        if info is None:
            drugs_resolved.append({"name": d, "status": "未在本数据库 · 请人工核对"})
            issues.append(DrugIssue(
                type="dose",
                severity="moderate",
                drugs=[d],
                description=f"{d} 不在本 demo 数据库中",
                advice="请药师查国家药典 / 国家药品监督管理局数据库",
            ))
            continue

        drugs_resolved.append({"name": d, **info})

        # 2. 特殊人群检查
        if req.pregnancy and info.get("pregnancy", "").startswith(("D", "X")):
            issues.append(DrugIssue(
                type="contraindication",
                severity="high",
                drugs=[d],
                description=f"{d} 妊娠分级 {info.get('pregnancy')} · 妊娠期禁用 / 慎用",
                advice="改用妊娠 B 级或更安全替代品 · 必须产科评估",
            ))
        if req.lactation and "禁用" in info.get("lactation", ""):
            issues.append(DrugIssue(
                type="contraindication",
                severity="high",
                drugs=[d],
                description=f"{d} 哺乳期禁用",
                advice="改用哺乳期可用替代品",
            ))
        if req.patient_age < 18 and ("禁用" in info.get("pediatric", "") or "未确立" in info.get("pediatric", "")):
            issues.append(DrugIssue(
                type="population",
                severity="moderate",
                drugs=[d],
                description=f"{d} 儿科信息:{info.get('pediatric')}",
                advice="儿科医师评估剂量 · 必要时换用儿科可用药",
            ))
        if req.renal_function in ("moderate", "severe") and info.get("renal"):
            issues.append(DrugIssue(
                type="dose",
                severity="moderate",
                drugs=[d],
                description=f"{d} 肾功能相关:{info.get('renal')}",
                advice="按肌酐清除率调整剂量",
            ))
        if req.hepatic_function in ("moderate", "severe") and info.get("hepatic"):
            issues.append(DrugIssue(
                type="dose",
                severity="moderate",
                drugs=[d],
                description=f"{d} 肝功能相关:{info.get('hepatic')}",
                advice="肝功能不全减量",
            ))
        for allergy in req.allergies:
            if allergy.lower() in (info.get("category") or "").lower():
                issues.append(DrugIssue(
                    type="contraindication",
                    severity="high",
                    drugs=[d],
                    description=f"患者过敏:{allergy} · {d} 属同类",
                    advice="禁用 · 换用非交叉过敏类药",
                ))

    # 3. 相互作用(两两组合)
    valid_drugs = [d for d in req.drugs if lookup(d) is not None]
    interactions = batch_check_interactions(valid_drugs)
    for inter in interactions:
        issues.append(DrugIssue(
            type="interaction",
            severity=inter["severity"],
            drugs=[inter["drug_a"], inter["drug_b"]],
            description=f"{inter['drug_a']} + {inter['drug_b']}:{inter['mechanism']}",
            advice=inter["advice"],
        ))

    # 4. 整体严重度
    sev_rank = {"high": 3, "moderate": 2, "low": 1}
    overall = "none"
    if issues:
        worst = max(sev_rank[i.severity] for i in issues)
        overall = {3: "high", 2: "moderate", 1: "low"}[worst]

    return MedicationCheckResponse(
        drugs_resolved=drugs_resolved,
        interactions=interactions,
        issues=issues,
        overall_severity=overall,
        must_pharmacist_review=True,
        disclaimer=ai_disclaimer("用药审查仅参考 · 处方最终以执业医师 / 药师为准"),
    )
