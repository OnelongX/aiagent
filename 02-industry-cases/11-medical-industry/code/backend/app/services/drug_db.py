"""药品数据库 mock · 用药审查关键

生产环境替换为:
- 国家药品监督管理局药品数据库
- Drugs.com / Lexicomp / Micromedex
- 国家基本药物目录 + 医保目录

本 mock 用 15 个常见药 + 6 对典型相互作用,
覆盖文章中所有示例,可直接 docker 跑通。
"""

# 通用名 → 基础属性
DRUG_INFO = {
    "阿司匹林": {
        "category":     "抗血小板 / 解热镇痛",
        "dose_range":   "75-325mg/d(抗血小板)",
        "pregnancy":    "D(妊娠晚期禁用)",
        "lactation":    "慎用(可分泌入乳)",
        "pediatric":    "16 岁以下慎用(瑞氏综合征风险)",
        "renal":        "eGFR<30 慎用",
        "key_warnings": ["消化道出血", "哮喘加重", "瑞氏综合征"],
    },
    "氯吡格雷": {
        "category":     "抗血小板",
        "dose_range":   "75mg qd",
        "pregnancy":    "B",
        "lactation":    "慎用",
        "pediatric":    "18 岁以下安全性未确立",
        "key_warnings": ["与质子泵抑制剂相互作用", "出血风险"],
    },
    "华法林": {
        "category":     "抗凝",
        "dose_range":   "起始 2.5-5mg/d · 依据 INR 调整",
        "pregnancy":    "X(致畸 · 禁用)",
        "lactation":    "可用",
        "pediatric":    "需专科评估",
        "key_warnings": ["治疗窗窄", "出血", "与多药 / 食物相互作用"],
    },
    "阿托伐他汀": {
        "category":     "他汀",
        "dose_range":   "10-80mg qn",
        "pregnancy":    "X(禁用)",
        "lactation":    "禁用",
        "pediatric":    "10 岁以上可用(家族性高胆固醇)",
        "renal":        "无需调整",
        "key_warnings": ["肌病 / 横纹肌溶解", "肝酶升高"],
    },
    "二甲双胍": {
        "category":     "口服降糖",
        "dose_range":   "500-2000mg/d",
        "pregnancy":    "B",
        "lactation":    "慎用",
        "pediatric":    "10 岁以上可用",
        "renal":        "eGFR<30 禁用",
        "key_warnings": ["乳酸酸中毒", "胃肠道反应"],
    },
    "胰岛素": {
        "category":     "注射降糖",
        "dose_range":   "个体化 · 0.4-1.0 U/kg/d",
        "pregnancy":    "B(妊娠首选)",
        "lactation":    "可用",
        "pediatric":    "可用",
        "key_warnings": ["低血糖", "局部脂肪萎缩"],
    },
    "氨氯地平": {
        "category":     "钙通道阻滞剂",
        "dose_range":   "5-10mg qd",
        "pregnancy":    "C",
        "lactation":    "慎用",
        "renal":        "无需调整",
        "key_warnings": ["踝部水肿", "面红"],
    },
    "缬沙坦": {
        "category":     "ARB",
        "dose_range":   "80-320mg qd",
        "pregnancy":    "D(中晚期禁用)",
        "lactation":    "慎用",
        "renal":        "eGFR<30 慎用",
        "key_warnings": ["高钾", "肾损伤", "妊娠致畸"],
    },
    "美托洛尔": {
        "category":     "β-阻滞剂",
        "dose_range":   "25-200mg/d",
        "pregnancy":    "C",
        "lactation":    "慎用",
        "key_warnings": ["哮喘禁用", "心动过缓", "突然停药反跳"],
    },
    "奥美拉唑": {
        "category":     "质子泵抑制剂",
        "dose_range":   "20-40mg qd",
        "pregnancy":    "C",
        "lactation":    "慎用",
        "key_warnings": ["与氯吡格雷相互作用", "长期使用骨折风险"],
    },
    "头孢曲松": {
        "category":     "三代头孢",
        "dose_range":   "1-2g qd IM/IV",
        "pregnancy":    "B",
        "lactation":    "可用",
        "pediatric":    "可用 · 新生儿慎用",
        "key_warnings": ["青霉素过敏交叉", "与钙剂禁配伍(新生儿)"],
    },
    "阿莫西林": {
        "category":     "青霉素类",
        "dose_range":   "0.25-1g tid",
        "pregnancy":    "B",
        "lactation":    "可用",
        "pediatric":    "可用",
        "key_warnings": ["青霉素过敏禁用", "皮疹"],
    },
    "布洛芬": {
        "category":     "NSAIDs",
        "dose_range":   "200-400mg q6h(成人)",
        "pregnancy":    "C(妊娠晚期 D · 禁用)",
        "lactation":    "可用(短期)",
        "pediatric":    "6 月以上可用 · 5-10mg/kg",
        "renal":        "eGFR<30 慎用",
        "key_warnings": ["消化道出血", "肾损伤", "心血管事件"],
    },
    "对乙酰氨基酚": {
        "category":     "解热镇痛",
        "dose_range":   "成人 500mg q4-6h · 单日不超 4g",
        "pregnancy":    "B(首选)",
        "lactation":    "可用",
        "pediatric":    "可用 · 10-15mg/kg",
        "hepatic":      "肝功能不全减量",
        "key_warnings": ["肝毒性(过量 / 饮酒)"],
    },
    "地高辛": {
        "category":     "强心苷",
        "dose_range":   "0.125-0.25mg qd",
        "pregnancy":    "C",
        "lactation":    "可用",
        "renal":        "eGFR<30 减量",
        "key_warnings": ["治疗窗极窄", "低钾增敏", "中毒"],
    },
}


# 典型相互作用(双向)· 严重程度:high / moderate / low
INTERACTIONS = {
    frozenset(["华法林", "阿司匹林"]): {
        "severity":  "high",
        "mechanism": "出血风险叠加 · 抗凝 + 抗血小板",
        "advice":    "原则上避免合用 · 必须合用时监测 INR + 消化道保护",
    },
    frozenset(["华法林", "布洛芬"]): {
        "severity":  "high",
        "mechanism": "NSAIDs 增强华法林作用 · 消化道出血风险",
        "advice":    "避免合用 · 替换为对乙酰氨基酚",
    },
    frozenset(["氯吡格雷", "奥美拉唑"]): {
        "severity":  "moderate",
        "mechanism": "奥美拉唑抑制 CYP2C19 · 减弱氯吡格雷活化",
        "advice":    "改用泮托拉唑或雷尼替丁",
    },
    frozenset(["地高辛", "胺碘酮"]): {
        "severity":  "high",
        "mechanism": "胺碘酮升高地高辛血药浓度 · 中毒风险",
        "advice":    "地高辛减量 50% · 监测血药浓度",
    },
    frozenset(["阿托伐他汀", "克拉霉素"]): {
        "severity":  "high",
        "mechanism": "CYP3A4 抑制 · 他汀血药浓度升高 · 横纹肌溶解风险",
        "advice":    "暂停他汀或改用瑞舒伐他汀",
    },
    frozenset(["二甲双胍", "造影剂"]): {
        "severity":  "high",
        "mechanism": "造影剂 + 二甲双胍 · 急性肾损伤 + 乳酸酸中毒",
        "advice":    "造影前 48h 停二甲双胍 · 复查肾功后再用",
    },
}


def lookup(drug_name: str) -> dict | None:
    """查通用名"""
    return DRUG_INFO.get(drug_name)


def check_interaction(drug_a: str, drug_b: str) -> dict | None:
    """查相互作用"""
    return INTERACTIONS.get(frozenset([drug_a, drug_b]))


def batch_check_interactions(drugs: list[str]) -> list[dict]:
    """两两组合检查"""
    results = []
    for i in range(len(drugs)):
        for j in range(i + 1, len(drugs)):
            inter = check_interaction(drugs[i], drugs[j])
            if inter:
                results.append({
                    "drug_a": drugs[i],
                    "drug_b": drugs[j],
                    **inter,
                })
    return results
