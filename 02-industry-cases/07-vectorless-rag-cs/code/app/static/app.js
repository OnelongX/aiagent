// === State ===
let currentSessionId = null;
let queryCount = 0;
let totalSources = 0;
let totalTime = 0;
let sending = false;

// === DOM ===
const messagesArea = document.getElementById('messagesArea');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const newChatBtnSidebar = document.getElementById('newChatBtnSidebar');
const fileUpload = document.getElementById('fileUpload');
const uploadStatus = document.getElementById('uploadStatus');
const chatTitle = document.getElementById('chatTitle');
const chatStatus = document.getElementById('chatStatus');
const chatBadge = document.getElementById('chatBadge');
const recentChats = document.getElementById('recentChats');
const sourceCards = document.getElementById('sourceCards');
const treePath = document.getElementById('treePath');
const statQueries = document.getElementById('statQueries');
const statSources = document.getElementById('statSources');
const statTime = document.getElementById('statTime');
const quickReplies = document.getElementById('quickReplies');

// === Events ===
sendBtn.addEventListener('click', () => sendMessage());
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
// Auto-resize textarea
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
});
newChatBtn.addEventListener('click', newChat);
newChatBtnSidebar.addEventListener('click', newChat);
fileUpload.addEventListener('change', handleFileUpload);

// === Chat Functions ===
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || sending) return;

    sending = true;
    sendBtn.disabled = true;

    // Clear welcome message
    const welcome = messagesArea.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    // Update header
    if (!currentSessionId) {
        chatTitle.textContent = text.length > 40 ? text.substring(0, 40) + '...' : text;
    }

    // Add user message
    appendMessage('user', text);
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Show typing indicator
    const typingEl = appendTyping();

    // Show quick replies after first message
    quickReplies.style.display = 'flex';

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: text,
            }),
        });

        const data = await res.json();
        typingEl.remove();

        if (!res.ok) {
            appendMessage('bot', '抱歉，发生了错误。请重试。');
            return;
        }

        currentSessionId = data.session_id;

        // Add bot response
        appendMessage('bot', data.reply, data.sources);

        // Update right panel
        updateSources(data.sources);
        updateTreePath(data.tree_path);

        // Update stats
        queryCount++;
        totalSources += data.sources.length;
        totalTime += data.search_time;

        statQueries.textContent = queryCount;
        statSources.textContent = totalSources;
        statTime.textContent = queryCount > 0 ? (totalTime / queryCount).toFixed(1) + 's' : '-';

        // Update recent chats
        updateRecentChats();

        // Update badge
        chatBadge.textContent = queryCount;
        chatBadge.classList.add('visible');

    } catch (err) {
        typingEl.remove();
        lastFailedMessage = text;
        appendRetryMessage('连接错误，请检查服务器是否运行。');
    } finally {
        sending = false;
        sendBtn.disabled = false;
    }
}

function appendRetryMessage(content) {
    const row = document.createElement('div');
    row.className = 'message-row bot';
    row.innerHTML = `
        <div class="bot-avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
        </div>
        <div class="bubble bot-bubble" style="border-left:3px solid var(--badge-red)">
            ${escapeHtml(content)}
            <div style="margin-top:8px">
                <button onclick="retryLastMessage()" style="background:var(--accent);color:white;border:none;padding:6px 14px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;font-family:var(--font)">
                    重试
                </button>
            </div>
        </div>`;
    messagesArea.appendChild(row);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function sendQuickMessage(text) {
    messageInput.value = text;
    sendMessage();
}

function newChat() {
    currentSessionId = null;
    queryCount = 0;
    totalSources = 0;
    totalTime = 0;
    chatTitle.textContent = '新对话';
    chatStatus.textContent = '准备就绪';
    chatBadge.classList.remove('visible');
    quickReplies.style.display = 'none';

    messagesArea.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M12 8v.01"/><path d="M8 12h.01"/><path d="M16 12h.01"/>
                </svg>
            </div>
            <h3>开始新对话</h3>
            <p>上传 PDF 文档，随时向我提问。AI 助手将为您的客户提供即时、准确的回答。</p>
            <div class="quick-actions">
                <button class="quick-btn" onclick="sendQuickMessage('如何重置密码？')">如何重置密码？</button>
                <button class="quick-btn" onclick="sendQuickMessage('有哪些计费选项？')">计费选项</button>
                <button class="quick-btn" onclick="sendQuickMessage('如何联系客服？')">联系客服</button>
            </div>
        </div>`;

    sourceCards.innerHTML = '<div class="empty-state-small">发送消息查看相关来源</div>';
    treePath.innerHTML = '<div class="empty-state-small">暂无搜索路径</div>';
    statQueries.textContent = '0';
    statSources.textContent = '0';
    statTime.textContent = '-';
}

// === Message Rendering ===
function appendMessage(role, content, sources = []) {
    const row = document.createElement('div');
    row.className = `message-row ${role}`;

    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (role === 'user') {
        row.innerHTML = `
            <div class="bubble user-bubble">
                ${escapeHtml(content)}
                <div class="bubble-time">${now}</div>
            </div>`;
    } else {
        const formattedContent = formatBotMessage(content);
        const sourceTags = sources.map(s =>
            `<div class="source-tag">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>
                来源：${escapeHtml(s.doc_name)} p.${s.start_page}-${s.end_page}
            </div>`
        ).join('');

        row.innerHTML = `
            <div class="bot-avatar">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>
                </svg>
            </div>
            <div class="bubble bot-bubble">
                ${formattedContent}
                ${sourceTags}
                <div class="bubble-time">${now} · 通过 PageIndex RAG</div>
            </div>`;

        // Add action buttons after the message row
        const actionsRow = document.createElement('div');
        actionsRow.className = 'bot-actions';
        actionsRow.innerHTML = `
            <button class="bot-action-btn" onclick="copyBotMessage(this)" title="复制">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                </svg>
                复制
            </button>
            <button class="bot-action-btn" onclick="rateBotMessage(this, 'up')" title="有帮助">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/>
                </svg>
            </button>
            <button class="bot-action-btn" onclick="rateBotMessage(this, 'down')" title="没有帮助">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/>
                </svg>
            </button>`;

        messagesArea.appendChild(row);
        messagesArea.appendChild(actionsRow);
        messagesArea.scrollTop = messagesArea.scrollHeight;
        return;
    }

    messagesArea.appendChild(row);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function appendTyping() {
    const row = document.createElement('div');
    row.className = 'message-row bot';
    row.innerHTML = `
        <div class="bot-avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>
            </svg>
        </div>
        <div class="bubble bot-bubble">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
        <span class="typing-text">AI 正在思考...</span>`;
    messagesArea.appendChild(row);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    return row;
}

// === Bot Action Handlers ===
function copyBotMessage(btn) {
    const bubble = btn.closest('.bot-actions').previousElementSibling.querySelector('.bot-bubble');
    if (bubble) {
        const text = bubble.innerText.replace(/复制$|来源：.*$/gm, '').trim();
        navigator.clipboard.writeText(text).then(() => {
            btn.classList.add('copied');
            btn.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 6 9 17l-5-5"/>
                </svg>
                已复制！`;
            setTimeout(() => {
                btn.classList.remove('copied');
                btn.innerHTML = `
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                    </svg>
                    复制`;
            }, 2000);
        });
    }
}

function rateBotMessage(btn, direction) {
    btn.style.color = direction === 'up' ? 'var(--success)' : 'var(--badge-red)';
}

function formatBotMessage(text) {
    let html = escapeHtml(text);
    // Code blocks (```)
    html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
        return `<pre><code>${code.trim()}</code></pre>`;
    });
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    // Numbered lists
    html = html.replace(/^(\d+)\.\s+(.+)$/gm, '<div style="padding-left:8px;margin:2px 0">$1. $2</div>');
    // Bullet lists
    html = html.replace(/^[•\-]\s+(.+)$/gm, '<div style="padding-left:8px;margin:2px 0">• $1</div>');
    // Line breaks (but not inside pre)
    html = html.replace(/\n/g, '<br>');
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// === Right Panel Updates ===
function updateSources(sources) {
    if (!sources || sources.length === 0) {
        sourceCards.innerHTML = '<div class="empty-state-small">未找到相关来源</div>';
        return;
    }

    const colors = ['blue', 'amber', 'green'];
    const confidenceLabels = ['HIGH', 'MED', 'LOW'];
    const confidenceClasses = ['high', 'med', 'low'];

    sourceCards.innerHTML = sources.map((s, i) => {
        const color = colors[i % colors.length];
        const score = s.relevance_score || 0;
        const confIdx = score >= 80 ? 0 : score >= 50 ? 1 : 2;
        return `
            <div class="source-card">
                <div class="source-card-header">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="${color === 'blue' ? '#2563EB' : color === 'amber' ? '#F59E0B' : '#22C55E'}" stroke-width="2">
                        <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/>
                    </svg>
                    <span class="source-card-title">${escapeHtml(s.doc_name)}</span>
                    <span class="confidence-badge ${confidenceClasses[confIdx]}">${confidenceLabels[confIdx]}</span>
                </div>
                <div class="source-card-pages ${color}">第 ${s.start_page}-${s.end_page} 页</div>
                <div class="source-card-desc">${escapeHtml(s.title)}${s.reason ? ' — ' + escapeHtml(s.reason) : ''}</div>
                <div class="relevance-bar">
                    <span class="relevance-label">相关度：</span>
                    <div class="bar-track">
                        <div class="bar-fill ${color}" style="width:${score}%"></div>
                    </div>
                    <span class="relevance-value" style="color:${color === 'blue' ? '#2563EB' : color === 'amber' ? '#D97706' : '#22C55E'}">${score}%</span>
                </div>
            </div>`;
    }).join('');
}

function updateTreePath(path) {
    if (!path || path.length === 0) {
        treePath.innerHTML = '<div class="empty-state-small">暂无搜索路径</div>';
        return;
    }

    treePath.innerHTML = path.map((node, i) => {
        const isLast = i === path.length - 1;
        const isFirst = i === 0;
        const indent = i * 22;
        const type = isFirst ? 'root' : isLast ? 'leaf' : 'branch';

        let icon;
        if (isFirst) {
            icon = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>`;
        } else if (isLast) {
            icon = `<svg width="6" height="6"><circle cx="3" cy="3" r="3" fill="#2563EB"/></svg>`;
        } else {
            icon = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#A1A1AA" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>`;
        }

        return `<div class="tree-node ${type}" style="padding-left:${indent}px">${icon}<span>${escapeHtml(node)}</span></div>`;
    }).join('');
}

// === Recent Chats ===
function renderRecentChatsList(sessions) {
    if (!sessions.length) {
        recentChats.innerHTML = '<div class="empty-state-small">暂无对话</div>';
        return;
    }
    recentChats.innerHTML = sessions.slice(0, 10).map(s => `
        <div class="recent-chat ${s.id === currentSessionId ? 'active' : ''}" onclick="loadSession('${s.id}')">
            <div class="recent-chat-content">
                <div class="recent-chat-title">${escapeHtml(s.title)}</div>
                <div class="recent-chat-meta">${s.query_count} 次查询</div>
            </div>
            <button class="recent-chat-delete" onclick="event.stopPropagation();deleteSession('${s.id}')" title="删除" aria-label="删除会话">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
        </div>
    `).join('');
}

function updateRecentChats() {
    fetch('/api/sessions')
        .then(res => res.json())
        .then(sessions => {
            renderRecentChatsList(sessions);
            chatBadge.textContent = sessions.length || '0';
            if (sessions.length) chatBadge.classList.add('visible');
            else chatBadge.classList.remove('visible');
        })
        .catch(() => {});
}

function loadSession(sessionId) {
    fetch(`/api/session/${sessionId}`)
        .then(res => res.json())
        .then(session => {
            currentSessionId = session.id;
            chatTitle.textContent = session.title;
            queryCount = session.query_count;
            totalSources = session.source_count || 0;

            messagesArea.innerHTML = '';
            for (const msg of session.history) {
                appendMessage(msg.role === 'user' ? 'user' : 'bot', msg.content);
            }

            quickReplies.style.display = 'flex';
            statQueries.textContent = queryCount;
            statSources.textContent = totalSources;
            updateRecentChats();
        })
        .catch(() => {});
}

// === File Upload ===
async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    uploadStatus.style.display = 'block';

    const formData = new FormData();
    formData.append('file', file);

    // Use XMLHttpRequest for progress tracking
    const xhr = new XMLHttpRequest();

    // Show progress bar
    uploadStatus.innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;width:100%">
            <span style="white-space:nowrap;font-size:12px;color:var(--accent)">正在上传 ${escapeHtml(file.name)}</span>
            <div style="flex:1;height:4px;background:var(--border);border-radius:2px;overflow:hidden">
                <div id="uploadProgressBar" style="width:0%;height:100%;background:var(--accent);border-radius:2px;transition:width 0.2s"></div>
            </div>
            <span id="uploadPercent" style="font-size:11px;font-weight:600;color:var(--accent);min-width:35px">0%</span>
        </div>`;

    xhr.upload.addEventListener('progress', (evt) => {
        if (evt.lengthComputable) {
            const pct = Math.round((evt.loaded / evt.total) * 100);
            const bar = document.getElementById('uploadProgressBar');
            const pctEl = document.getElementById('uploadPercent');
            if (bar) bar.style.width = pct + '%';
            if (pctEl) pctEl.textContent = pct + '%';
            if (pct >= 100) {
                uploadStatus.innerHTML = `<span style="font-size:12px;color:var(--accent)">正在索引 ${escapeHtml(file.name)}（AI 分析中，请稍候...）</span>`;
            }
        }
    });

    xhr.addEventListener('load', () => {
        try {
            const data = JSON.parse(xhr.responseText);
            if (xhr.status === 200) {
                uploadStatus.textContent = `${data.doc_name} 已索引（${data.sections} 个分块）`;
                showToast(`${data.doc_name} 索引成功（${data.sections} 个分块）`, 'success');
                if (views.knowledge && views.knowledge.style.display !== 'none') {
                    loadKnowledgeBase();
                }
                setTimeout(() => { uploadStatus.style.display = 'none'; }, 3000);
            } else {
                uploadStatus.textContent = `错误：${data.detail}`;
                showToast(`上传失败：${data.detail}`, 'error');
            }
        } catch {
            uploadStatus.textContent = '处理响应失败';
            showToast('处理响应失败', 'error');
        }
    });

    xhr.addEventListener('error', () => {
        uploadStatus.textContent = '上传失败，请检查服务器连接。';
        showToast('上传失败，请检查服务器连接。', 'error');
    });

    xhr.open('POST', `/api/upload?library_id=${encodeURIComponent(currentLibraryId || 'default')}`);
    xhr.send(formData);

    fileUpload.value = '';
}

// === View Navigation ===
const views = {
    chat: document.getElementById('viewChat'),
    knowledge: document.getElementById('viewKnowledge'),
    analytics: document.getElementById('viewAnalytics'),
    settings: document.getElementById('viewSettings'),
};

document.querySelectorAll('.nav-item[data-view]').forEach(item => {
    item.addEventListener('click', () => {
        const view = item.dataset.view;
        switchView(view);
    });
});

function switchView(viewName) {
    // Hide all views
    Object.values(views).forEach(v => { if (v) v.style.display = 'none'; });

    // Show target view
    if (views[viewName]) views[viewName].style.display = 'flex';

    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const activeNav = document.querySelector(`.nav-item[data-view="${viewName}"]`);
    if (activeNav) activeNav.classList.add('active');

    // Load data for specific views
    if (viewName === 'knowledge') loadKnowledgeBase();
    if (viewName === 'analytics') loadAnalytics();
    if (viewName === 'settings') loadSettings();
}

// === Knowledge Base ===
let kbDocs = [];

function loadKnowledgeBase() {
    const kbTableBody = document.getElementById('kbTableBody');
    if (kbTableBody) kbTableBody.innerHTML = renderSkeleton(4);

    fetch('/api/documents')
        .then(res => res.json())
        .then(docs => {
            kbDocs = docs;
            const kbTotal = document.getElementById('kbTotal');
            const kbIndexed = document.getElementById('kbIndexed');

            if (kbTotal) kbTotal.textContent = docs.length;
            if (kbIndexed) kbIndexed.textContent = docs.length;

            renderKbTable(docs);
        })
        .catch(() => {
            if (kbTableBody) kbTableBody.innerHTML = '<div class="empty-state-small">加载文档失败。</div>';
        });
}

function renderKbTable(docs) {
    const kbTableBody = document.getElementById('kbTableBody');
    if (!kbTableBody) return;

    if (!docs.length) {
        kbTableBody.innerHTML = '<div class="empty-state-small">暂无文档，点击"上传文档"开始使用。</div>';
        return;
    }

    kbTableBody.innerHTML = docs.map(d => {
        const name = d.name || d.doc_name || 'Document';
        const docId = d.filename || name.replace(/\.pdf$/i, '');
        const docType = d.doc_type || 'PDF';
        const enhanced = d.enhanced ? '<span style="color:var(--success);font-size:10px;font-weight:600" title="语义增强">✓ 增强</span>' : '';
        return `
        <div class="kb-row" data-name="${escapeHtml(name).toLowerCase()}" style="cursor:pointer" onclick="openDocDetail('${escapeHtml(docId)}')">
            <div class="kb-row-name">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>
                ${escapeHtml(name)}
            </div>
            <div class="kb-row-type"><span class="kb-type-badge blue">PDF</span></div>
            <div class="kb-row-status"><span class="kb-status-dot" style="background:var(--success)"></span><span style="color:var(--success)">已索引</span> ${enhanced}</div>
            <div class="kb-row-chunks">${d.sections || '-'}</div>
            <div class="kb-row-updated">刚刚</div>
            <div class="kb-row-actions" onclick="event.stopPropagation()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="cursor:pointer" title="打开文件" onclick="window.open('/api/documents/${encodeURIComponent(docId)}/file','_blank')"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="cursor:pointer" title="编辑索引" onclick="openDocDetail('${escapeHtml(docId)}')"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="cursor:pointer" class="delete" title="删除" onclick="currentDocId='${escapeHtml(docId)}';document.getElementById('docDeleteBtn').click()"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
            </div>
        </div>`;
    }).join('');
}

// KB search (debounced version is registered in init section below)
const kbSearch = document.getElementById('kbSearch');

// KB tab switching
document.querySelectorAll('.page-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.page-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        // Filter logic (all tabs show same data for now since we only have PDFs)
        renderKbTable(kbDocs);
    });
});

// KB upload button
const uploadDocBtn = document.getElementById('uploadDocBtn');
if (uploadDocBtn) {
    uploadDocBtn.addEventListener('click', () => fileUpload.click());
}

// === Document Detail / Edit ===
const docDetailDrawer = document.getElementById('docDetailDrawer');
let currentDocId = null;
let currentDoc = null;

function openDocDetail(docId) {
    currentDocId = docId;
    if (docDetailDrawer) docDetailDrawer.classList.add('open');

    fetch(`/api/documents/${encodeURIComponent(docId)}`)
        .then(res => res.json())
        .then(doc => {
            currentDoc = doc;
            document.getElementById('docDetailName').textContent = doc.doc_name || docId;
            document.getElementById('docDetailMeta').textContent =
                `${doc.structure?.length || 0} 个分块 · 索引 ID: ${docId}`;
            document.getElementById('docDescEdit').value = doc.doc_description || '';
            document.getElementById('docChunkCount').textContent = doc.structure?.length || 0;
            renderChunks(doc.structure || []);
        })
        .catch(() => showToast('加载文档详情失败', 'error'));
}

function closeDocDetail() {
    if (docDetailDrawer) docDetailDrawer.classList.remove('open');
    currentDocId = null;
    currentDoc = null;
}

document.getElementById('docDetailBack')?.addEventListener('click', closeDocDetail);

function renderChunks(chunks) {
    const list = document.getElementById('docChunksList');
    if (!list) return;
    if (!chunks.length) {
        list.innerHTML = '<div class="empty-state-small">暂无分块数据</div>';
        return;
    }
    list.innerHTML = chunks.map((c, i) => {
        const tags = (c.semantic_tags || []).map(t => `<span class="chunk-tag">${escapeHtml(t)}</span>`).join('');
        const keywords = (c.keywords || []).map(k => `<span class="chunk-keyword">${escapeHtml(k)}</span>`).join('');
        const entities = (c.entities || []).map(e => `<span class="chunk-entity">${escapeHtml(e)}</span>`).join('');
        const titleZh = c.title_zh || '';
        const summaryZh = c.summary_zh || '';
        return `
        <div class="chunk-card" data-chunk-id="${c.node_id}" id="chunk_${c.node_id}">
            <div class="chunk-card-header">
                <span class="chunk-card-id">#${c.node_id}</span>
                <span class="chunk-card-pages">第 ${c.start_index}-${c.end_index} 页</span>
                ${tags ? `<div class="chunk-tags">${tags}</div>` : ''}
                <div class="chunk-card-actions">
                    <button onclick="toggleChunkEdit('${c.node_id}')" title="编辑"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg></button>
                    <button class="delete" onclick="deleteChunk('${c.node_id}')" title="删除"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg></button>
                </div>
            </div>
            <div class="chunk-field">
                <label>原始标题</label>
                <input type="text" value="${escapeHtml(c.title || '')}" id="chunkTitle_${c.node_id}" disabled>
            </div>
            ${titleZh ? `<div class="chunk-field"><label>中文标题</label><input type="text" value="${escapeHtml(titleZh)}" id="chunkTitleZh_${c.node_id}" disabled></div>` : ''}
            <div class="chunk-field">
                <label>页码范围</label>
                <div class="chunk-pages-row">
                    <input type="number" value="${c.start_index}" id="chunkStart_${c.node_id}" disabled placeholder="起始页">
                    <input type="number" value="${c.end_index}" id="chunkEnd_${c.node_id}" disabled placeholder="结束页">
                </div>
            </div>
            ${summaryZh ? `<div class="chunk-field"><label>中文摘要</label><textarea rows="2" id="chunkSummaryZh_${c.node_id}" disabled>${escapeHtml(summaryZh)}</textarea></div>` : ''}
            <div class="chunk-field">
                <label>原始摘要</label>
                <textarea rows="3" id="chunkSummary_${c.node_id}" disabled>${escapeHtml(c.summary || '')}</textarea>
            </div>
            ${keywords ? `<div class="chunk-field"><label>关键词</label><div class="chunk-meta-tags">${keywords}</div></div>` : ''}
            ${entities ? `<div class="chunk-field"><label>实体</label><div class="chunk-meta-tags">${entities}</div></div>` : ''}
            <button class="chunk-save-btn" onclick="saveChunk('${c.node_id}')">保存修改</button>
        </div>`;
    }).join('');
}

function toggleChunkEdit(chunkId) {
    const card = document.getElementById(`chunk_${chunkId}`);
    if (!card) return;
    const isEditing = card.classList.contains('editing');
    // Close all other editing states
    document.querySelectorAll('.chunk-card.editing').forEach(c => {
        c.classList.remove('editing');
        c.querySelectorAll('input, textarea').forEach(el => el.disabled = true);
    });
    if (!isEditing) {
        card.classList.add('editing');
        card.querySelectorAll('input, textarea').forEach(el => el.disabled = false);
        card.querySelector('input')?.focus();
    }
}

function saveChunk(chunkId) {
    if (!currentDocId) return;
    const data = {
        title: document.getElementById(`chunkTitle_${chunkId}`)?.value || '',
        summary: document.getElementById(`chunkSummary_${chunkId}`)?.value || '',
        start_index: parseInt(document.getElementById(`chunkStart_${chunkId}`)?.value) || 1,
        end_index: parseInt(document.getElementById(`chunkEnd_${chunkId}`)?.value) || 1,
    };
    fetch(`/api/documents/${encodeURIComponent(currentDocId)}/chunk/${chunkId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    })
        .then(res => {
            if (!res.ok) throw new Error();
            return res.json();
        })
        .then(() => {
            showToast('分块已保存', 'success');
            const card = document.getElementById(`chunk_${chunkId}`);
            if (card) {
                card.classList.remove('editing');
                card.querySelectorAll('input, textarea').forEach(el => el.disabled = true);
            }
        })
        .catch(() => showToast('保存失败', 'error'));
}

function deleteChunk(chunkId) {
    if (!currentDocId) return;
    showConfirm('确认删除此分块？', '删除后此分块将不再参与检索，但不会影响原始 PDF 文件。', 'warning', () => {
        fetch(`/api/documents/${encodeURIComponent(currentDocId)}/chunk/${chunkId}`, { method: 'DELETE' })
            .then(res => {
                if (!res.ok) throw new Error();
                return res.json();
            })
            .then(r => {
                showToast('分块已删除', 'success');
                document.getElementById(`chunk_${chunkId}`)?.remove();
                document.getElementById('docChunkCount').textContent = r.remaining_chunks;
            })
            .catch(() => showToast('删除失败', 'error'));
    });
}

// Save doc description
document.getElementById('docDescSaveBtn')?.addEventListener('click', () => {
    if (!currentDocId) return;
    const desc = document.getElementById('docDescEdit')?.value || '';
    fetch(`/api/documents/${encodeURIComponent(currentDocId)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_description: desc }),
    })
        .then(res => res.json())
        .then(() => showToast('文档描述已保存', 'success'))
        .catch(() => showToast('保存失败', 'error'));
});

// Delete document
document.getElementById('docDeleteBtn')?.addEventListener('click', () => {
    if (!currentDocId) return;
    showConfirm('确认删除此文档？', '将同时删除索引文件和 PDF 原文件，此操作不可撤销。', 'danger', () => {
        fetch(`/api/documents/${encodeURIComponent(currentDocId)}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(() => {
                showToast('文档已删除', 'success');
                closeDocDetail();
                loadKnowledgeBase();
            })
            .catch(() => showToast('删除失败', 'error'));
    });
});

// Open PDF file
document.getElementById('docOpenFileBtn')?.addEventListener('click', () => {
    if (!currentDocId) return;
    window.open(`/api/documents/${encodeURIComponent(currentDocId)}/file`, '_blank');
});

// Re-index document
document.getElementById('docReindexBtn')?.addEventListener('click', () => {
    if (!currentDocId) return;
    showConfirm('确认重新索引？', '将使用 AI 重新分析 PDF 并生成新的索引结构，原有编辑会被覆盖。', 'warning', () => {
        showToast('正在重新索引...');
        fetch(`/api/documents/${encodeURIComponent(currentDocId)}/reindex`, { method: 'POST' })
            .then(res => {
                if (!res.ok) throw new Error();
                return res.json();
            })
            .then(r => {
                showToast(`重新索引完成，共 ${r.sections} 个分块`, 'success');
                openDocDetail(currentDocId); // Reload
            })
            .catch(() => showToast('重新索引失败', 'error'));
    });
});

// === Skeleton Loading ===
function renderSkeleton(count) {
    return Array.from({ length: count }, () => `
        <div class="kb-row" style="opacity:0.5">
            <div class="kb-row-name"><div class="skeleton" style="width:180px;height:14px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-type"><div class="skeleton" style="width:40px;height:20px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-status"><div class="skeleton" style="width:60px;height:14px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-chunks"><div class="skeleton" style="width:30px;height:14px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-updated"><div class="skeleton" style="width:70px;height:14px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-actions"></div>
        </div>
    `).join('');
}

// === Analytics ===
let analyticsChart = null;

function loadAnalytics() {
    const anTotalConv = document.getElementById('anTotalConv');
    const anAvgTime = document.getElementById('anAvgTime');
    const topQueryList = document.getElementById('topQueryList');

    // Load from analytics API (persisted data)
    fetch('/api/analytics')
        .then(res => res.json())
        .then(data => {
            if (anTotalConv) anTotalConv.textContent = data.total_sessions || 0;
            if (anAvgTime) anAvgTime.textContent = data.avg_search_time ? data.avg_search_time + 's' : '-';

            // Render chart from events
            renderAnalyticsChart(data.events || []);
        })
        .catch(() => {});

    // Load sessions for top queries
    fetch('/api/sessions')
        .then(res => res.json())
        .then(sessions => {
            if (topQueryList && sessions.length > 0) {
                const colors = ['#2563EB', '#22C55E', '#6366F1', '#D97706', '#EF4444'];
                topQueryList.innerHTML = sessions.slice(0, 5).map((s, i) => {
                    const width = Math.max(20, 100 - i * 18);
                    return `
                    <div class="query-item">
                        <div class="query-item-top">
                            <span class="query-item-name">${escapeHtml(s.title)}</span>
                            <span class="query-item-count" style="color:${colors[i]}">${s.query_count}</span>
                        </div>
                        <div class="query-bar"><div class="query-bar-fill" style="width:${width}%;background:${colors[i]}"></div></div>
                    </div>`;
                }).join('');
            }
        })
        .catch(() => {});
}

function renderAnalyticsChart(events) {
    const canvas = document.getElementById('analyticsCanvas');
    if (!canvas || typeof Chart === 'undefined') return;

    // Group search events by date
    const dailyData = {};
    events.filter(e => e.event_type === 'search').forEach(e => {
        const day = (e.created_at || '').slice(0, 10);
        if (!day) return;
        if (!dailyData[day]) dailyData[day] = { queries: 0, sources: 0 };
        dailyData[day].queries++;
        const d = JSON.parse(e.data || '{}');
        dailyData[day].sources += d.sources || 0;
    });

    const labels = Object.keys(dailyData).sort().slice(-7);
    const queries = labels.map(d => dailyData[d]?.queries || 0);
    const sources = labels.map(d => dailyData[d]?.sources || 0);

    // Format labels to short date
    const shortLabels = labels.map(d => {
        const parts = d.split('-');
        return `${parts[1]}/${parts[2]}`;
    });

    if (analyticsChart) analyticsChart.destroy();

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    const textColor = isDark ? '#94A3B8' : '#71717A';

    analyticsChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: shortLabels.length ? shortLabels : ['暂无数据'],
            datasets: [
                { label: '查询数', data: queries.length ? queries : [0], backgroundColor: '#2563EB', borderRadius: 4 },
                { label: '来源数', data: sources.length ? sources : [0], backgroundColor: '#FDE68A', borderRadius: 4 },
            ],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { color: textColor, font: { family: 'Inter', size: 11 } } },
                y: { grid: { color: gridColor }, ticks: { color: textColor, font: { family: 'Inter', size: 11 } }, beginAtZero: true },
            },
        },
    });
}

// === CSV Export ===
const exportCsvBtn = document.getElementById('exportCsvBtn');
if (exportCsvBtn) {
    exportCsvBtn.addEventListener('click', () => {
        fetch('/api/sessions')
            .then(res => res.json())
            .then(sessions => {
                if (!sessions.length) {
                    showToast('暂无数据可导出', 'error');
                    return;
                }
                const header = '会话ID,标题,查询数,创建时间\n';
                const rows = sessions.map(s =>
                    `"${s.id}","${s.title}",${s.query_count},"${s.created_at}"`
                ).join('\n');
                const csv = header + rows;
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `pageindex-analytics-${new Date().toISOString().slice(0, 10)}.csv`;
                a.click();
                URL.revokeObjectURL(url);
                showToast('分析数据已导出为 CSV', 'success');
            })
            .catch(() => showToast('导出数据失败', 'error'));
    });
}

// === Settings: Full Implementation ===
const settingsPages = {
    general: { el: document.getElementById('settingsGeneral'), title: '通用设置', desc: '管理账户设置和偏好' },
    aimodel: { el: document.getElementById('settingsAimodel'), title: 'AI 模型配置', desc: '选择和配置 AI 助手使用的模型' },
    notifications: { el: document.getElementById('settingsNotifications'), title: '通知设置', desc: '配置通知偏好' },
    danger: { el: document.getElementById('settingsDanger'), title: '安全与数据', desc: '危险操作与数据管理' },
};

// Sub-page navigation
document.querySelectorAll('.settings-nav-item[data-settings-page]').forEach(item => {
    item.addEventListener('click', () => {
        const page = item.dataset.settingsPage;
        document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        Object.values(settingsPages).forEach(p => { if (p.el) p.el.style.display = 'none'; });
        if (settingsPages[page]) {
            settingsPages[page].el.style.display = 'flex';
            document.getElementById('settingsTitle').textContent = settingsPages[page].title;
            document.getElementById('settingsDesc').textContent = settingsPages[page].desc;
        }
        // Hide save button on danger page
        document.getElementById('settingsSaveBtn').style.display = page === 'danger' ? 'none' : 'flex';
    });
});

// Load settings from backend
function loadSettings() {
    fetch('/api/settings')
        .then(res => res.json())
        .then(s => {
            // Profile
            const nameEl = document.getElementById('settingName');
            const emailEl = document.getElementById('settingEmail');
            const roleEl = document.getElementById('settingRole');
            const tzEl = document.getElementById('settingTimezone');
            if (nameEl) nameEl.value = s.profile?.name || '';
            if (emailEl) emailEl.value = s.profile?.email || '';
            if (roleEl) roleEl.value = s.profile?.role || '客服专员';
            if (tzEl) tzEl.value = s.profile?.timezone || 'UTC+8 (Asia/Shanghai)';
            // Update sidebar user name
            const sidebarName = document.querySelector('.user-name');
            if (sidebarName && s.profile?.name) sidebarName.textContent = s.profile.name;
            // AI
            const modelEl = document.getElementById('settingModel');
            const tempEl = document.getElementById('settingTemp');
            const maxTokEl = document.getElementById('settingMaxTokens');
            const autoEl = document.getElementById('settingAutoSuggest');
            const ragEl = document.getElementById('settingRag');
            const logEl = document.getElementById('settingLogging');
            if (modelEl) modelEl.value = s.ai?.model || 'gpt-4o-mini';
            if (tempEl) { tempEl.value = s.ai?.temperature ?? 0.7; document.getElementById('settingTempVal').textContent = tempEl.value; }
            if (maxTokEl) maxTokEl.value = String(s.ai?.max_tokens || 2048);
            if (autoEl) autoEl.checked = s.ai?.auto_suggest !== false;
            if (ragEl) ragEl.checked = s.ai?.rag_enabled !== false;
            if (logEl) logEl.checked = !!s.ai?.logging_enabled;
            // Notifications
            const nce = document.getElementById('notifNewConv');
            const nre = document.getElementById('notifResolution');
            const nee = document.getElementById('notifEscalation');
            const nwe = document.getElementById('notifWeekly');
            const nse = document.getElementById('notifSound');
            if (nce) nce.checked = s.notifications?.new_conversation !== false;
            if (nre) nre.checked = s.notifications?.resolution !== false;
            if (nee) nee.checked = s.notifications?.escalation !== false;
            if (nwe) nwe.checked = !!s.notifications?.weekly_report;
            if (nse) nse.checked = s.notifications?.sound !== false;
        })
        .catch(() => {});
}

// Save settings
document.getElementById('settingsSaveBtn')?.addEventListener('click', () => {
    // Determine which page is active
    const activePage = document.querySelector('.settings-nav-item.active')?.dataset.settingsPage;
    if (activePage === 'general') {
        const data = {
            name: document.getElementById('settingName')?.value || '',
            email: document.getElementById('settingEmail')?.value || '',
            role: document.getElementById('settingRole')?.value || '',
            timezone: document.getElementById('settingTimezone')?.value || '',
        };
        if (!data.name.trim()) { showToast('姓名不能为空', 'error'); return; }
        if (!data.email.includes('@')) { showToast('请输入有效的邮箱地址', 'error'); return; }
        fetch('/api/settings/profile', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
            .then(res => res.json())
            .then(() => {
                showToast('个人信息已保存', 'success');
                const sidebarName = document.querySelector('.user-name');
                if (sidebarName) sidebarName.textContent = data.name;
                const sidebarRole = document.querySelector('.user-role');
                if (sidebarRole) sidebarRole.textContent = data.role;
            })
            .catch(() => showToast('保存失败', 'error'));
    } else if (activePage === 'aimodel') {
        const data = {
            model: document.getElementById('settingModel')?.value,
            temperature: parseFloat(document.getElementById('settingTemp')?.value || 0.7),
            max_tokens: parseInt(document.getElementById('settingMaxTokens')?.value || 2048),
            auto_suggest: document.getElementById('settingAutoSuggest')?.checked,
            rag_enabled: document.getElementById('settingRag')?.checked,
            logging_enabled: document.getElementById('settingLogging')?.checked,
        };
        fetch('/api/settings/ai', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
            .then(res => res.json())
            .then(() => showToast('AI 模型配置已保存', 'success'))
            .catch(() => showToast('保存失败', 'error'));
    } else if (activePage === 'notifications') {
        const data = {
            new_conversation: document.getElementById('notifNewConv')?.checked,
            resolution: document.getElementById('notifResolution')?.checked,
            escalation: document.getElementById('notifEscalation')?.checked,
            weekly_report: document.getElementById('notifWeekly')?.checked,
            sound: document.getElementById('notifSound')?.checked,
        };
        fetch('/api/settings/notifications', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
            .then(res => res.json())
            .then(() => showToast('通知设置已保存', 'success'))
            .catch(() => showToast('保存失败', 'error'));
    }
});

// Temperature slider live value
document.getElementById('settingTemp')?.addEventListener('input', (e) => {
    document.getElementById('settingTempVal').textContent = e.target.value;
});

// Avatar upload
document.getElementById('changeAvatarBtn')?.addEventListener('click', () => {
    document.getElementById('avatarUpload')?.click();
});
document.getElementById('avatarUpload')?.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) { showToast('头像文件不能超过 2MB', 'error'); return; }
    const reader = new FileReader();
    reader.onload = (ev) => {
        const preview = document.getElementById('avatarPreview');
        if (preview) preview.innerHTML = `<img src="${ev.target.result}" alt="头像">`;
        showToast('头像已更新', 'success');
    };
    reader.readAsDataURL(file);
    e.target.value = '';
});

// Confirm dialog
const confirmOverlay = document.getElementById('confirmOverlay');
let confirmCallback = null;

function showConfirm(title, desc, iconType, onConfirm) {
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmDesc').textContent = desc;
    const iconEl = document.getElementById('confirmIcon');
    iconEl.className = 'confirm-icon ' + iconType;
    iconEl.innerHTML = iconType === 'danger'
        ? '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>'
        : '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>';
    confirmCallback = onConfirm;
    confirmOverlay.classList.add('open');
}

document.getElementById('confirmCancel')?.addEventListener('click', () => {
    confirmOverlay.classList.remove('open');
    confirmCallback = null;
});
document.getElementById('confirmOk')?.addEventListener('click', () => {
    confirmOverlay.classList.remove('open');
    if (confirmCallback) confirmCallback();
    confirmCallback = null;
});
confirmOverlay?.addEventListener('click', (e) => {
    if (e.target === confirmOverlay) { confirmOverlay.classList.remove('open'); confirmCallback = null; }
});

// Danger zone buttons
document.getElementById('resetDataBtn')?.addEventListener('click', () => {
    showConfirm('确认重置训练数据？', '此操作将清除所有已索引文档的训练数据。上传的 PDF 文件不会被删除，但需要重新索引。', 'warning', () => {
        fetch('/api/settings/reset', { method: 'POST' })
            .then(res => res.json())
            .then(() => showToast('训练数据已重置', 'success'))
            .catch(() => showToast('重置失败', 'error'));
    });
});

document.getElementById('deleteWorkspaceBtn')?.addEventListener('click', () => {
    showConfirm('确认删除工作区？', '此操作将永久删除所有对话记录、上传的文档、索引数据和设置。此操作不可撤销！', 'danger', () => {
        fetch('/api/settings/workspace', { method: 'DELETE' })
            .then(res => res.json())
            .then(() => {
                showToast('工作区已删除', 'success');
                setTimeout(() => window.location.reload(), 1500);
            })
            .catch(() => showToast('删除失败', 'error'));
    });
});

// === Dark Mode Toggle ===
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');

function setTheme(dark) {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    localStorage.setItem('theme', dark ? 'dark' : 'light');
    if (themeIcon) {
        themeIcon.innerHTML = dark
            ? '<circle cx="12" cy="12" r="5"/><line x1="12" x2="12" y1="1" y2="3"/><line x1="12" x2="12" y1="21" y2="23"/><line x1="4.22" x2="5.64" y1="4.22" y2="5.64"/><line x1="18.36" x2="19.78" y1="18.36" y2="19.78"/><line x1="1" x2="3" y1="12" y2="12"/><line x1="21" x2="23" y1="12" y2="12"/><line x1="4.22" x2="5.64" y1="19.78" y2="18.36"/><line x1="18.36" x2="19.78" y1="5.64" y2="4.22"/>'
            : '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>';
    }
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(!isDark);
        showToast(isDark ? '已切换到浅色模式' : '已切换到深色模式');
    });
}

// Restore saved theme
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') setTheme(true);

// === Command Palette (⌘K) ===
const cmdOverlay = document.getElementById('cmdOverlay');
const cmdInput = document.getElementById('cmdInput');

function openCmdPalette() {
    cmdOverlay.classList.add('open');
    setTimeout(() => cmdInput.focus(), 50);
}

function closeCmdPalette() {
    cmdOverlay.classList.remove('open');
    cmdInput.value = '';
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // ⌘K or Ctrl+K — open command palette
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        cmdOverlay.classList.contains('open') ? closeCmdPalette() : openCmdPalette();
    }
    // Escape — close command palette
    if (e.key === 'Escape' && cmdOverlay.classList.contains('open')) {
        closeCmdPalette();
    }
    // ⌘N — new chat
    if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
        e.preventDefault();
        closeCmdPalette();
        newChat();
        switchView('chat');
    }
    // ⌘U — upload document
    if ((e.metaKey || e.ctrlKey) && e.key === 'u') {
        e.preventDefault();
        closeCmdPalette();
        fileUpload.click();
    }
    // ⌘D — toggle dark mode
    if ((e.metaKey || e.ctrlKey) && e.key === 'd') {
        e.preventDefault();
        closeCmdPalette();
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(!isDark);
        showToast(isDark ? '已切换到浅色模式' : '已切换到深色模式');
    }
});

// Click overlay to close
cmdOverlay.addEventListener('click', (e) => {
    if (e.target === cmdOverlay) closeCmdPalette();
});

// Command palette item clicks
document.querySelectorAll('.cmd-item[data-action]').forEach(item => {
    item.addEventListener('click', () => {
        const action = item.dataset.action;
        closeCmdPalette();

        if (action.startsWith('view:')) {
            switchView(action.split(':')[1]);
        } else if (action === 'new-chat') {
            newChat();
            switchView('chat');
        } else if (action === 'upload') {
            fileUpload.click();
        } else if (action === 'toggle-dark') {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            setTheme(!isDark);
            showToast(isDark ? '已切换到浅色模式' : '已切换到深色模式');
        }
    });
});

// Command palette search filter + keyboard nav
let cmdActiveIndex = 0;

function getCmdVisibleItems() {
    return [...document.querySelectorAll('.cmd-item')].filter(i => i.style.display !== 'none');
}

function updateCmdActive() {
    document.querySelectorAll('.cmd-item').forEach(i => i.classList.remove('active'));
    const items = getCmdVisibleItems();
    if (items[cmdActiveIndex]) items[cmdActiveIndex].classList.add('active');
}

// Cmd palette keyboard nav (input filter is debounced in init section)
if (cmdInput) {
    cmdInput.addEventListener('keydown', (e) => {
        const items = getCmdVisibleItems();
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            cmdActiveIndex = (cmdActiveIndex + 1) % items.length;
            updateCmdActive();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            cmdActiveIndex = (cmdActiveIndex - 1 + items.length) % items.length;
            updateCmdActive();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (items[cmdActiveIndex]) items[cmdActiveIndex].click();
        }
    });
}

// === Mobile Menu ===
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const sidebar = document.querySelector('.sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        sidebarOverlay.classList.toggle('open');
    });
}

if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
    });
}

// Close sidebar on nav click (mobile)
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('open');
        }
    });
});

// === Toast Notifications ===
const toastEl = document.getElementById('toast');

function showToast(message, type = '') {
    toastEl.textContent = message;
    toastEl.className = 'toast' + (type ? ' ' + type : '');
    toastEl.classList.add('show');
    setTimeout(() => toastEl.classList.remove('show'), 2500);
}

// === P0: Debounce Utility ===
function debounce(fn, ms) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), ms);
    };
}

// Apply debounce to KB search
if (kbSearch) {
    kbSearch.addEventListener('input', debounce(() => {
        const q = kbSearch.value.toLowerCase();
        document.querySelectorAll('.kb-row').forEach(row => {
            const name = row.dataset.name || '';
            row.style.display = name.includes(q) ? 'flex' : 'none';
        });
    }, 200));
}

// Apply debounce to cmd palette search
if (cmdInput) {
    const debouncedCmdSearch = debounce(() => {
        const query = cmdInput.value.toLowerCase();
        document.querySelectorAll('.cmd-item').forEach(item => {
            const text = item.querySelector('.cmd-item-text')?.textContent.toLowerCase() || '';
            item.style.display = text.includes(query) ? 'flex' : 'none';
        });
        cmdActiveIndex = 0;
        updateCmdActive();
    }, 150);
    cmdInput.addEventListener('input', debouncedCmdSearch);
}

// === P0: Scroll to Bottom Button ===
const scrollBottomBtn = document.getElementById('scrollBottomBtn');

messagesArea.addEventListener('scroll', () => {
    const distFromBottom = messagesArea.scrollHeight - messagesArea.scrollTop - messagesArea.clientHeight;
    if (scrollBottomBtn) {
        scrollBottomBtn.classList.toggle('visible', distFromBottom > 150);
    }
});

if (scrollBottomBtn) {
    scrollBottomBtn.addEventListener('click', () => {
        messagesArea.scrollTo({ top: messagesArea.scrollHeight, behavior: 'smooth' });
    });
}

// === P0: Network Status ===
const networkBar = document.getElementById('networkBar');

window.addEventListener('offline', () => {
    networkBar.textContent = '您已离线，请检查网络连接。';
    networkBar.className = 'network-bar offline';
});

window.addEventListener('online', () => {
    networkBar.textContent = '网络已恢复';
    networkBar.className = 'network-bar online';
});

// === P1: Session Delete ===
function deleteSession(sessionId) {
    fetch(`/api/session/${sessionId}`, { method: 'DELETE' })
        .then(res => {
            if (res.ok) {
                showToast('会话已删除', 'success');
                if (currentSessionId === sessionId) newChat();
                updateRecentChats();
            } else {
                // If API doesn't support DELETE, just remove from UI
                showToast('会话已移除');
                if (currentSessionId === sessionId) newChat();
                updateRecentChats();
            }
        })
        .catch(() => showToast('会话已移除'));
}

// === P1: Message Retry ===
let lastFailedMessage = null;

function retryLastMessage() {
    if (lastFailedMessage) {
        // Remove the error message row
        const lastBotRows = messagesArea.querySelectorAll('.message-row.bot');
        const lastBotRow = lastBotRows[lastBotRows.length - 1];
        if (lastBotRow) lastBotRow.remove();
        messageInput.value = lastFailedMessage;
        lastFailedMessage = null;
        sendMessage();
    }
}

// === P1: File Validation ===
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

function validateFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('仅支持 PDF 文件', 'error');
        return false;
    }
    if (file.size > MAX_FILE_SIZE) {
        showToast(`文件过大（${(file.size / 1024 / 1024).toFixed(1)}MB），最大 50MB。`, 'error');
        return false;
    }
    return true;
}

// Override file upload to add validation
fileUpload.removeEventListener('change', handleFileUpload);
fileUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file && validateFile(file)) {
        handleFileUpload(e);
    } else {
        fileUpload.value = '';
    }
});

// Settings persistence is now handled by backend API (see Settings section above)

// === P2: Unified API Wrapper ===
async function apiFetch(url, options = {}) {
    try {
        const res = await fetch(url, options);
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || `Request failed (${res.status})`);
        }
        return await res.json();
    } catch (err) {
        if (!navigator.onLine) {
            showToast('您已离线', 'error');
        }
        throw err;
    }
}

// === P2: Dynamic Theme Color Meta ===
function updateThemeColorMeta() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = isDark ? '#0F172A' : '#2563EB';
}
// Hook into theme toggle
const origSetTheme = setTheme;
// Already handled by setTheme — just add meta update
const themeObserver = new MutationObserver(() => updateThemeColorMeta());
themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

// === P3: Message Search ===
const msgSearchBar = document.getElementById('msgSearchBar');
const msgSearchInput = document.getElementById('msgSearchInput');
const msgSearchToggle = document.getElementById('msgSearchToggle');

function openMsgSearch() {
    msgSearchBar.classList.add('open');
    setTimeout(() => msgSearchInput.focus(), 50);
}

function closeMsgSearch() {
    msgSearchBar.classList.remove('open');
    msgSearchInput.value = '';
    // Remove highlights
    document.querySelectorAll('.msg-highlight').forEach(el => {
        el.replaceWith(el.textContent);
    });
}

if (msgSearchToggle) {
    msgSearchToggle.addEventListener('click', () => {
        msgSearchBar.classList.contains('open') ? closeMsgSearch() : openMsgSearch();
    });
}

if (msgSearchInput) {
    msgSearchInput.addEventListener('input', debounce(() => {
        // Remove old highlights
        document.querySelectorAll('.msg-highlight').forEach(el => {
            el.replaceWith(el.textContent);
        });

        const query = msgSearchInput.value.trim();
        if (!query) return;

        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        document.querySelectorAll('.bubble').forEach(bubble => {
            const walker = document.createTreeWalker(bubble, NodeFilter.SHOW_TEXT);
            const textNodes = [];
            while (walker.nextNode()) textNodes.push(walker.currentNode);
            textNodes.forEach(node => {
                if (regex.test(node.textContent)) {
                    const span = document.createElement('span');
                    span.innerHTML = node.textContent.replace(regex, '<mark class="msg-highlight">$1</mark>');
                    node.replaceWith(span);
                }
            });
        });

        // Scroll to first match
        const firstMatch = document.querySelector('.msg-highlight');
        if (firstMatch) firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 250));
}

// ⌘F to search messages (when chat view active)
document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'f') {
        const chatVisible = views.chat && views.chat.style.display !== 'none';
        if (chatVisible && !cmdOverlay.classList.contains('open')) {
            e.preventDefault();
            openMsgSearch();
        }
    }
});

// === Library Management ===
let currentLibraryId = localStorage.getItem('currentLibrary') || 'default';
const librarySelect = document.getElementById('librarySelect');

function loadLibraries() {
    fetch('/api/libraries')
        .then(res => res.json())
        .then(libs => {
            if (!librarySelect) return;
            librarySelect.innerHTML = libs.map(l =>
                `<option value="${l.id}" ${l.id === currentLibraryId ? 'selected' : ''}>${escapeHtml(l.name)} (${l.doc_count})</option>`
            ).join('');
        })
        .catch(() => {});
}

function switchLibrary(libId) {
    currentLibraryId = libId;
    localStorage.setItem('currentLibrary', libId);
    // Refresh current view data
    updateRecentChats();
    const activeView = document.querySelector('.nav-item.active')?.dataset.view;
    if (activeView === 'knowledge') loadKnowledgeBase();
    if (activeView === 'analytics') loadAnalytics();
}

if (librarySelect) {
    librarySelect.addEventListener('change', () => switchLibrary(librarySelect.value));
}

// Manage libraries button — show dialog to create/manage
document.getElementById('manageLibsBtn')?.addEventListener('click', () => {
    const name = prompt('新建知识库名称：');
    if (!name || !name.trim()) return;
    const desc = prompt('知识库描述（可选）：') || '';
    fetch('/api/libraries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), description: desc }),
    })
        .then(res => res.json())
        .then(lib => {
            showToast(`知识库「${lib.name}」已创建`, 'success');
            loadLibraries();
            switchLibrary(lib.id);
        })
        .catch(() => showToast('创建失败', 'error'));
});

// Override functions to use currentLibraryId

// Override updateRecentChats to scope by library
const _origUpdateRecentChats = updateRecentChats;
updateRecentChats = function() {
    fetch(`/api/sessions?library_id=${currentLibraryId}`)
        .then(res => res.json())
        .then(sessions => {
            renderRecentChatsList(sessions);
            chatBadge.textContent = sessions.length || '0';
            if (sessions.length) chatBadge.classList.add('visible');
            else chatBadge.classList.remove('visible');
        })
        .catch(() => {});
};

// Override loadKnowledgeBase to scope by library
const _origLoadKB = loadKnowledgeBase;
loadKnowledgeBase = function() {
    const kbTableBody = document.getElementById('kbTableBody');
    if (kbTableBody) kbTableBody.innerHTML = renderSkeleton(4);

    fetch(`/api/documents?library_id=${currentLibraryId}`)
        .then(res => res.json())
        .then(docs => {
            kbDocs = docs;
            const kbTotal = document.getElementById('kbTotal');
            const kbIndexed = document.getElementById('kbIndexed');
            if (kbTotal) kbTotal.textContent = docs.length;
            if (kbIndexed) kbIndexed.textContent = docs.filter(d => d.enhanced || d.sections > 0).length;
            renderKbTable(docs);
        })
        .catch(() => {
            if (kbTableBody) kbTableBody.innerHTML = '<div class="empty-state-small">加载文档失败。</div>';
        });
};

// Override loadAnalytics to scope by library
const _origLoadAnalytics = loadAnalytics;
loadAnalytics = function() {
    const anTotalConv = document.getElementById('anTotalConv');
    const anAvgTime = document.getElementById('anAvgTime');
    const topQueryList = document.getElementById('topQueryList');

    fetch(`/api/analytics?library_id=${currentLibraryId}`)
        .then(res => res.json())
        .then(data => {
            if (anTotalConv) anTotalConv.textContent = data.total_sessions || 0;
            if (anAvgTime) anAvgTime.textContent = data.avg_search_time ? data.avg_search_time + 's' : '-';
            renderAnalyticsChart(data.events || []);
        })
        .catch(() => {});

    fetch(`/api/sessions?library_id=${currentLibraryId}`)
        .then(res => res.json())
        .then(sessions => {
            if (topQueryList && sessions.length > 0) {
                const colors = ['#2563EB', '#22C55E', '#6366F1', '#D97706', '#EF4444'];
                topQueryList.innerHTML = sessions.slice(0, 5).map((s, i) => {
                    const width = Math.max(20, 100 - i * 18);
                    return `<div class="query-item"><div class="query-item-top"><span class="query-item-name">${escapeHtml(s.title)}</span><span class="query-item-count" style="color:${colors[i]}">${s.query_count}</span></div><div class="query-bar"><div class="query-bar-fill" style="width:${width}%;background:${colors[i]}"></div></div></div>`;
                }).join('');
            } else if (topQueryList) {
                topQueryList.innerHTML = '<div class="empty-state-small">暂无查询数据</div>';
            }
        })
        .catch(() => {});
};

// Patch sendMessage to include library_id
const _origSendMessageBody = ''; // Will override in the fetch call
// Override via patching the fetch body in sendMessage
const origFetch = window.fetch;
window.fetch = function(url, options) {
    if (url === '/api/chat' && options?.body) {
        try {
            const body = JSON.parse(options.body);
            body.library_id = currentLibraryId;
            options.body = JSON.stringify(body);
        } catch {}
    }
    if (url === '/api/upload' && options?.body instanceof FormData) {
        options.body.append('library_id', currentLibraryId);
    }
    return origFetch.call(this, url, options);
};

// === Init ===
loadLibraries();
updateRecentChats();
updateThemeColorMeta();
