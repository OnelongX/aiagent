// Legal Industry AI Assistant frontend

const API = '/api';

document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById(t.dataset.tab).classList.add('active');
  });
});

async function post(path, body) {
  const resp = await fetch(API + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const err = await resp.text();
    throw new Error('HTTP ' + resp.status + ': ' + err);
  }
  return resp.json();
}

function loading(id) {
  document.getElementById(id).innerHTML = '<p class="loading">⏳ 处理中... LLM 调用可能需要 10-30 秒</p>';
}

function showError(id, e) {
  document.getElementById(id).innerHTML = '<div class="error">❌ ' + e.message + '</div>';
}

function esc(s) {
  if (!s) return '';
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[c]);
}

// ============ 1. 合同审查 ============
async function reviewContract() {
  loading('c-result');
  try {
    const data = await post('/contract/review', {
      contract_text: document.getElementById('c-text').value,
      contract_type: document.getElementById('c-type').value,
      jurisdiction: document.getElementById('c-juris').value,
      party_role: document.getElementById('c-role').value,
    });

    let html = '<h3>整体定级:<span class="risk-level ' + data.overall_level.toLowerCase() + '">' + data.overall_level + '</span></h3>';
    if (data.summary) html += '<p style="margin:12px 0;color:#5a5a78;">' + esc(data.summary) + '</p>';
    data.risks.forEach(r => {
      html += '<div class="risk-item ' + r.level.toLowerCase() + '">';
      html += '<span class="risk-level ' + r.level.toLowerCase() + '">' + r.level + '</span>';
      if (r.ai_drafted) html += '<span class="ai-badge">AI 起草</span>';
      html += '<div class="risk-clause">原条款:' + esc(r.clause) + '</div>';
      html += '<div class="risk-issue">⚠️ ' + esc(r.issue) + '</div>';
      html += '<div class="risk-suggestion">💡 ' + esc(r.suggestion) + '</div>';
      html += '</div>';
    });
    html += '<div style="margin-top:14px;padding:12px;background:#fefce8;border-radius:6px;font-size:13px;color:#7c6f00;">📜 ' + esc(data.ai_assist_notice) + '</div>';
    document.getElementById('c-result').innerHTML = html;
  } catch (e) { showError('c-result', e); }
}

// ============ 2. 类案检索 ============
async function searchCases() {
  loading('cs-result');
  try {
    const data = await post('/cases/search', {
      case_facts: document.getElementById('cs-facts').value,
      claim_type: document.getElementById('cs-claim').value,
      jurisdiction: document.getElementById('cs-juris').value,
    });

    let html = '';
    if (data.cross_jurisdiction_warning) {
      html += '<div class="cross-warning">⚠️ 检测到跨地区案例 · 裁判尺度可能不同 · 援引时需评估</div>';
    }
    data.cases.forEach(c => {
      html += '<div class="case-card">';
      html += '<div class="case-num">' + esc(c.case_number) + '</div>';
      html += '<div class="case-title">' + esc(c.title) + '</div>';
      html += '<div class="case-meta">' + esc(c.court) + ' · ' + esc(c.judgment_date) + '</div>';
      if (c.summary) html += '<div class="case-summary">' + esc(c.summary) + '</div>';
      html += '<div class="badges">';
      html += '<span class="badge court-' + c.court_level + '">' + c.court_level + '</span>';
      html += '<span class="badge sim">相似度 ' + (c.similarity * 100).toFixed(0) + '%</span>';
      if (c.source) html += '<span class="badge" style="background:#e0e0f0">' + c.source + '</span>';
      html += '</div></div>';
    });
    html += '<div style="margin-top:14px;padding:12px;background:#fefce8;border-radius:6px;font-size:13px;color:#7c6f00;">⚖️ ' + esc(data.notice) + '</div>';
    document.getElementById('cs-result').innerHTML = html;
  } catch (e) { showError('cs-result', e); }
}

// ============ 3. 文书起草 ============
async function draftDoc() {
  loading('d-result');
  try {
    let caseInfo;
    try {
      caseInfo = JSON.parse(document.getElementById('d-info').value);
    } catch (err) {
      throw new Error('案件信息 JSON 格式错误:' + err.message);
    }
    const data = await post('/drafting/generate', {
      document_type: document.getElementById('d-type').value,
      case_info: caseInfo,
      jurisdiction: '中国大陆',
    });

    let html = '<div class="doc-output">' + esc(data.document) + '</div>';
    if (data.placeholders && data.placeholders.length) {
      html += '<div class="placeholder-list">⚠️ <strong>需要律师亲自补的占位符</strong>(' + data.placeholders.length + ' 处):<br/>';
      data.placeholders.forEach(p => html += '· ' + esc(p) + '<br/>');
      html += '</div>';
    }
    if (data.legal_basis && data.legal_basis.length) {
      html += '<div class="legal-basis"><strong>📚 法律依据(已验真)</strong><br/>';
      data.legal_basis.forEach(l => {
        html += '<div style="margin-top:6px;">';
        html += esc(l.statute) + ' ' + esc(l.article_number);
        if (l.verified) html += ' <span class="verified">✅ 已验真</span>';
        else html += ' <span class="unverified">❌ 未验真 · 慎用</span>';
        if (l.text) html += '<br/><span style="color:#475569;font-size:12px;">' + esc(l.text) + '</span>';
        html += '</div>';
      });
      html += '</div>';
    }
    document.getElementById('d-result').innerHTML = html;
  } catch (e) { showError('d-result', e); }
}

// ============ 4. 法律咨询 ============
async function askQA() {
  loading('qa-result');
  try {
    const data = await post('/qa', {
      question: document.getElementById('qa-q').value,
    });

    let html = '<div class="qa-intent ' + data.intent + '">' + data.intent + '</div>';
    html += '<div class="qa-answer">' + esc(data.answer) + '</div>';
    if (data.emergency_contacts && data.emergency_contacts.length) {
      html += '<div class="emergency-contacts"><strong>🚨 紧急联系</strong><ul>';
      data.emergency_contacts.forEach(c => html += '<li>' + esc(c) + '</li>');
      html += '</ul></div>';
    }
    if (data.referenced_laws && data.referenced_laws.length) {
      html += '<div class="legal-basis"><strong>📚 相关法律</strong><br/>';
      data.referenced_laws.forEach(l => {
        html += '<div>' + esc(l.statute) + ' ' + esc(l.article_number) + '</div>';
      });
      html += '</div>';
    }
    document.getElementById('qa-result').innerHTML = html;
  } catch (e) { showError('qa-result', e); }
}

// ============ 5. 法规追踪 ============
async function trackReg() {
  loading('r-result');
  try {
    const data = await post('/regulation/track', {
      days: parseInt(document.getElementById('r-days').value) || 7,
      business_keywords: document.getElementById('r-keywords').value.split(',').map(s => s.trim()).filter(s => s),
    });

    let html = '';
    data.updates.forEach(u => {
      html += '<div class="reg-card">';
      html += '<div class="reg-title">' + esc(u.title) + '</div>';
      html += '<div class="reg-source">' + esc(u.source) + ' · 发布 ' + esc(u.publish_date) + (u.effective_date ? ' · 生效 ' + esc(u.effective_date) : '') + '</div>';
      html += '<div class="reg-summary">' + esc(u.summary) + '</div>';
      if (u.affected_industries.length) {
        html += '<div style="margin-top:6px;">影响:';
        u.affected_industries.forEach(i => html += '<span class="badge sim" style="margin-right:4px;">' + esc(i) + '</span>');
        html += '</div>';
      }
      if (u.source_url) html += '<div class="reg-link" style="margin-top:6px;"><a href="' + u.source_url + '" target="_blank">原文链接</a></div>';
      html += '</div>';
    });
    html += '<div style="margin-top:14px;padding:12px;background:#fef2f2;border-radius:6px;font-size:13px;color:#c0392b;">⚠️ ' + esc(data.warning) + '</div>';
    document.getElementById('r-result').innerHTML = html;
  } catch (e) { showError('r-result', e); }
}

// ============ 6. PII 脱敏 ============
async function doPII() {
  loading('p-result');
  try {
    const data = await post('/pii/redact', {
      text: document.getElementById('p-text').value,
    });

    let html = '<h3>脱敏后文本</h3><div class="pii-redacted">' + esc(data.redacted_text) + '</div>';
    if (data.redacted_entities.length) {
      html += '<h3 style="margin-top:14px;">识别到的敏感实体 (' + data.redacted_entities.length + ')</h3>';
      html += '<table class="pii-table"><thead><tr><th>类型</th><th>占位符</th></tr></thead><tbody>';
      data.redacted_entities.forEach(e => {
        html += '<tr><td>' + esc(e.type) + '</td><td><code>' + esc(e.placeholder) + '</code></td></tr>';
      });
      html += '</tbody></table>';
    } else {
      html += '<p>✅ 未发现敏感信息(或脱敏未启用)</p>';
    }
    document.getElementById('p-result').innerHTML = html;
  } catch (e) { showError('p-result', e); }
}
