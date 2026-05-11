// === Chat Module ===

let currentSessionId = null;
let queryCount = 0;
let totalSources = 0;
let totalTime = 0;
let sending = false;
let lastFailedMessage = null;

const messagesArea = document.getElementById('messagesArea');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatTitle = document.getElementById('chatTitle');
const chatStatus = document.getElementById('chatStatus');
const chatBadge = document.getElementById('chatBadge');
const quickReplies = document.getElementById('quickReplies');
const recentChats = document.getElementById('recentChats');
const sourceCards = document.getElementById('sourceCards');
const treePath = document.getElementById('treePath');
const statQueries = document.getElementById('statQueries');
const statSources = document.getElementById('statSources');
const statTime = document.getElementById('statTime');
const uploadStatus = document.getElementById('uploadStatus');
const kbUploadStatus = document.getElementById('kbUploadStatus');
const fileUpload = document.getElementById('fileUpload');

// === Send Message ===
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || sending) return;

    sending = true;
    sendBtn.disabled = true;

    const welcome = messagesArea.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    if (!currentSessionId) {
        chatTitle.textContent = text.length > 40 ? text.substring(0, 40) + '...' : text;
    }

    appendMessage('user', text);
    messageInput.value = '';
    messageInput.style.height = 'auto';

    const typingEl = appendTyping();
    quickReplies.style.display = 'flex';

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                library_id: getCurrentLibrary(),
                message: text,
            }),
        });

        const data = await res.json();
        typingEl.remove();

        if (!res.ok) {
            appendMessage('bot', '抱歉，发生错误，请重试。');
            return;
        }

        currentSessionId = data.session_id;
        appendMessage('bot', data.reply, data.sources);
        updateSources(data.sources);
        updateTreePath(data.tree_path);

        queryCount++;
        totalSources += data.sources.length;
        totalTime += data.search_time;

        statQueries.textContent = queryCount;
        statSources.textContent = totalSources;
        statTime.textContent = queryCount > 0 ? (totalTime / queryCount).toFixed(1) + 's' : '-';

        updateRecentChats();
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
            <div class="welcome-icon"><svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.5"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M12 8v.01"/><path d="M8 12h.01"/><path d="M16 12h.01"/></svg></div>
            <h3>开始新对话</h3>
            <p>上传 PDF 文档，随时向我提问。AI 助手将为您的客户提供即时、准确的回答。</p>
            <div class="quick-actions">
                <button class="quick-btn" onclick="sendQuickMessage('如何重置密码？')">如何重置密码？</button>
                <button class="quick-btn" onclick="sendQuickMessage('计费选项有哪些？')">计费选项</button>
                <button class="quick-btn" onclick="sendQuickMessage('如何联系客服？')">联系客服</button>
            </div>
        </div>`;

    sourceCards.innerHTML = '<div class="empty-state-small">发送消息查看相关来源</div>';
    treePath.innerHTML = '<div class="empty-state-small">暂无搜索路径</div>';
    statQueries.textContent = '0';
    statSources.textContent = '0';
    statTime.textContent = '-';
}

function retryLastMessage() {
    if (lastFailedMessage) {
        const lastBotRows = messagesArea.querySelectorAll('.message-row.bot');
        const lastBotRow = lastBotRows[lastBotRows.length - 1];
        if (lastBotRow) lastBotRow.remove();
        messageInput.value = lastFailedMessage;
        lastFailedMessage = null;
        sendMessage();
    }
}

// === Message Rendering ===
function appendMessage(role, content, sources = []) {
    const row = document.createElement('div');
    row.className = `message-row ${role}`;
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (role === 'user') {
        row.innerHTML = `<div class="bubble user-bubble">${escapeHtml(content)}<div class="bubble-time">${now}</div></div>`;
    } else {
        const formattedContent = formatBotMessage(content);
        const sourceTags = sources.map(s =>
            `<div class="source-tag"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>来源：${escapeHtml(s.doc_name)} 第${s.start_page}-${s.end_page}页</div>`
        ).join('');

        row.innerHTML = `
            <div class="bot-avatar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg></div>
            <div class="bubble bot-bubble">${formattedContent}${sourceTags}<div class="bubble-time">${now} · 通过 PageIndex RAG</div></div>`;

        const actionsRow = document.createElement('div');
        actionsRow.className = 'bot-actions';
        actionsRow.innerHTML = `
            <button class="bot-action-btn" onclick="copyBotMessage(this)" title="复制"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>复制</button>
            <button class="bot-action-btn" onclick="rateBotMessage(this,'up')"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg></button>
            <button class="bot-action-btn" onclick="rateBotMessage(this,'down')"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg></button>`;
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
        <div class="bot-avatar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg></div>
        <div class="bubble bot-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>
        <span class="typing-text">AI 正在思考...</span>`;
    messagesArea.appendChild(row);
    messagesArea.scrollTop = messagesArea.scrollHeight;
    return row;
}

function appendRetryMessage(content) {
    const row = document.createElement('div');
    row.className = 'message-row bot';
    row.innerHTML = `
        <div class="bot-avatar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg></div>
        <div class="bubble bot-bubble" style="border-left:3px solid var(--badge-red)">${escapeHtml(content)}
            <div style="margin-top:8px"><button onclick="retryLastMessage()" style="background:var(--accent);color:white;border:none;padding:6px 14px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;font-family:var(--font)">重试</button></div>
        </div>`;
    messagesArea.appendChild(row);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function copyBotMessage(btn) {
    const bubble = btn.closest('.bot-actions').previousElementSibling.querySelector('.bot-bubble');
    if (bubble) {
        navigator.clipboard.writeText(bubble.innerText.replace(/复制$|来源：.*$/gm, '').trim()).then(() => {
            btn.classList.add('copied');
            const orig = btn.innerHTML;
            btn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg>已复制！';
            setTimeout(() => { btn.classList.remove('copied'); btn.innerHTML = orig; }, 2000);
        });
    }
}

function rateBotMessage(btn, dir) {
    btn.style.color = dir === 'up' ? 'var(--success)' : 'var(--badge-red)';
}

function formatBotMessage(text) {
    let html = escapeHtml(text);
    html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => `<pre><code>${code.trim()}</code></pre>`);
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    html = html.replace(/^(\d+)\.\s+(.+)$/gm, '<div style="padding-left:8px;margin:2px 0">$1. $2</div>');
    html = html.replace(/^[•\-]\s+(.+)$/gm, '<div style="padding-left:8px;margin:2px 0">• $1</div>');
    html = html.replace(/\n/g, '<br>');
    return html;
}

// === Right Panel ===
function updateSources(sources) {
    if (!sources || !sources.length) {
        sourceCards.innerHTML = '<div class="empty-state-small">未找到相关来源</div>';
        return;
    }
    const colors = ['blue', 'amber', 'green'];
    const confLabels = ['HIGH', 'MED', 'LOW'];
    const confClasses = ['high', 'med', 'low'];
    sourceCards.innerHTML = sources.map((s, i) => {
        const color = colors[i % 3];
        const score = s.relevance_score || 0;
        const ci = score >= 80 ? 0 : score >= 50 ? 1 : 2;
        return `<div class="source-card"><div class="source-card-header"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="${color==='blue'?'#2563EB':color==='amber'?'#F59E0B':'#22C55E'}" stroke-width="2"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg><span class="source-card-title">${escapeHtml(s.doc_name)}</span><span class="confidence-badge ${confClasses[ci]}">${confLabels[ci]}</span></div><div class="source-card-pages ${color}">第 ${s.start_page}-${s.end_page} 页</div><div class="source-card-desc">${escapeHtml(s.title)}${s.reason?' — '+escapeHtml(s.reason):''}</div><div class="relevance-bar"><span class="relevance-label">相关度：</span><div class="bar-track"><div class="bar-fill ${color}" style="width:${score}%"></div></div><span class="relevance-value" style="color:${color==='blue'?'#2563EB':color==='amber'?'#D97706':'#22C55E'}">${score}%</span></div></div>`;
    }).join('');
}

function updateTreePath(path) {
    if (!path || !path.length) {
        treePath.innerHTML = '<div class="empty-state-small">暂无搜索路径</div>';
        return;
    }
    treePath.innerHTML = path.map((node, i) => {
        const isFirst = i === 0, isLast = i === path.length - 1;
        const indent = i * 22;
        const type = isFirst ? 'root' : isLast ? 'leaf' : 'branch';
        const icon = isFirst
            ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>'
            : isLast ? '<svg width="6" height="6"><circle cx="3" cy="3" r="3" fill="#2563EB"/></svg>'
            : '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#A1A1AA" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>';
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
    fetch(`/api/sessions?library_id=${getCurrentLibrary()}`)
        .then(r => r.json())
        .then(sessions => {
            renderRecentChatsList(sessions);
            chatBadge.textContent = sessions.length || '0';
            sessions.length ? chatBadge.classList.add('visible') : chatBadge.classList.remove('visible');
        })
        .catch(() => {});
}

function loadSession(sessionId) {
    fetch(`/api/session/${sessionId}`)
        .then(r => r.json())
        .then(session => {
            currentSessionId = session.id;
            chatTitle.textContent = session.title;
            queryCount = session.query_count;
            totalSources = session.source_count || 0;
            messagesArea.innerHTML = '';
            for (const msg of session.history) appendMessage(msg.role === 'user' ? 'user' : 'bot', msg.content);
            quickReplies.style.display = 'flex';
            statQueries.textContent = queryCount;
            statSources.textContent = totalSources;
            updateRecentChats();
        })
        .catch(() => {});
}

function deleteSession(sessionId) {
    fetch(`/api/session/${sessionId}`, { method: 'DELETE' })
        .then(() => {
            showToast('会话已删除', 'success');
            if (currentSessionId === sessionId) newChat();
            updateRecentChats();
        })
        .catch(() => showToast('会话已移除'));
}

// === File Upload ===
const MAX_FILE_SIZE = 50 * 1024 * 1024;

function validateFile(file) {
    const ext = file.name.toLowerCase().split('.').pop();
    if (!['pdf', 'md', 'markdown'].includes(ext)) { showToast('仅支持 PDF 和 Markdown 文件', 'error'); return false; }
    if (file.size > MAX_FILE_SIZE) { showToast(`文件过大（${(file.size/1024/1024).toFixed(1)}MB），最大 50MB`, 'error'); return false; }
    return true;
}

function setUploadStatusHTML(html) {
    uploadStatus.innerHTML = html;
    if (kbUploadStatus) kbUploadStatus.innerHTML = html;
}
function setUploadStatusText(text) {
    uploadStatus.textContent = text;
    if (kbUploadStatus) kbUploadStatus.textContent = text;
}
function setUploadStatusVisible(visible) {
    uploadStatus.style.display = visible ? 'block' : 'none';
    if (kbUploadStatus) kbUploadStatus.style.display = visible ? 'block' : 'none';
}

function handleFileUpload(file) {
    if (!file || !validateFile(file)) return;

    setUploadStatusVisible(true);
    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();

    // Phase 1: Upload progress
    setUploadStatusHTML(`<div style="display:flex;align-items:center;gap:8px;width:100%"><span style="white-space:nowrap;font-size:12px;color:var(--accent)">正在上传 ${escapeHtml(file.name)}</span><div style="flex:1;height:4px;background:var(--border);border-radius:2px;overflow:hidden"><div class="js-upload-bar" style="width:0%;height:100%;background:var(--accent);border-radius:2px;transition:width 0.2s"></div></div><span class="js-upload-pct" style="font-size:11px;font-weight:600;color:var(--accent);min-width:35px">0%</span></div>`);

    xhr.upload.addEventListener('progress', (evt) => {
        if (evt.lengthComputable) {
            const pct = Math.round((evt.loaded / evt.total) * 100);
            document.querySelectorAll('.js-upload-bar').forEach(el => el.style.width = pct + '%');
            document.querySelectorAll('.js-upload-pct').forEach(el => el.textContent = pct + '%');
        }
    });

    xhr.addEventListener('load', () => {
        try {
            const data = JSON.parse(xhr.responseText);
            if (xhr.status === 200 && data.task_id) {
                showToast(`${escapeHtml(file.name)} 已提交，正在后台索引...`);
                pollTaskStatus(data.task_id, file.name);
            } else {
                setUploadStatusText(`错误：${data.detail || '上传失败'}`);
                showToast(`上传失败：${data.detail || '未知错误'}`, 'error');
            }
        } catch { showToast('处理响应失败', 'error'); }
    });

    xhr.addEventListener('error', () => {
        setUploadStatusText('上传失败，请检查服务器连接。');
        showToast('上传失败，请检查服务器连接。', 'error');
    });

    xhr.open('POST', `/api/upload?library_id=${encodeURIComponent(getCurrentLibrary())}`);
    xhr.send(formData);
}

function pollTaskStatus(taskId, fileName) {
    setUploadStatusHTML(`
        <div style="display:flex;align-items:center;gap:8px;width:100%">
            <span style="white-space:nowrap;font-size:12px;color:var(--accent)" class="js-task-msg">正在索引 ${escapeHtml(fileName)}...</span>
            <div style="flex:1;height:4px;background:var(--border);border-radius:2px;overflow:hidden">
                <div class="js-task-bar" style="width:0%;height:100%;background:var(--accent);border-radius:2px;transition:width 0.5s"></div>
            </div>
            <span class="js-task-pct" style="font-size:11px;font-weight:600;color:var(--accent);min-width:35px">0%</span>
        </div>`);

    const poll = setInterval(() => {
        fetch(`/api/tasks/${taskId}`)
            .then(r => r.json())
            .then(task => {
                document.querySelectorAll('.js-task-bar').forEach(el => el.style.width = task.progress + '%');
                document.querySelectorAll('.js-task-pct').forEach(el => el.textContent = task.progress + '%');
                document.querySelectorAll('.js-task-msg').forEach(el => el.textContent = task.message || '处理中...');

                if (task.status === 'completed') {
                    clearInterval(poll);
                    const result = task.result_data || {};
                    setUploadStatusText(`${result.doc_name || fileName} 索引完成（${result.sections || 0} 个分块）`);
                    showToast(`${result.doc_name || fileName} 索引成功`, 'success');
                    loadLibraries();
                    const kbView = document.getElementById('viewKnowledge');
                    if (kbView && kbView.style.display !== 'none') loadKnowledgeBase();
                    setTimeout(() => { setUploadStatusVisible(false); }, 4000);
                } else if (task.status === 'failed') {
                    clearInterval(poll);
                    setUploadStatusText(`索引失败：${task.error || '未知错误'}`);
                    showToast(`索引失败：${task.error || '未知错误'}`, 'error');
                    setTimeout(() => { setUploadStatusVisible(false); }, 5000);
                }
            })
            .catch(() => {});
    }, 2000);
}

// === Events ===
sendBtn.addEventListener('click', () => sendMessage());
messageInput.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });
messageInput.addEventListener('input', () => { messageInput.style.height = 'auto'; messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px'; });
document.getElementById('newChatBtn')?.addEventListener('click', newChat);
document.getElementById('newChatBtnSidebar')?.addEventListener('click', newChat);

fileUpload.addEventListener('change', (e) => {
    handleFileUpload(e.target.files[0]);
    fileUpload.value = '';
});

// Scroll to bottom button
const scrollBottomBtn = document.getElementById('scrollBottomBtn');
messagesArea.addEventListener('scroll', () => {
    const dist = messagesArea.scrollHeight - messagesArea.scrollTop - messagesArea.clientHeight;
    scrollBottomBtn?.classList.toggle('visible', dist > 150);
});
scrollBottomBtn?.addEventListener('click', () => messagesArea.scrollTo({ top: messagesArea.scrollHeight, behavior: 'smooth' }));

// Message search
const msgSearchBar = document.getElementById('msgSearchBar');
const msgSearchInput = document.getElementById('msgSearchInput');
document.getElementById('msgSearchToggle')?.addEventListener('click', () => {
    msgSearchBar.classList.contains('open') ? closeMsgSearch() : openMsgSearch();
});

function openMsgSearch() { msgSearchBar.classList.add('open'); setTimeout(() => msgSearchInput.focus(), 50); }
function closeMsgSearch() {
    msgSearchBar.classList.remove('open');
    msgSearchInput.value = '';
    document.querySelectorAll('.msg-highlight').forEach(el => el.replaceWith(el.textContent));
}

msgSearchInput?.addEventListener('input', debounce(() => {
    document.querySelectorAll('.msg-highlight').forEach(el => el.replaceWith(el.textContent));
    const q = msgSearchInput.value.trim();
    if (!q) return;
    const regex = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    document.querySelectorAll('.bubble').forEach(bubble => {
        const walker = document.createTreeWalker(bubble, NodeFilter.SHOW_TEXT);
        const nodes = [];
        while (walker.nextNode()) nodes.push(walker.currentNode);
        nodes.forEach(n => {
            if (regex.test(n.textContent)) {
                const span = document.createElement('span');
                span.innerHTML = n.textContent.replace(regex, '<mark class="msg-highlight">$1</mark>');
                n.replaceWith(span);
            }
        });
    });
    document.querySelector('.msg-highlight')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
}, 250));
