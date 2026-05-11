// === Utilities ===

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(fn, ms) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), ms);
    };
}

function showToast(message, type = '') {
    const el = document.getElementById('toast');
    if (!el) return;
    el.textContent = message;
    el.className = 'toast' + (type ? ' ' + type : '');
    el.classList.add('show');
    setTimeout(() => el.classList.remove('show'), 2500);
}

function showConfirm(title, desc, iconType, onConfirm) {
    const overlay = document.getElementById('confirmOverlay');
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmDesc').textContent = desc;
    const iconEl = document.getElementById('confirmIcon');
    iconEl.className = 'confirm-icon ' + iconType;
    iconEl.innerHTML = iconType === 'danger'
        ? '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>'
        : '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>';
    window._confirmCallback = onConfirm;
    overlay.classList.add('open');
}

// Confirm dialog event setup
document.getElementById('confirmCancel')?.addEventListener('click', () => {
    document.getElementById('confirmOverlay').classList.remove('open');
});
document.getElementById('confirmOk')?.addEventListener('click', () => {
    document.getElementById('confirmOverlay').classList.remove('open');
    if (window._confirmCallback) window._confirmCallback();
});
document.getElementById('confirmOverlay')?.addEventListener('click', (e) => {
    if (e.target.id === 'confirmOverlay') {
        e.target.classList.remove('open');
    }
});

// Get current library ID
function getCurrentLibrary() {
    return localStorage.getItem('currentLibrary') || 'default';
}

function setCurrentLibrary(id) {
    localStorage.setItem('currentLibrary', id);
}
