// Finance AI Assistant · frontend
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

function runKYC() {
  call("/api/kyc/review", {
    customer_name:   document.getElementById("kyc-name").value,
    id_card:         document.getElementById("kyc-id").value,
    occupation:      document.getElementById("kyc-occupation").value,
    income_yearly:   +document.getElementById("kyc-income").value,
    source_of_fund:  document.getElementById("kyc-fund").value,
    purpose:         document.getElementById("kyc-purpose").value,
    pep_self_report: document.getElementById("kyc-pep").checked,
  }, "kyc-out");
}

function runAML() {
  call("/api/aml/screen", {
    transaction: {
      amount_rmb:         +document.getElementById("aml-amount").value,
      count_24h:          +document.getElementById("aml-count").value,
      cross_border:       document.getElementById("aml-cross").checked,
      counterparty_risky: document.getElementById("aml-risky").checked,
      night_time:         document.getElementById("aml-night").checked,
      cash_intensive:     document.getElementById("aml-cash").checked,
      new_account_days:   +document.getElementById("aml-new").value,
      note:               document.getElementById("aml-note").value,
    },
  }, "aml-out");
}

function runCredit() {
  call("/api/credit/score", {
    customer_name:   document.getElementById("cr-name").value,
    age:             +document.getElementById("cr-age").value,
    income_monthly:  +document.getElementById("cr-income").value,
    debt_monthly:    +document.getElementById("cr-debt").value,
    employment:      document.getElementById("cr-emp").value,
    credit_history:  document.getElementById("cr-hist").value,
    loan_amount:     +document.getElementById("cr-loan").value,
    loan_purpose:    document.getElementById("cr-purpose").value,
    region:          document.getElementById("cr-region").value,
    device_risk:     document.getElementById("cr-device").value,
    blacklist_hit:   document.getElementById("cr-bl").checked,
  }, "cr-out");
}

function runAdvisory() {
  const level = document.getElementById("adv-level").value;
  call("/api/advisory/qa", {
    question:       document.getElementById("adv-q").value,
    customer_level: level || null,
  }, "adv-out");
}

function runSuitability() {
  call("/api/suitability/check", {
    customer_level:  document.getElementById("su-level").value,
    product_code:    document.getElementById("su-code").value,
    invest_amount:   +document.getElementById("su-amount").value,
    holding_horizon: document.getElementById("su-horizon").value,
  }, "su-out");
}

function runCustomer() {
  const products = document.getElementById("ci-prod").value
    .split(/[,,]/).map((s) => s.trim()).filter(Boolean);
  const npsRaw = document.getElementById("ci-nps").value;
  call("/api/customer/insight", {
    customer_id:           document.getElementById("ci-id").value,
    age:                   +document.getElementById("ci-age").value,
    aum_rmb:               +document.getElementById("ci-aum").value,
    last_active_days:      +document.getElementById("ci-act").value,
    products_held:         products,
    redemption_30d:        +document.getElementById("ci-red").value,
    interaction_count_30d: +document.getElementById("ci-int").value,
    nps_score:             npsRaw === "" ? null : +npsRaw,
  }, "ci-out");
}

function runPII() {
  call("/api/pii/redact", {
    text: document.getElementById("pii-in").value,
  }, "pii-out");
}
