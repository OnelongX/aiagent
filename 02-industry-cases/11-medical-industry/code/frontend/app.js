// Medical AI Assistant · frontend
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

function runImaging() {
  call("/api/imaging/review", {
    modality:         document.getElementById("img-modality").value,
    body_part:        document.getElementById("img-body").value,
    clinical_history: document.getElementById("img-history").value,
    findings_text:    document.getElementById("img-findings").value,
  }, "img-out");
}

function runTriage() {
  call("/api/triage/", {
    age:             +document.getElementById("tri-age").value,
    sex:             document.getElementById("tri-sex").value,
    chief_complaint: document.getElementById("tri-cc").value,
    duration:        document.getElementById("tri-dur").value,
    history:         document.getElementById("tri-hist").value,
  }, "tri-out");
}

function runMedication() {
  const drugs = document.getElementById("med-drugs").value
    .split(/[,,]/).map((s) => s.trim()).filter(Boolean);
  const allergy = document.getElementById("med-allergy").value.trim();
  call("/api/medication/check", {
    drugs,
    patient_age:       +document.getElementById("med-age").value,
    patient_weight_kg: +document.getElementById("med-weight").value,
    pregnancy:         document.getElementById("med-preg").checked,
    lactation:         document.getElementById("med-lact").checked,
    renal_function:    document.getElementById("med-renal").value,
    hepatic_function:  document.getElementById("med-hepatic").value,
    allergies:         allergy ? [allergy] : [],
  }, "med-out");
}

function runDischarge() {
  const meds = document.getElementById("dis-meds").value
    .split(/[,,]/).map((s) => s.trim()).filter(Boolean);
  call("/api/discharge/summary", {
    admission_date:   document.getElementById("dis-in").value,
    discharge_date:   document.getElementById("dis-out").value,
    chief_complaint:  document.getElementById("dis-cc").value,
    admission_dx:     document.getElementById("dis-adm").value,
    discharge_dx:     document.getElementById("dis-dis").value,
    course:           document.getElementById("dis-course").value,
    medications:      meds,
    follow_up:        document.getElementById("dis-fu").value,
  }, "dis-out-box");
}

function runCDSS() {
  call("/api/cdss/", {
    age:             +document.getElementById("cdss-age").value,
    sex:             document.getElementById("cdss-sex").value,
    chief_complaint: document.getElementById("cdss-cc").value,
    history:         document.getElementById("cdss-hist").value,
    current_dx:      document.getElementById("cdss-dx").value,
  }, "cdss-out");
}

function runQA() {
  call("/api/education/qa", {
    question:    document.getElementById("qa-q").value,
    patient_age: +document.getElementById("qa-age").value,
    is_followup: document.getElementById("qa-followup").checked,
  }, "qa-out");
}

function runPII() {
  call("/api/pii/redact", {
    text: document.getElementById("pii-in").value,
  }, "pii-out");
}
