// === Settings Module ===

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
        document.getElementById('settingsSaveBtn').style.display = page === 'danger' ? 'none' : 'flex';
    });
});

function loadSettings() {
    fetch('/api/settings')
        .then(r => r.json())
        .then(s => {
            const set = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
            const chk = (id, val) => { const el = document.getElementById(id); if (el) el.checked = val !== false; };
            set('settingName', s.profile?.name);
            set('settingEmail', s.profile?.email);
            set('settingRole', s.profile?.role);
            set('settingTimezone', s.profile?.timezone);
            const sn = document.querySelector('.user-name');
            if (sn && s.profile?.name) sn.textContent = s.profile.name;
            set('settingModel', s.ai?.model);
            const tempEl = document.getElementById('settingTemp');
            if (tempEl) { tempEl.value = s.ai?.temperature ?? 0.7; document.getElementById('settingTempVal').textContent = tempEl.value; }
            set('settingMaxTokens', String(s.ai?.max_tokens || 2048));
            chk('settingAutoSuggest', s.ai?.auto_suggest);
            chk('settingRag', s.ai?.rag_enabled);
            chk('settingLogging', s.ai?.logging_enabled);
            chk('notifNewConv', s.notifications?.new_conversation);
            chk('notifResolution', s.notifications?.resolution);
            chk('notifEscalation', s.notifications?.escalation);
            chk('notifWeekly', s.notifications?.weekly_report);
            chk('notifSound', s.notifications?.sound);
        })
        .catch(() => {});
}

// Save
document.getElementById('settingsSaveBtn')?.addEventListener('click', () => {
    const page = document.querySelector('.settings-nav-item.active')?.dataset.settingsPage;
    let section, data;
    if (page === 'general') {
        section = 'profile';
        data = { name: document.getElementById('settingName')?.value, email: document.getElementById('settingEmail')?.value, role: document.getElementById('settingRole')?.value, timezone: document.getElementById('settingTimezone')?.value };
        if (!data.name?.trim()) { showToast('姓名不能为空', 'error'); return; }
        if (!data.email?.includes('@')) { showToast('请输入有效邮箱', 'error'); return; }
    } else if (page === 'aimodel') {
        section = 'ai';
        data = { model: document.getElementById('settingModel')?.value, temperature: parseFloat(document.getElementById('settingTemp')?.value || 0.7), max_tokens: parseInt(document.getElementById('settingMaxTokens')?.value || 2048), auto_suggest: document.getElementById('settingAutoSuggest')?.checked, rag_enabled: document.getElementById('settingRag')?.checked, logging_enabled: document.getElementById('settingLogging')?.checked };
    } else if (page === 'notifications') {
        section = 'notifications';
        data = { new_conversation: document.getElementById('notifNewConv')?.checked, resolution: document.getElementById('notifResolution')?.checked, escalation: document.getElementById('notifEscalation')?.checked, weekly_report: document.getElementById('notifWeekly')?.checked, sound: document.getElementById('notifSound')?.checked };
    }
    if (!section) return;
    fetch(`/api/settings/${section}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(() => {
            showToast('设置已保存', 'success');
            if (section === 'profile') {
                const sn = document.querySelector('.user-name');
                if (sn) sn.textContent = data.name;
                const sr = document.querySelector('.user-role');
                if (sr) sr.textContent = data.role;
            }
        })
        .catch(() => showToast('保存失败', 'error'));
});

document.getElementById('settingTemp')?.addEventListener('input', (e) => {
    document.getElementById('settingTempVal').textContent = e.target.value;
});

// Avatar
document.getElementById('changeAvatarBtn')?.addEventListener('click', () => document.getElementById('avatarUpload')?.click());
document.getElementById('avatarUpload')?.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) { showToast('头像文件不能超过 2MB', 'error'); return; }
    const reader = new FileReader();
    reader.onload = (ev) => { document.getElementById('avatarPreview').innerHTML = `<img src="${ev.target.result}" alt="头像">`; showToast('头像已更新', 'success'); };
    reader.readAsDataURL(file);
    e.target.value = '';
});

// Danger zone
document.getElementById('resetDataBtn')?.addEventListener('click', () => {
    showConfirm('确认重置训练数据？', '将清除所有索引数据，需要重新索引。', 'warning', () => {
        fetch('/api/settings/reset', { method: 'POST' }).then(() => showToast('训练数据已重置', 'success')).catch(() => showToast('重置失败', 'error'));
    });
});
document.getElementById('deleteWorkspaceBtn')?.addEventListener('click', () => {
    showConfirm('确认删除工作区？', '永久删除所有数据，不可撤销！', 'danger', () => {
        fetch('/api/settings/workspace', { method: 'DELETE' }).then(() => { showToast('工作区已删除', 'success'); setTimeout(() => window.location.reload(), 1500); }).catch(() => showToast('删除失败', 'error'));
    });
});
