// Manufacturing AI Assistant · frontend
const API = location.origin;

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.target).classList.add("active");
  });
});

async function call(path, body, outId) {
  const out = document.getElementById(outId);
  out.textContent = "⏳ 请求中...";
  try {
    const r = await fetch(API + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const txt = await r.text();
    try {
      out.textContent = JSON.stringify(JSON.parse(txt), null, 2);
    } catch {
      out.textContent = txt;
    }
  } catch (e) {
    out.textContent = "❌ 请求失败:" + e.message;
  }
}

function runMES() {
  call("/api/mes/qa", {
    question:       document.getElementById("mes-q").value,
    workshop_scope: document.getElementById("mes-ws").value,
  }, "mes-out");
}

function runProcess() {
  let params = {};
  try { params = JSON.parse(document.getElementById("pr-params").value); }
  catch (e) {
    document.getElementById("pr-out").textContent = "❌ 参数 JSON 解析失败:" + e.message;
    return;
  }
  call("/api/process/recommend", {
    line_code:      document.getElementById("pr-line").value,
    process_step:   document.getElementById("pr-step").value,
    target_yield:   +document.getElementById("pr-yield").value,
    current_params: params,
    issue_desc:     document.getElementById("pr-issue").value,
  }, "pr-out");
}

function runQC() {
  call("/api/qc/inspect", {
    line_code:     document.getElementById("qc-line").value,
    product_type:  document.getElementById("qc-prod").value,
    defect_obs:    document.getElementById("qc-obs").value,
    image_caption: document.getElementById("qc-img").value,
  }, "qc-out");
}

function runPdM() {
  call("/api/pdm/check", {
    line_code:          document.getElementById("pd-line").value,
    extra_observations: document.getElementById("pd-obs").value,
  }, "pd-out");
}

function runScheduling() {
  let orders = [];
  try { orders = JSON.parse(document.getElementById("sc-orders").value); }
  catch (e) {
    document.getElementById("sc-out").textContent = "❌ 订单 JSON 解析失败:" + e.message;
    return;
  }
  const lines = document.getElementById("sc-lines").value
    .split(/[,,]/).map((s) => s.trim()).filter(Boolean);
  call("/api/scheduling/plan", {
    orders, available_lines: lines,
    horizon_days: +document.getElementById("sc-days").value,
  }, "sc-out");
}

function runSOP() {
  call("/api/sop/qa", {
    question:  document.getElementById("sop-q").value,
    line_code: document.getElementById("sop-line").value || null,
  }, "sop-out");
}

function runPII() {
  call("/api/pii/redact", {
    text: document.getElementById("pii-in").value,
  }, "pii-out");
}
