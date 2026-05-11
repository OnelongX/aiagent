// Education AI Assistant frontend

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
  if (!resp.ok) throw new Error('HTTP ' + resp.status + ': ' + await resp.text());
  return resp.json();
}

function loading(id) {
  document.getElementById(id).innerHTML = '<p class="loading">⏳ 处理中...</p>';
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

// 1. 客观题判分
async function gradeObj() {
  loading('g-obj-result');
  try {
    let questions = JSON.parse(document.getElementById('g-obj').value);
    const data = await post('/grade/objective', { questions });
    let html = '<div class="score-summary">';
    html += '<div class="score-card"><div class="label">总题</div><div class="value">' + data.score_summary.total + '</div></div>';
    html += '<div class="score-card"><div class="label">正确</div><div class="value" style="color:#047857;">' + data.score_summary.correct + '</div></div>';
    html += '<div class="score-card"><div class="label">错误</div><div class="value" style="color:#c0392b;">' + data.score_summary.wrong + '</div></div>';
    html += '<div class="score-card"><div class="label">正确率</div><div class="value">' + (data.score_summary.rate * 100).toFixed(1) + '%</div></div>';
    html += '</div>';
    html += '<table class="obj-table"><thead><tr><th>题号</th><th>学生答案</th><th>正确答案</th><th>结果</th></tr></thead><tbody>';
    data.results.forEach(r => {
      html += '<tr><td>' + r.question_id + '</td><td>' + esc(r.student_answer) + '</td><td>' + esc(r.correct_answer) + '</td>';
      html += '<td class="' + (r.correct ? 'right' : 'wrong') + '">' + (r.correct ? '✓ 正确' : '✗ 错误') + '</td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('g-obj-result').innerHTML = html;
  } catch (e) { showError('g-obj-result', e); }
}

// 2. 作文批改
async function gradeEssay() {
  loading('e-result');
  try {
    const data = await post('/grade/essay', {
      question_id: 'E1',
      prompt: document.getElementById('e-prompt').value,
      student_answer: document.getElementById('e-text').value,
    });
    let html = '<div class="teacher-review-badge">⚠️ 必须教师二审才能发学生</div>';
    if (data.sensitive_flag) {
      html += '<div class="sensitive-flag">🚨 检测到敏感话题(' + data.sensitive_flag + '),AI 不予自动评分 · 请教师亲自阅读</div>';
      html += '<div class="essay-overall">' + esc(data.overall_comment) + '</div>';
      document.getElementById('e-result').innerHTML = html;
      return;
    }
    html += '<h3>初评总分:' + data.initial_total + '</h3>';
    data.dimensions.forEach(d => {
      html += '<div class="essay-dim"><span class="name">' + esc(d.name) + '</span><span class="score">' + d.score + '/' + d.max_score + '</span><div class="comment">' + esc(d.comment) + '</div></div>';
    });
    if (data.highlights && data.highlights.length) {
      html += '<h4 style="margin-top:14px;">✨ 亮点</h4>';
      data.highlights.forEach(h => html += '<p style="color:#047857;">· ' + esc(h) + '</p>');
    }
    if (data.improvements && data.improvements.length) {
      html += '<h4 style="margin-top:14px;">💡 改进建议</h4>';
      data.improvements.forEach(imp => {
        html += '<div class="essay-improve">';
        html += '<div class="loc">📍 ' + esc(imp.location) + '</div>';
        html += '<div class="orig">' + esc(imp.original) + '</div>';
        html += '<div class="sugg">→ ' + esc(imp.suggestion) + '</div>';
        if (imp.reason) html += '<div style="color:#64748b;font-size:12px;margin-top:4px;">理由:' + esc(imp.reason) + '</div>';
        html += '</div>';
      });
    }
    if (data.overall_comment) html += '<div class="essay-overall"><strong>总评</strong><br/>' + esc(data.overall_comment) + '</div>';
    document.getElementById('e-result').innerHTML = html;
  } catch (e) { showError('e-result', e); }
}

// 3. 学情分析
async function doAnalytics() {
  loading('a-result');
  try {
    const data = await post('/analytics/class', {
      class_id: document.getElementById('a-class').value,
      results: JSON.parse(document.getElementById('a-results').value),
    });
    let html = '<div class="score-summary"><div class="score-card"><div class="label">班级整体正确率</div><div class="value">' + (data.overall_correct_rate * 100).toFixed(1) + '%</div></div></div>';
    html += '<h3>🎯 薄弱知识点 TOP ' + data.weak_points.length + '</h3>';
    data.weak_points.forEach(wp => {
      html += '<div class="weak-card">';
      html += '<span class="name">' + esc(wp.knowledge_point) + '</span>';
      html += ' · <span class="rate">正确率 ' + (wp.correct_rate * 100).toFixed(0) + '%</span>';
      html += ' · ' + wp.students_need_support + ' 人需要支持';
      html += '</div>';
    });
    if (data.teaching_suggestions.length) {
      html += '<h3 style="margin-top:16px;">💡 教学建议</h3>';
      data.teaching_suggestions.forEach(s => html += '<p style="margin:4px 0;">· ' + esc(s) + '</p>');
    }
    html += '<div style="margin-top:14px;padding:12px;background:#ecfdf5;border-radius:6px;color:#065f46;font-size:13px;">' + esc(data.notice) + '</div>';
    document.getElementById('a-result').innerHTML = html;
  } catch (e) { showError('a-result', e); }
}

// 4. 周报草稿
async function genReport() {
  loading('r-result');
  try {
    const data = await post('/communication/weekly-report', {
      class_id: document.getElementById('r-class').value,
      learning_data: JSON.parse(document.getElementById('r-data').value),
      teacher_notes: document.getElementById('r-notes').value || null,
    });
    let html = '<div class="teacher-review-badge">⚠️ 教师审核签字后才能发家长群</div>';
    if (data.issues && data.issues.length) {
      html += '<div class="issue-list"><strong>⚠️ 检测到家校沟通禁忌</strong>';
      data.issues.forEach(i => {
        html += '<div class="issue-item">[' + esc(i.issue_type) + '] "' + esc(i.matched_text) + '" - ' + (i.severity === 'block' ? '阻断' : '警告') + '</div>';
      });
      html += '</div>';
    }
    html += '<h3 style="margin-top:14px;">周报草稿</h3>';
    html += '<div class="report-output">' + esc(data.draft) + '</div>';
    document.getElementById('r-result').innerHTML = html;
  } catch (e) { showError('r-result', e); }
}

// 5. 家长答疑
async function parentQA() {
  loading('pq-result');
  try {
    const data = await post('/communication/parent-qa', {
      question: document.getElementById('pq-q').value,
    });
    let html = '<div class="qa-intent ' + data.intent + '">' + data.intent + '</div>';
    html += '<div class="qa-answer">' + esc(data.answer) + '</div>';
    if (data.redirect_to_teacher) {
      html += '<div style="margin-top:10px;padding:10px;background:#fefce8;border-radius:6px;color:#92400e;">📞 建议联系班主任跟进</div>';
    }
    document.getElementById('pq-result').innerHTML = html;
  } catch (e) { showError('pq-result', e); }
}

// 6. 个性化推荐
async function recommend_() {
  loading('rec-result');
  try {
    const weak = document.getElementById('rec-weak').value.split(',').map(s => s.trim()).filter(s => s);
    const mastery = JSON.parse(document.getElementById('rec-mastery').value || '{}');
    const data = await post('/recommend', {
      student_id: document.getElementById('rec-sid').value,
      subject: document.getElementById('rec-subj').value,
      target_count: parseInt(document.getElementById('rec-count').value) || 10,
      weak_points: weak,
      current_mastery: mastery,
    });
    let html = '<h3>📝 推荐题目(' + data.exercises.length + ' 题)</h3>';
    data.exercises.forEach(e => {
      html += '<div class="exercise-card">';
      html += '<div class="kp">📚 ' + esc(e.knowledge_point) + '</div>';
      html += '<div class="preview">' + esc(e.content_preview) + '</div>';
      html += '<div class="meta">难度 ' + (e.difficulty * 100).toFixed(0) + '% · 优先级 ' + (e.priority * 100).toFixed(0) + '% · ID: ' + e.exercise_id + '</div>';
      html += '</div>';
    });
    if (data.study_plan_summary) html += '<div style="margin-top:14px;padding:12px;background:#f0f9ff;border-radius:6px;white-space:pre-wrap;">' + esc(data.study_plan_summary) + '</div>';
    html += '<div class="daily-cap">⏰ 每日学习时长上限:' + data.daily_load_cap_minutes + ' 分钟(双减政策对齐)</div>';
    document.getElementById('rec-result').innerHTML = html;
  } catch (e) { showError('rec-result', e); }
}

// 7. PII 脱敏
async function doPII() {
  loading('p-result');
  try {
    const data = await post('/pii/redact', { text: document.getElementById('p-text').value });
    let html = '<h3>脱敏后文本</h3><div class="pii-redacted">' + esc(data.redacted_text) + '</div>';
    if (data.minor_data_detected) {
      html += '<div class="minor-warning">⚠️ 检测到未成年人相关数据 · 需要家长同意 + 私有部署 · 不能用于商业目的</div>';
    }
    if (data.redacted_entities.length) {
      html += '<h3 style="margin-top:14px;">识别到的敏感实体 (' + data.redacted_entities.length + ')</h3>';
      html += '<table class="obj-table"><thead><tr><th>类型</th><th>占位符</th></tr></thead><tbody>';
      data.redacted_entities.forEach(e => {
        html += '<tr><td>' + esc(e.type) + '</td><td><code>' + esc(e.placeholder) + '</code></td></tr>';
      });
      html += '</tbody></table>';
    } else {
      html += '<p>✅ 未发现敏感信息</p>';
    }
    document.getElementById('p-result').innerHTML = html;
  } catch (e) { showError('p-result', e); }
}
