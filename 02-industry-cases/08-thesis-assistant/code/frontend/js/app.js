// Thesis Assistant frontend · 学生论文助手

const API = '/api';

// Tab switching
document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.getElementById(t.dataset.tab).classList.add('active');
  });
});

// Generic POST
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

function showLoading(elId) {
  document.getElementById(elId).innerHTML = '<p class="loading">⏳ 处理中...(LLM 调用可能需要 10-30 秒)</p>';
}

function showError(elId, e) {
  document.getElementById(elId).innerHTML = '<div class="error">❌ ' + e.message + '</div>';
}

// ============ 1. 大纲 ============
async function genOutline() {
  showLoading('o-result');
  try {
    const data = await post('/outline', {
      topic: document.getElementById('o-topic').value,
      discipline: document.getElementById('o-discipline').value,
      paper_type: document.getElementById('o-type').value,
      target_words: parseInt(document.getElementById('o-words').value) || 8000,
      key_points: document.getElementById('o-points').value.split('\n').filter(s => s.trim()),
      n_versions: 3,
    });

    let html = '<p class="hint">💡 ' + (data.note || '请挑选最合适的大纲') + '</p>';
    data.versions.forEach((v, i) => {
      html += '<div class="outline-version"><h3>大纲版本 ' + (i + 1) + '</h3>';
      v.forEach(c => {
        html += '<div class="outline-chapter">';
        html += '<strong>' + escape(c.chapter) + '</strong>';
        if (c.words) html += ' <span style="color:#94a3b8;font-size:12px;">(~' + c.words + ' 字)</span>';
        if (c.subsections && c.subsections.length) {
          html += '<ul>';
          c.subsections.forEach(s => html += '<li>' + escape(s) + '</li>');
          html += '</ul>';
        }
        html += '</div>';
      });
      html += '</div>';
    });
    document.getElementById('o-result').innerHTML = html;
  } catch (e) { showError('o-result', e); }
}

// ============ 2. 章节起草 ============
async function genSection() {
  showLoading('s-result');
  try {
    const data = await post('/section', {
      chapter: document.getElementById('s-chapter').value,
      key_points: document.getElementById('s-points').value.split('\n').filter(s => s.trim()),
      target_words: parseInt(document.getElementById('s-words').value) || 1000,
    });

    let html = '<div class="section-draft">' + escape(data.draft) + '</div>';
    if (data.placeholders && data.placeholders.length) {
      html += '<div class="section-placeholder">⚠️ <strong>需要你亲自补的占位符</strong>(' + data.placeholders.length + ' 处):<br/>';
      data.placeholders.forEach(p => html += '· ' + escape(p) + '<br/>');
      html += '</div>';
    }
    document.getElementById('s-result').innerHTML = html;
  } catch (e) { showError('s-result', e); }
}

// ============ 3. 润色 ============
async function genPolish() {
  showLoading('p-result');
  try {
    const data = await post('/polish', {
      text: document.getElementById('p-text').value,
      style: document.getElementById('p-style').value,
    });

    let html = '';
    if (data.summary) html += '<p class="hint">📝 摘要:' + escape(data.summary) + '</p>';
    if (data.diffs.length === 0) {
      html += '<p>✅ 没有发现需要修改的地方。</p>';
    } else {
      data.diffs.forEach(d => {
        html += '<div class="diff-item">';
        html += '<div class="diff-original">- ' + escape(d.original) + '</div>';
        html += '<div class="diff-polished">+ ' + escape(d.polished) + '</div>';
        if (d.reason) html += '<div class="diff-reason">理由:' + escape(d.reason) + '</div>';
        html += '</div>';
      });
    }
    document.getElementById('p-result').innerHTML = html;
  } catch (e) { showError('p-result', e); }
}

// ============ 4. 文献检索 ============
async function genCite() {
  showLoading('c-result');
  try {
    const data = await post('/cite/search', {
      query: document.getElementById('c-query').value,
      year_from: parseInt(document.getElementById('c-yfrom').value) || null,
      year_to: parseInt(document.getElementById('c-yto').value) || null,
      limit: parseInt(document.getElementById('c-limit').value) || 10,
    });

    let html = '<p class="hint">📚 找到 ' + data.total + ' 篇 · ✅ 已 DOI 校验 · ❌ 未校验请谨慎使用</p>';
    data.papers.forEach(p => {
      html += '<div class="paper-card">';
      html += '<div class="title">' + escape(p.title || '(无标题)') + '</div>';
      html += '<div class="meta">' + escape(p.authors.slice(0, 3).join(', ')) +
              (p.authors.length > 3 ? ' 等' : '') +
              ' · ' + (p.year || '') +
              (p.venue ? ' · ' + escape(p.venue) : '') + '</div>';
      if (p.abstract) html += '<div class="abs">' + escape(p.abstract.slice(0, 200)) + '...</div>';
      html += '<div class="badges">';
      html += '<span class="badge src">' + p.source + '</span>';
      if (p.doi) {
        html += '<span class="badge doi">DOI: ' + escape(p.doi) + '</span>';
        html += '<span class="badge ' + (p.doi_verified ? 'verified' : 'unverified') + '">' +
                (p.doi_verified ? '✅ 已校验' : '❌ 未校验') + '</span>';
      }
      if (p.arxiv_id) html += '<span class="badge src">arxiv:' + escape(p.arxiv_id) + '</span>';
      html += '</div></div>';
    });
    document.getElementById('c-result').innerHTML = html;
  } catch (e) { showError('c-result', e); }
}

// ============ 5. 查重 ============
async function genDedupe() {
  showLoading('d-result');
  try {
    const data = await post('/dedupe', {
      text: document.getElementById('d-text').value,
      compare_against: document.getElementById('d-ref').value.split('\n').filter(s => s.trim()),
      threshold: parseFloat(document.getElementById('d-th').value) || 0.85,
    });

    let html = '<p class="hint">ℹ️ ' + escape(data.notice) + '</p>';
    if (data.issues.length === 0) {
      html += '<p>✅ 未发现高相似度段落。</p>';
    } else {
      data.issues.forEach(i => {
        html += '<div class="dedupe-issue">';
        html += '<div class="sim">⚠️ 相似度:' + (i.similarity * 100).toFixed(1) + '%</div>';
        html += '<div class="chunk">本文片段:' + escape(i.user_chunk) + '</div>';
        html += '<div class="chunk">类似于:' + escape(i.similar_chunk) + '</div>';
        html += '<div class="suggestion">💡 ' + escape(i.suggestion) + '</div>';
        html += '</div>';
      });
    }
    document.getElementById('d-result').innerHTML = html;
  } catch (e) { showError('d-result', e); }
}

// ============ 6. 答辩 ============
async function genDefense() {
  showLoading('df-result');
  try {
    const data = await post('/defense', {
      thesis_abstract: document.getElementById('df-abs').value,
      thesis_outline: document.getElementById('df-out').value.split('\n').filter(s => s.trim()),
      questions_per_persona: parseInt(document.getElementById('df-n').value) || 3,
    });

    const personaNames = {
      critic: '🔴 严厉派(挑刺)',
      friendly: '🟢 友好派(扩展)',
      outsider: '🟣 跨学科派(挑战 generalizability)',
    };

    let html = '';
    data.questions.forEach(q => {
      html += '<div class="defense-question ' + q.persona + '">';
      html += '<div class="persona">' + personaNames[q.persona] + '</div>';
      html += '<div class="q">' + escape(q.question) + '</div>';
      if (q.hint) html += '<div class="hint">💡 ' + escape(q.hint) + '</div>';
      html += '</div>';
    });
    document.getElementById('df-result').innerHTML = html;
  } catch (e) { showError('df-result', e); }
}

function escape(s) {
  if (!s) return '';
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[c]);
}
