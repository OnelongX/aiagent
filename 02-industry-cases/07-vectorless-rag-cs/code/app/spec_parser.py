"""
Dedicated parser for solar/storage product spec sheets.
Extracts structured parameters, electrical specs, mechanical specs,
temperature coefficients, and packaging info from PV module datasheets.
"""

import json
import re
from pathlib import Path
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("CHATGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE") or None
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


def _ocr_extract_full_text(pdf_path: str) -> str:
    """Extract text from PDF using RapidOCR (for short docs with encoding issues)."""
    import fitz
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    doc = fitz.open(pdf_path)
    all_text = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        result, _ = ocr(img_bytes)
        lines = []
        if result:
            for line in result:
                lines.append(line[1])
        all_text.append("\n".join(lines))
    doc.close()
    return "\n\n---PAGE BREAK---\n\n".join(all_text)


def extract_full_text(pdf_path: str) -> str:
    """Extract all text from PDF. Uses OCR for short docs (≤10 pages) for reliability."""
    import fitz
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    doc.close()

    # Short docs: use OCR for best accuracy (avoids font encoding issues)
    if num_pages <= 10:
        try:
            text = _ocr_extract_full_text(pdf_path)
            if len(text.strip()) > 50:
                return text
        except Exception as e:
            print(f"  OCR extraction failed, falling back to PyMuPDF: {e}")

    # Long docs or OCR fallback: use PyMuPDF text extraction
    doc = fitz.open(pdf_path)
    all_text = []
    for page in doc:
        blocks = page.get_text("dict", sort=True)["blocks"]
        page_lines = []
        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    spans_text = " ".join(span["text"] for span in line["spans"])
                    if spans_text.strip():
                        page_lines.append(spans_text.strip())
        all_text.append("\n".join(page_lines))
    doc.close()
    return "\n\n---PAGE BREAK---\n\n".join(all_text)


def is_solar_storage_spec(text: str) -> bool:
    """Detect if document is a solar/storage/energy product spec sheet."""
    text_lower = text.lower()
    solar_keywords = [
        "pmpp", "voc", "isc", "vmpp", "impp", "bifacial", "monocrystalline",
        "polycrystalline", "topcon", "perc", "hjt", "solar", "module", "cell",
        "stc", "nmot", "noct", "irradiance", "pv",
        "组件", "光伏", "双面", "单晶", "多晶", "转换效率", "开路电压", "短路电流",
        "峰值功率", "衰减", "温度系数",
    ]
    storage_keywords = [
        "battery", "kwh", "inverter", "bms", "soc", "dod", "cycle",
        "储能", "电池", "逆变器", "充放电", "循环次数", "容量",
    ]
    device_keywords = [
        "mppt", "fuse", "breaker", "all-in-one", "ess", "charge controller",
        "一体机", "熔断器", "断路器", "控制器", "汇流箱", "配电",
    ]
    solar_hits = sum(1 for kw in solar_keywords if kw in text_lower)
    storage_hits = sum(1 for kw in storage_keywords if kw in text_lower)
    device_hits = sum(1 for kw in device_keywords if kw in text_lower)
    return solar_hits >= 3 or storage_hits >= 3 or device_hits >= 2


# Product type keyword definitions
_TYPE_KEYWORDS = {
    "aio": [  # 一体机 (All-in-One ESS)
        "all-in-one", "all in one", "ess", "energy storage system", "hybrid ess",
        "integrated", "一体机", "储能一体机", "一体式", "集成式储能",
    ],
    "mppt": [  # MPPT 控制器
        "charge controller", "solar controller", "mppt controller", "solar regulator",
        "充电控制器", "太阳能控制器", "mppt控制器",
    ],
    "fuse": [  # 熔断器/保护器件
        "fuse", "fuse link", "circuit breaker", "dc breaker", "surge protector",
        "spd", "disconnect", "combiner box",
        "熔断器", "熔丝", "断路器", "防雷器", "浪涌保护", "汇流箱", "隔离开关",
    ],
    "battery": [
        "battery", "kwh", "bms", "soc", "dod", "cycle life", "lifepo4",
        "charge current", "discharge current", "rate capacity",
        "储能电池", "充放电", "循环次数", "额定容量", "放电截止",
    ],
    "inverter": [
        "inverter", "ac output", "grid-tied", "hybrid inverter", "hybrid solar",
        "on-grid", "off-grid", "ac voltage", "grid frequency", "mppt",
        "rated ac", "ac output power", "european efficiency", "grid type",
        "逆变器", "并网", "离网", "交流输出",
    ],
    "solar": [
        "pmpp", "voc", "isc", "vmpp", "impp", "bifacial", "topcon",
        "perc", "hjt", "solar module", "光伏组件", "双面", "转换效率",
    ],
}


def _detect_product_type(text: str) -> str:
    """Detect product type from spec sheet text."""
    text_lower = text.lower()
    scores = {}
    for ptype, keywords in _TYPE_KEYWORDS.items():
        scores[ptype] = sum(1 for kw in keywords if kw in text_lower)

    # AIO: matches both battery+inverter strongly
    if scores["aio"] >= 2:
        return "aio"

    # Explicit title detection — highest priority
    first_500 = text_lower[:500]
    if "inverter" in first_500 and "battery" not in first_500[:100]:
        return "inverter"

    # If both inverter and battery score high, check which dominates
    # Inverters often mention "battery" in their specs (battery data section)
    if scores["inverter"] >= 3 and scores["battery"] >= 2:
        # If "inverter" appears in title/header area, it's an inverter
        if "inverter" in first_500:
            return "inverter"

    best = max(scores, key=scores.get)
    if scores[best] >= 2:
        return best
    return "solar"


_AIO_PROMPT_TEMPLATE = """你是光伏储能行业的技术专家。请从以下储能一体机（All-in-One ESS）产品规格书中提取所有结构化信息。

规格书原文：
{text}

请严格按以下 JSON 格式返回，尽可能完整提取：

{{
    "product_info": {{
        "manufacturer": "制造商名称",
        "series": "产品系列名",
        "model": "具体型号",
        "product_type": "储能一体机",
        "cell_type": "电芯类型（如：LiFePO4）",
        "power_range": "功率范围",
        "bifacial": false
    }},
    "inverter_specs": {{
        "inverter_type": "混合",
        "rated_power": "额定输出功率",
        "max_power": "最大输出功率",
        "max_dc_voltage": "最大直流输入电压",
        "mppt_voltage_range": "MPPT电压范围",
        "mppt_count": "MPPT路数",
        "strings_per_mppt": "每路MPPT组串数",
        "max_input_current": "最大输入电流",
        "max_short_circuit_current": null,
        "rated_ac_voltage": "额定交流输出电压",
        "ac_voltage_range": "交流电压范围",
        "rated_ac_current": "额定交流输出电流",
        "rated_frequency": "额定频率",
        "max_efficiency": "最大逆变效率",
        "euro_efficiency": "欧洲效率",
        "thd": null,
        "power_factor": null,
        "battery_voltage_range": null,
        "max_charge_current": null,
        "max_discharge_current": null
    }},
    "battery_specs": {{
        "rated_voltage": "额定电池电压（V）",
        "rated_energy": "额定能量（kWh）",
        "rated_capacity": "额定容量（Ah）",
        "cell_combination": "电芯组合",
        "cycle_life": "循环寿命",
        "max_charge_current": "最大充电电流（A）",
        "max_discharge_current": "最大放电电流（A）",
        "discharge_cutoff_voltage": "放电截止电压（V）",
        "charge_cutoff_voltage": "充电截止电压（V）",
        "charge_temp_range": "充电温度范围",
        "discharge_temp_range": "放电温度范围",
        "storage_temp_range": null,
        "ip_class": "防护等级",
        "max_parallel": "最大并联/扩展数量",
        "communication": "通信协议",
        "monitoring": "监控方式"
    }},
    "mechanical_specs": {{
        "dimensions": "长x宽x高 mm",
        "weight": "重量 kg",
        "case_material": "外壳材料",
        "case_type": "安装方式",
        "connector": null
    }},
    "warranty": {{
        "product_warranty": "产品质保年限",
        "power_warranty": "容量质保年限",
        "first_year_degradation": null,
        "annual_degradation": null
    }},
    "certifications": ["认证列表"],
    "key_features": ["核心特点/卖点列表，中文"],
    "summary_zh": "用中文写的2-3句产品概述"
}}

注意：
- 数值要带单位
- 一体机同时包含逆变器参数和电池参数，请分别填入 inverter_specs 和 battery_specs
- 如果某个字段在原文中找不到，设为 null
- 如果是英文规格书，key_features 和 summary_zh 用中文翻译"""

_MPPT_PROMPT_TEMPLATE = """你是光伏行业的技术专家。请从以下MPPT太阳能充电控制器产品规格书中提取所有结构化信息。

规格书原文：
{text}

请严格按以下 JSON 格式返回，尽可能完整提取：

{{
    "product_info": {{
        "manufacturer": "制造商名称",
        "series": "产品系列名",
        "model": "具体型号",
        "product_type": "MPPT控制器",
        "cell_type": null,
        "power_range": null,
        "bifacial": false
    }},
    "controller_specs": {{
        "rated_charge_current": "额定充电电流（A）",
        "max_pv_voltage": "最大PV输入电压（V）",
        "max_pv_power": "最大PV输入功率（W）",
        "battery_voltage": "电池电压（V），如12/24/48V自适应",
        "mppt_voltage_range": "MPPT电压范围",
        "mppt_count": "MPPT路数",
        "max_efficiency": "最大转换效率",
        "charge_stages": "充电阶段（如：三阶段）",
        "equalization_voltage": "均充电压",
        "float_voltage": "浮充电压",
        "low_voltage_disconnect": "低压断开电压",
        "self_consumption": "自耗电流",
        "operating_temp": "工作温度范围",
        "ip_class": "防护等级",
        "display": "显示屏类型",
        "communication": "通信接口"
    }},
    "mechanical_specs": {{
        "dimensions": "长x宽x高 mm",
        "weight": "重量 kg",
        "case_material": "外壳材料",
        "case_type": null,
        "connector": "端子类型"
    }},
    "certifications": ["认证列表"],
    "key_features": ["核心特点/卖点列表，中文"],
    "summary_zh": "用中文写的2-3句产品概述"
}}

注意：
- 数值要带单位
- 如果某个字段在原文中找不到，设为 null
- 如果是英文规格书，key_features 和 summary_zh 用中文翻译"""

_FUSE_PROMPT_TEMPLATE = """你是光伏行业的技术专家。请从以下光伏保护器件（熔断器/断路器/浪涌保护器/汇流箱）产品规格书中提取所有结构化信息。

规格书原文：
{text}

请严格按以下 JSON 格式返回，尽可能完整提取：

{{
    "product_info": {{
        "manufacturer": "制造商名称",
        "series": "产品系列名",
        "model": "具体型号",
        "product_type": "保护器件类型（如：光伏熔断器/直流断路器/浪涌保护器/汇流箱）",
        "cell_type": null,
        "power_range": null,
        "bifacial": false
    }},
    "protection_specs": {{
        "device_type": "器件类型",
        "rated_voltage": "额定电压（V DC/AC）",
        "max_voltage": "最大电压",
        "rated_current": "额定电流（A）",
        "breaking_capacity": "分断能力（kA）",
        "current_ratings": "可选电流规格列表",
        "response_time": "响应时间",
        "i2t_value": "I²t值（熔断器）",
        "arc_voltage": "电弧电压",
        "poles": "极数",
        "tripping_curve": "脱扣曲线（断路器）",
        "protection_level": "保护等级（SPD）",
        "max_discharge_current": "最大放电电流（SPD）",
        "nominal_discharge_current": "标称放电电流（SPD）",
        "ip_class": "防护等级",
        "operating_temp": "工作温度范围",
        "mounting": "安装方式（如：DIN导轨）",
        "strings_count": "组串数（汇流箱）",
        "max_input_current_per_string": "每串最大输入电流（汇流箱）"
    }},
    "mechanical_specs": {{
        "dimensions": "长x宽x高 mm",
        "weight": "重量 kg",
        "case_material": "外壳材料",
        "case_type": null,
        "connector": "接线方式"
    }},
    "certifications": ["认证列表"],
    "key_features": ["核心特点/卖点列表，中文"],
    "summary_zh": "用中文写的2-3句产品概述"
}}

注意：
- 数值要带单位
- 如果某个字段在原文中找不到，设为 null
- 如果有多个型号/规格，列出主要型号的参数
- 如果是英文规格书，key_features 和 summary_zh 用中文翻译"""

_BATTERY_PROMPT_TEMPLATE = """你是储能行业的技术专家。请从以下储能电池产品规格书中提取所有技术参数。

规格书原文：
{text}

请严格按以下 JSON 格式返回：

{{
    "product_info": {{
        "manufacturer": "制造商",
        "series": "系列名",
        "model": "所有型号，用/分隔",
        "product_type": "储能电池",
        "cell_type": "电芯类型（如：LiFePO4）"
    }},
    "spec_table": {{
        "models": ["型号1", "型号2"],
        "categories": [
            {{
                "category": "分类名称（如：电气参数、机械参数、环境参数、安全认证等）",
                "params": [
                    {{
                        "name": "参数名（中文）",
                        "name_en": "参数名（英文原文）",
                        "values": ["型号1的值", "型号2的值"],
                        "common_value": "如果所有型号值相同，填在这里，values 留空数组"
                    }}
                ]
            }}
        ]
    }},
    "certifications": ["认证列表"],
    "key_features": ["核心特点/卖点列表，中文"],
    "summary_zh": "用中文写的2-3句产品概述"
}}

重要规则：
- spec_table 中必须包含规格书里的【所有参数】，逐行提取，不要遗漏任何一行
- 如果只有一个型号，models 只有一个元素，values 也只有一个元素
- 如果某参数所有型号值相同，用 common_value 填写，values 留空数组 []
- 如果某参数各型号不同，values 数组按 models 顺序填写每个型号的值，common_value 留 null
- 数值要带单位
- 参数名 name 用中文，name_en 保留英文原文
- 如果是英文规格书，key_features 和 summary_zh 用中文"""

_INVERTER_PROMPT_TEMPLATE = """你是光伏和储能行业的技术专家。请从以下逆变器产品规格书中提取所有技术参数。

规格书原文：
{text}

请严格按以下 JSON 格式返回：

{{
    "product_info": {{
        "manufacturer": "制造商",
        "series": "系列名",
        "model": "所有型号，用/分隔",
        "product_type": "逆变器",
        "power_range": "功率范围"
    }},
    "spec_table": {{
        "models": ["型号1", "型号2", "型号3"],
        "categories": [
            {{
                "category": "分类名称（如：直流输入、交流输入/输出、效率、保护功能、电池数据、通用数据、备用数据、认证等）",
                "params": [
                    {{
                        "name": "参数名（中文）",
                        "name_en": "参数名（英文原文）",
                        "values": ["型号1的值", "型号2的值", "型号3的值"],
                        "common_value": "如果所有型号值相同，填在这里，values 留空数组"
                    }}
                ]
            }}
        ]
    }},
    "certifications": ["认证列表"],
    "key_features": ["核心特点/卖点列表，中文"],
    "summary_zh": "用中文写的2-3句产品概述"
}}

重要规则：
- spec_table 中必须包含规格书里的【所有参数】，逐行提取，不要遗漏任何一行
- 如果某参数所有型号值相同，用 common_value 填写，values 留空数组 []
- 如果某参数各型号不同，values 数组按 models 顺序填写每个型号的值，common_value 留 null
- 如果某型号没有该参数的值，对应位置填 "-"
- 数值要带单位
- 参数名 name 用中文，name_en 保留英文原文
- 如果是英文规格书，key_features 和 summary_zh 用中文"""

_SOLAR_PROMPT_TEMPLATE = """你是光伏行业的技术专家。请从以下光伏产品规格书中提取所有结构化信息。

规格书原文：
{text}

请严格按以下 JSON 格式返回，尽可能完整提取：

{{
    "product_info": {{
        "manufacturer": "制造商名称",
        "series": "产品系列名",
        "model": "具体型号",
        "product_type": "产品类型（如：光伏组件/逆变器）",
        "cell_type": "电池技术类型（如：TOPCon/PERC/HJT/单晶/多晶）",
        "power_range": "功率范围（如：630~650W）",
        "bifacial": true或false
    }},
    "electrical_specs_stc": [
        {{"model": "型号", "pmpp": "额定功率W", "vmpp": "最大功率电压V", "impp": "最大功率电流A", "voc": "开路电压V", "isc": "短路电流A", "efficiency": "效率%"}}
    ],
    "electrical_specs_nmot": [
        {{"model": "型号", "pmpp": "W", "vmpp": "V", "impp": "A", "voc": "V", "isc": "A"}}
    ],
    "bifacial_specs": [
        {{"gain_percent": "增益百分比", "pmpp": "W", "vmpp": "V", "impp": "A", "voc": "V", "isc": "A"}}
    ],
    "temperature_coefficients": {{
        "pmpp": "如 -0.29%/℃",
        "voc": "如 -0.25%/℃",
        "isc": "如 +0.043%/℃"
    }},
    "mechanical_specs": {{
        "dimensions": "长x宽x高 mm",
        "weight": "重量 kg",
        "cell_count": "电池片数量",
        "glass": "玻璃规格",
        "frame": "边框类型",
        "junction_box_ip": "IP等级",
        "cable_length": "电缆长度",
        "cable_size": "电缆截面积",
        "connector": "连接器类型"
    }},
    "operating_params": {{
        "max_system_voltage": "最大系统电压",
        "max_fuse_rating": "最大保险丝额定值",
        "nmot": "标称工作温度",
        "operating_temp": "工作温度范围",
        "max_load_front": "正面最大载荷",
        "max_load_rear": "背面最大载荷"
    }},
    "warranty": {{
        "product_warranty": "产品质保年限",
        "power_warranty": "功率质保年限",
        "first_year_degradation": "首年衰减",
        "annual_degradation": "历年衰减"
    }},
    "packaging": {{
        "pieces_per_pallet": "每托数量",
        "pallet_weight": "单托重量",
        "container_qty": "装柜数量"
    }},
    "certifications": ["认证列表"],
    "key_features": ["核心特点/卖点列表，中文"],
    "summary_zh": "用中文写的2-3句产品概述"
}}

注意：
- 数值要带单位
- 如果某个字段在原文中找不到，设为 null
- electrical_specs_stc 应包含所有功率档位的数据
- 如果是中文规格书直接提取，英文规格书翻译后提取"""


def parse_spec_sheet(pdf_path: str, model: str = "gpt-4o-mini") -> dict:
    """
    Parse a solar/storage spec sheet PDF into structured data.
    Returns comprehensive product information.
    """
    full_text = extract_full_text(pdf_path)

    if not is_solar_storage_spec(full_text):
        return {}  # Not a solar/storage spec

    product_type = _detect_product_type(full_text)
    print(f"  Detected {product_type} spec sheet, performing deep extraction...")

    templates = {
        "aio": _AIO_PROMPT_TEMPLATE,
        "battery": _BATTERY_PROMPT_TEMPLATE,
        "inverter": _INVERTER_PROMPT_TEMPLATE,
        "mppt": _MPPT_PROMPT_TEMPLATE,
        "fuse": _FUSE_PROMPT_TEMPLATE,
        "solar": _SOLAR_PROMPT_TEMPLATE,
    }
    prompt = templates.get(product_type, _SOLAR_PROMPT_TEMPLATE).format(text=full_text[:6000])

    try:
        resp = _get_client().chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content)
        result["_source"] = "spec_parser"
        result["_text_length"] = len(full_text)
        return result
    except Exception as e:
        print(f"  Spec sheet parsing failed: {e}")
        return {}


def format_spec_for_retrieval(spec_data: dict) -> str:
    """Format parsed spec data into searchable text for the index."""
    if not spec_data:
        return ""

    parts = []

    # Product info
    pi = spec_data.get("product_info", {})
    if pi:
        parts.append(f"产品：{pi.get('manufacturer', '')} {pi.get('series', '')} {pi.get('model', '')}")
        parts.append(f"类型：{pi.get('product_type', '')}，技术：{pi.get('cell_type', '')}")
        parts.append(f"功率范围：{pi.get('power_range', '')}")
        if pi.get("bifacial"):
            parts.append("双面组件")

    # Summary
    if spec_data.get("summary_zh"):
        parts.append(f"\n概述：{spec_data['summary_zh']}")

    # Key features
    features = spec_data.get("key_features", [])
    if features:
        parts.append("\n核心特点：")
        for f in features:
            parts.append(f"  - {f}")

    # Universal spec_table format
    st = spec_data.get("spec_table", {})
    if st and st.get("categories"):
        models = st.get("models", [])
        for cat in st["categories"]:
            parts.append(f"\n{cat.get('category', '')}：")
            for p in cat.get("params", []):
                name = p.get("name", "")
                if p.get("common_value"):
                    parts.append(f"  {name}：{p['common_value']}")
                elif p.get("values"):
                    for i, v in enumerate(p["values"]):
                        m = models[i] if i < len(models) else ""
                        parts.append(f"  {name}（{m}）：{v}")

    # Battery specs (multi-model)
    bs_list = spec_data.get("battery_specs_list", [])
    bs = spec_data.get("battery_specs", {})
    if bs_list:
        parts.append("\n电池型号参数：")
        for item in bs_list:
            model = item.get("model", "")
            parts.append(f"\n  【{model}】")
            for k, v in item.items():
                if k != "model" and v:
                    parts.append(f"    {k}：{v}")
    if bs and any(v for v in bs.values() if v and k != "注意"):
        parts.append("\n电池共有参数：")
        for key, val in bs.items():
            if val and key != "注意":
                parts.append(f"  {key}：{val}")

    # Controller specs (MPPT)
    ctrl = spec_data.get("controller_specs", {})
    if ctrl and any(v for v in ctrl.values() if v):
        parts.append("\nMPPT控制器参数：")
        ctrl_labels = {
            "rated_charge_current": "额定充电电流", "max_pv_voltage": "最大PV输入电压",
            "max_pv_power": "最大PV输入功率", "battery_voltage": "电池电压",
            "mppt_voltage_range": "MPPT电压范围", "mppt_count": "MPPT路数",
            "max_efficiency": "最大效率", "charge_stages": "充电阶段",
            "equalization_voltage": "均充电压", "float_voltage": "浮充电压",
            "self_consumption": "自耗电流", "ip_class": "防护等级",
            "communication": "通信接口",
        }
        for key, label in ctrl_labels.items():
            val = ctrl.get(key)
            if val:
                parts.append(f"  {label}：{val}")

    # Protection specs (fuse/breaker/SPD)
    prot = spec_data.get("protection_specs", {})
    if prot and any(v for v in prot.values() if v):
        parts.append("\n保护器件参数：")
        prot_labels = {
            "device_type": "器件类型", "rated_voltage": "额定电压",
            "max_voltage": "最大电压", "rated_current": "额定电流",
            "breaking_capacity": "分断能力", "current_ratings": "电流规格",
            "response_time": "响应时间", "poles": "极数",
            "tripping_curve": "脱扣曲线", "protection_level": "保护等级",
            "max_discharge_current": "最大放电电流", "ip_class": "防护等级",
            "mounting": "安装方式", "strings_count": "组串数",
        }
        for key, label in prot_labels.items():
            val = prot.get(key)
            if val:
                parts.append(f"  {label}：{val}")

    # Inverter specs (multi-model)
    inv_list = spec_data.get("inverter_specs_list", [])
    inv = spec_data.get("inverter_specs", {})
    if inv_list:
        parts.append("\n逆变器型号参数：")
        for item in inv_list:
            model = item.get("model", "")
            parts.append(f"\n  【{model}】")
            for k, v in item.items():
                if k != "model" and v:
                    parts.append(f"    {k}：{v}")
    if inv and any(v for v in inv.values() if v and k != "注意"):
        parts.append("\n逆变器共有参数：")
        for key, val in inv.items():
            if val and key != "注意":
                parts.append(f"  {key}：{val}")

    # Backup specs
    backup = spec_data.get("backup_specs", {})
    if backup and any(v for v in backup.values() if v):
        parts.append("\n备用/离网参数：")
        for key, val in backup.items():
            if val:
                parts.append(f"  {key}：{val}")

    # STC specs (solar)
    stc = spec_data.get("electrical_specs_stc", [])
    if stc:
        parts.append("\nSTC 电气参数：")
        for s in stc:
            parts.append(f"  {s.get('model', '')}: Pmpp={s.get('pmpp', '')} Vmpp={s.get('vmpp', '')} Impp={s.get('impp', '')} Voc={s.get('voc', '')} Isc={s.get('isc', '')} η={s.get('efficiency', '')}")

    # Temperature coefficients
    tc = spec_data.get("temperature_coefficients", {})
    if tc and any(tc.values()):
        parts.append(f"\n温度系数：Pmpp={tc.get('pmpp', '')} Voc={tc.get('voc', '')} Isc={tc.get('isc', '')}")

    # Mechanical
    ms = spec_data.get("mechanical_specs", {})
    if ms:
        parts.append(f"\n机械参数：尺寸={ms.get('dimensions', '')} 重量={ms.get('weight', '')} 电池片={ms.get('cell_count', '')}")

    # Warranty
    w = spec_data.get("warranty", {})
    if w:
        parts.append(f"\n质保：产品={w.get('product_warranty', '')} 功率={w.get('power_warranty', '')} 首年衰减={w.get('first_year_degradation', '')} 历年衰减={w.get('annual_degradation', '')}")

    return "\n".join(parts)
