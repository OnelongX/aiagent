// === Analytics Module ===

let analyticsChart = null;

function loadAnalytics() {
    const anTotalConv = document.getElementById('anTotalConv');
    const anAvgTime = document.getElementById('anAvgTime');
    const topQueryList = document.getElementById('topQueryList');
    const libId = getCurrentLibrary();

    fetch(`/api/analytics?library_id=${libId}`)
        .then(r => r.json())
        .then(data => {
            if (anTotalConv) anTotalConv.textContent = data.total_sessions || 0;
            if (anAvgTime) anAvgTime.textContent = data.avg_search_time ? data.avg_search_time + 's' : '-';
            renderAnalyticsChart(data.events || []);
        })
        .catch(() => {});

    fetch(`/api/sessions?library_id=${libId}`)
        .then(r => r.json())
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
}

function renderAnalyticsChart(events) {
    const canvas = document.getElementById('analyticsCanvas');
    if (!canvas || typeof Chart === 'undefined') return;

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
    const shortLabels = labels.map(d => { const p = d.split('-'); return `${p[1]}/${p[2]}`; });

    if (analyticsChart) analyticsChart.destroy();

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
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
                x: { grid: { display: false }, ticks: { color: isDark ? '#94A3B8' : '#71717A', font: { family: 'Inter', size: 11 } } },
                y: { grid: { color: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)' }, ticks: { color: isDark ? '#94A3B8' : '#71717A', font: { family: 'Inter', size: 11 } }, beginAtZero: true },
            },
        },
    });
}

// CSV Export
document.getElementById('exportCsvBtn')?.addEventListener('click', () => {
    fetch(`/api/sessions?library_id=${getCurrentLibrary()}`)
        .then(r => r.json())
        .then(sessions => {
            if (!sessions.length) { showToast('暂无数据可导出', 'error'); return; }
            const csv = '会话ID,标题,查询数,创建时间\n' + sessions.map(s => `"${s.id}","${s.title}",${s.query_count},"${s.created_at}"`).join('\n');
            const blob = new Blob([csv], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `pageindex-analytics-${new Date().toISOString().slice(0,10)}.csv`;
            a.click();
            showToast('分析数据已导出为 CSV', 'success');
        })
        .catch(() => showToast('导出数据失败', 'error'));
});
