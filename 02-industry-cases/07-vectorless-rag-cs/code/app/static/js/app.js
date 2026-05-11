// === Main App Module ===
// Orchestrates views, theme, command palette, mobile menu, library switching

// === View Navigation ===
const views = {
    chat: document.getElementById('viewChat'),
    knowledge: document.getElementById('viewKnowledge'),
    analytics: document.getElementById('viewAnalytics'),
    settings: document.getElementById('viewSettings'),
};

document.querySelectorAll('.nav-item[data-view]').forEach(item => {
    item.addEventListener('click', () => switchView(item.dataset.view));
});

function switchView(viewName) {
    Object.values(views).forEach(v => { if (v) v.style.display = 'none'; });
    if (views[viewName]) views[viewName].style.display = 'flex';
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`.nav-item[data-view="${viewName}"]`)?.classList.add('active');
    if (viewName === 'knowledge') loadKnowledgeBase();
    if (viewName === 'analytics') loadAnalytics();
    if (viewName === 'settings') loadSettings();
}

// === Dark Mode ===
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');

function setTheme(dark) {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    localStorage.setItem('theme', dark ? 'dark' : 'light');
    if (themeIcon) themeIcon.innerHTML = dark
        ? '<circle cx="12" cy="12" r="5"/><line x1="12" x2="12" y1="1" y2="3"/><line x1="12" x2="12" y1="21" y2="23"/><line x1="4.22" x2="5.64" y1="4.22" y2="5.64"/><line x1="18.36" x2="19.78" y1="18.36" y2="19.78"/><line x1="1" x2="3" y1="12" y2="12"/><line x1="21" x2="23" y1="12" y2="12"/><line x1="4.22" x2="5.64" y1="19.78" y2="18.36"/><line x1="18.36" x2="19.78" y1="5.64" y2="4.22"/>'
        : '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>';
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#0F172A' : '#2563EB');
}

themeToggle?.addEventListener('click', () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    setTheme(!isDark);
    showToast(isDark ? '已切换到浅色模式' : '已切换到深色模式');
});

if (localStorage.getItem('theme') === 'dark') setTheme(true);

// === Command Palette ===
const cmdOverlay = document.getElementById('cmdOverlay');
const cmdInput = document.getElementById('cmdInput');
let cmdActiveIndex = 0;

function openCmdPalette() { cmdOverlay.classList.add('open'); setTimeout(() => cmdInput.focus(), 50); }
function closeCmdPalette() { cmdOverlay.classList.remove('open'); cmdInput.value = ''; }

function getCmdVisibleItems() { return [...document.querySelectorAll('.cmd-item')].filter(i => i.style.display !== 'none'); }
function updateCmdActive() { document.querySelectorAll('.cmd-item').forEach(i => i.classList.remove('active')); const items = getCmdVisibleItems(); if (items[cmdActiveIndex]) items[cmdActiveIndex].classList.add('active'); }

cmdInput?.addEventListener('input', debounce(() => {
    const q = cmdInput.value.toLowerCase();
    document.querySelectorAll('.cmd-item').forEach(i => { i.style.display = (i.querySelector('.cmd-item-text')?.textContent.toLowerCase() || '').includes(q) ? 'flex' : 'none'; });
    cmdActiveIndex = 0; updateCmdActive();
}, 150));

cmdInput?.addEventListener('keydown', (e) => {
    const items = getCmdVisibleItems();
    if (e.key === 'ArrowDown') { e.preventDefault(); cmdActiveIndex = (cmdActiveIndex + 1) % items.length; updateCmdActive(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); cmdActiveIndex = (cmdActiveIndex - 1 + items.length) % items.length; updateCmdActive(); }
    else if (e.key === 'Enter') { e.preventDefault(); items[cmdActiveIndex]?.click(); }
});

cmdOverlay?.addEventListener('click', (e) => { if (e.target === cmdOverlay) closeCmdPalette(); });

document.querySelectorAll('.cmd-item[data-action]').forEach(item => {
    item.addEventListener('click', () => {
        const action = item.dataset.action;
        closeCmdPalette();
        if (action.startsWith('view:')) switchView(action.split(':')[1]);
        else if (action === 'new-chat') { newChat(); switchView('chat'); }
        else if (action === 'upload') fileUpload.click();
        else if (action === 'toggle-dark') { const d = document.documentElement.getAttribute('data-theme') === 'dark'; setTheme(!d); showToast(d ? '已切换到浅色模式' : '已切换到深色模式'); }
    });
});

// Global keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); cmdOverlay.classList.contains('open') ? closeCmdPalette() : openCmdPalette(); }
    if (e.key === 'Escape' && cmdOverlay.classList.contains('open')) closeCmdPalette();
    if ((e.metaKey || e.ctrlKey) && e.key === 'n') { e.preventDefault(); closeCmdPalette(); newChat(); switchView('chat'); }
    if ((e.metaKey || e.ctrlKey) && e.key === 'u') { e.preventDefault(); closeCmdPalette(); fileUpload.click(); }
    if ((e.metaKey || e.ctrlKey) && e.key === 'd') { e.preventDefault(); closeCmdPalette(); const d = document.documentElement.getAttribute('data-theme') === 'dark'; setTheme(!d); showToast(d ? '已切换到浅色模式' : '已切换到深色模式'); }
    if ((e.metaKey || e.ctrlKey) && e.key === 'f') {
        const chatVisible = views.chat && views.chat.style.display !== 'none';
        if (chatVisible && !cmdOverlay.classList.contains('open')) { e.preventDefault(); openMsgSearch(); }
    }
});

// === Mobile Menu ===
const sidebar = document.querySelector('.sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
document.getElementById('mobileMenuBtn')?.addEventListener('click', () => { sidebar.classList.toggle('open'); sidebarOverlay.classList.toggle('open'); });
sidebarOverlay?.addEventListener('click', () => { sidebar.classList.remove('open'); sidebarOverlay.classList.remove('open'); });
document.querySelectorAll('.nav-item').forEach(item => { item.addEventListener('click', () => { if (window.innerWidth <= 768) { sidebar.classList.remove('open'); sidebarOverlay.classList.remove('open'); } }); });

// === Network Status ===
const networkBar = document.getElementById('networkBar');
window.addEventListener('offline', () => { networkBar.textContent = '您已离线，请检查网络连接。'; networkBar.className = 'network-bar offline'; });
window.addEventListener('online', () => { networkBar.textContent = '网络已恢复'; networkBar.className = 'network-bar online'; });

// === Library Selector ===
const librarySelect = document.getElementById('librarySelect');

function loadLibraries() {
    fetch('/api/libraries')
        .then(r => r.json())
        .then(libs => {
            if (!librarySelect) return;
            const cur = getCurrentLibrary();
            librarySelect.innerHTML = libs.map(l => `<option value="${l.id}" ${l.id === cur ? 'selected' : ''}>${escapeHtml(l.name)} (${l.doc_count})</option>`).join('');
        })
        .catch(() => {});
}

function switchLibrary(libId) {
    setCurrentLibrary(libId);
    updateRecentChats();
    const active = document.querySelector('.nav-item.active')?.dataset.view;
    if (active === 'knowledge') loadKnowledgeBase();
    if (active === 'analytics') loadAnalytics();
}

librarySelect?.addEventListener('change', () => switchLibrary(librarySelect.value));

document.getElementById('manageLibsBtn')?.addEventListener('click', () => {
    const name = prompt('新建知识库名称：');
    if (!name?.trim()) return;
    const desc = prompt('知识库描述（可选）：') || '';
    fetch('/api/libraries', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name.trim(), description: desc }) })
        .then(r => r.json())
        .then(lib => { showToast(`知识库「${lib.name}」已创建`, 'success'); setCurrentLibrary(lib.id); loadLibraries(); })
        .catch(() => showToast('创建失败', 'error'));
});

// === Init ===
loadLibraries();
updateRecentChats();
