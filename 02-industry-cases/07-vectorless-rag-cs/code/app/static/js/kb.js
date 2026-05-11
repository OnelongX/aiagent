// === Knowledge Base Module ===

let kbDocs = [];
let currentDocId = null;
let currentDoc = null;
const docDetailDrawer = document.getElementById('docDetailDrawer');

function loadKnowledgeBase() {
    const kbTableBody = document.getElementById('kbTableBody');
    if (kbTableBody) kbTableBody.innerHTML = renderSkeleton(4);

    fetch(`/api/documents?library_id=${getCurrentLibrary()}`)
        .then(r => r.json())
        .then(docs => {
            kbDocs = docs;
            document.getElementById('kbTotal').textContent = docs.length;
            document.getElementById('kbIndexed').textContent = docs.filter(d => d.enhanced || d.sections > 0).length;
            renderKbTable(docs);
        })
        .catch(() => {
            if (kbTableBody) kbTableBody.innerHTML = '<div class="empty-state-small">加载文档失败。</div>';
        });
}

function renderSkeleton(count) {
    return Array.from({ length: count }, () => `
        <div class="kb-row" style="opacity:0.5">
            <div class="kb-row-name"><div class="skeleton" style="width:180px;height:14px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-type"><div class="skeleton" style="width:40px;height:20px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-status"><div class="skeleton" style="width:60px;height:14px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-chunks"><div class="skeleton" style="width:30px;height:14px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-updated"><div class="skeleton" style="width:70px;height:14px;border-radius:4px;background:var(--bg-hover)"></div></div>
            <div class="kb-row-actions"></div>
        </div>`).join('');
}

function renderKbTable(docs) {
    const kbTableBody = document.getElementById('kbTableBody');
    if (!kbTableBody) return;
    if (!docs.length) { kbTableBody.innerHTML = '<div class="empty-state-small">暂无文档，点击"上传文档"开始使用。</div>'; return; }

    kbTableBody.innerHTML = docs.map(d => {
        const name = d.name || d.doc_name || 'Document';
        const docId = d.filename || d.id || name.replace(/\.(pdf|md|markdown)$/i, '');
        const enhanced = d.enhanced ? '<span style="color:var(--success);font-size:10px;font-weight:600" title="语义增强">✓ 增强</span>' : '';
        const isMd = name.toLowerCase().endsWith('.md') || name.toLowerCase().endsWith('.markdown');
        const fileType = isMd ? 'MD' : 'PDF';
        const typeColor = isMd ? 'purple' : (d.has_parameters ? 'amber' : 'blue');
        const typeLabel = d.has_parameters ? '规格书' : fileType;
        return `
        <div class="kb-row" data-name="${escapeHtml(name).toLowerCase()}" style="cursor:pointer" onclick="openDocDetail('${escapeHtml(docId)}')">
            <div class="kb-row-name"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${isMd ? '#6366F1' : '#2563EB'}" stroke-width="2"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>${escapeHtml(name)}</div>
            <div class="kb-row-type"><span class="kb-type-badge ${typeColor}">${typeLabel}</span></div>
            <div class="kb-row-status"><span class="kb-status-dot" style="background:var(--success)"></span><span style="color:var(--success)">已索引</span> ${enhanced}</div>
            <div class="kb-row-chunks">${d.sections || '-'}</div>
            <div class="kb-row-updated">刚刚</div>
            <div class="kb-row-actions" onclick="event.stopPropagation()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="cursor:pointer" title="打开文件" onclick="window.open('/api/documents/${encodeURIComponent(docId)}/file','_blank')"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="cursor:pointer" title="编辑" onclick="openDocDetail('${escapeHtml(docId)}')"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="cursor:pointer" class="delete" title="删除" onclick="deleteDocument('${escapeHtml(docId)}')"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
            </div>
        </div>`;
    }).join('');
}

// === Document Detail ===
function openDocDetail(docId) {
    currentDocId = docId;
    docDetailDrawer?.classList.add('open');
    fetch(`/api/documents/${encodeURIComponent(docId)}`)
        .then(r => r.json())
        .then(doc => {
            currentDoc = doc;
            document.getElementById('docDetailName').textContent = doc.doc_name || docId;
            document.getElementById('docDetailMeta').textContent = `${doc.structure?.length || 0} 个分块 · 索引 ID: ${docId}`;
            document.getElementById('docDescEdit').value = doc.doc_description_zh || doc.doc_description || '';
            document.getElementById('docChunkCount').textContent = doc.structure?.length || 0;
            renderChunks(doc.structure || []);
            renderSpecData(doc);
        })
        .catch(() => showToast('加载文档详情失败', 'error'));
}

function closeDocDetail() {
    docDetailDrawer?.classList.remove('open');
    currentDocId = null;
}

function renderChunks(chunks) {
    const list = document.getElementById('docChunksList');
    if (!list) return;
    if (!chunks.length) { list.innerHTML = '<div class="empty-state-small">暂无分块数据</div>'; return; }
    list.innerHTML = chunks.map(c => {
        const tags = (c.semantic_tags || []).map(t => `<span class="chunk-tag">${escapeHtml(t)}</span>`).join('');
        const keywords = (c.keywords || []).map(k => `<span class="chunk-keyword">${escapeHtml(k)}</span>`).join('');
        const entities = (c.entities || []).map(e => `<span class="chunk-entity">${escapeHtml(e)}</span>`).join('');
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
            <div class="chunk-field"><label>标题</label><input type="text" value="${escapeHtml(c.title_zh || c.title || '')}" id="chunkTitle_${c.node_id}" disabled></div>
            <div class="chunk-field"><label>页码范围</label><div class="chunk-pages-row"><input type="number" value="${c.start_index}" id="chunkStart_${c.node_id}" disabled><input type="number" value="${c.end_index}" id="chunkEnd_${c.node_id}" disabled></div></div>
            <div class="chunk-field"><label>摘要</label><textarea rows="3" id="chunkSummary_${c.node_id}" disabled>${escapeHtml(c.summary_zh || c.summary || '')}</textarea></div>
            ${keywords ? `<div class="chunk-field"><label>关键词</label><div class="chunk-meta-tags">${keywords}</div></div>` : ''}
            ${entities ? `<div class="chunk-field"><label>实体</label><div class="chunk-meta-tags">${entities}</div></div>` : ''}
            <button class="chunk-save-btn" onclick="saveChunk('${c.node_id}')">保存修改</button>
        </div>`;
    }).join('');
}

function toggleChunkEdit(chunkId) {
    const card = document.getElementById(`chunk_${chunkId}`);
    if (!card) return;
    const editing = card.classList.contains('editing');
    document.querySelectorAll('.chunk-card.editing').forEach(c => { c.classList.remove('editing'); c.querySelectorAll('input,textarea').forEach(el => el.disabled = true); });
    if (!editing) { card.classList.add('editing'); card.querySelectorAll('input,textarea').forEach(el => el.disabled = false); card.querySelector('input')?.focus(); }
}

function saveChunk(chunkId) {
    if (!currentDocId) return;
    const data = {
        title: document.getElementById(`chunkTitle_${chunkId}`)?.value || '',
        summary: document.getElementById(`chunkSummary_${chunkId}`)?.value || '',
        start_index: parseInt(document.getElementById(`chunkStart_${chunkId}`)?.value) || 1,
        end_index: parseInt(document.getElementById(`chunkEnd_${chunkId}`)?.value) || 1,
    };
    fetch(`/api/documents/${encodeURIComponent(currentDocId)}/chunk/${chunkId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(r => { if (!r.ok) throw 0; return r.json(); })
        .then(() => { showToast('分块已保存', 'success'); toggleChunkEdit(chunkId); toggleChunkEdit(chunkId); /* close */ })
        .catch(() => showToast('保存失败', 'error'));
}

function deleteChunk(chunkId) {
    if (!currentDocId) return;
    showConfirm('确认删除此分块？', '删除后此分块将不再参与检索。', 'warning', () => {
        fetch(`/api/documents/${encodeURIComponent(currentDocId)}/chunk/${chunkId}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(r => { showToast('分块已删除', 'success'); document.getElementById(`chunk_${chunkId}`)?.remove(); document.getElementById('docChunkCount').textContent = r.remaining_chunks; })
            .catch(() => showToast('删除失败', 'error'));
    });
}

// Document detail events
document.getElementById('docDetailBack')?.addEventListener('click', closeDocDetail);
document.getElementById('docOpenFileBtn')?.addEventListener('click', () => { if (currentDocId) window.open(`/api/documents/${encodeURIComponent(currentDocId)}/file`, '_blank'); });
document.getElementById('docDescSaveBtn')?.addEventListener('click', () => {
    if (!currentDocId) return;
    fetch(`/api/documents/${encodeURIComponent(currentDocId)}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ doc_description: document.getElementById('docDescEdit')?.value || '' }) })
        .then(() => showToast('文档描述已保存', 'success'))
        .catch(() => showToast('保存失败', 'error'));
});
function deleteDocument(docId) {
    showConfirm('确认删除此文档？', '将同时删除索引文件和原始文件，此操作不可撤销。', 'danger', () => {
        fetch(`/api/documents/${encodeURIComponent(docId)}`, { method: 'DELETE' })
            .then(r => {
                if (!r.ok) throw new Error(r.status);
                return r.json();
            })
            .then(() => {
                showToast('文档已删除', 'success');
                closeDocDetail();
                loadKnowledgeBase();
            })
            .catch((e) => showToast('删除失败：文件可能已不存在', 'error'));
    });
}

document.getElementById('docDeleteBtn')?.addEventListener('click', () => {
    if (currentDocId) deleteDocument(currentDocId);
});
document.getElementById('docReindexBtn')?.addEventListener('click', () => {
    if (!currentDocId) return;
    showConfirm('确认重新索引？', '将使用 AI 重新分析并生成新索引，原有编辑会被覆盖。', 'warning', () => {
        showToast('正在重新索引...');
        fetch(`/api/documents/${encodeURIComponent(currentDocId)}/reindex`, { method: 'POST' })
            .then(r => { if (!r.ok) throw 0; return r.json(); })
            .then(r => { showToast(`重新索引完成，共 ${r.sections} 个分块`, 'success'); openDocDetail(currentDocId); })
            .catch(() => showToast('重新索引失败', 'error'));
    });
});

// KB search
const kbSearch = document.getElementById('kbSearch');
kbSearch?.addEventListener('input', debounce(() => {
    const q = kbSearch.value.toLowerCase();
    document.querySelectorAll('.kb-row').forEach(row => { row.style.display = (row.dataset.name || '').includes(q) ? 'flex' : 'none'; });
}, 200));

// KB tabs
document.querySelectorAll('.page-tab').forEach(tab => {
    tab.addEventListener('click', () => { document.querySelectorAll('.page-tab').forEach(t => t.classList.remove('active')); tab.classList.add('active'); renderKbTable(kbDocs); });
});

// Upload button
document.getElementById('uploadDocBtn')?.addEventListener('click', () => fileUpload.click());

// === Spec Data Rendering ===
function renderSpecData(doc) {
    const section = document.getElementById('specDataSection');
    if (!section) return;

    const sd = doc.spec_data;
    if (!sd || !sd.product_info) {
        section.style.display = 'none';
        return;
    }
    section.style.display = 'block';

    // Product Info
    const pi = sd.product_info || {};
    document.getElementById('specProductInfo').innerHTML = `
        <div class="spec-info-grid">
            <div class="spec-info-item"><span class="spec-label">制造商</span><span class="spec-value">${escapeHtml(pi.manufacturer || '-')}</span></div>
            <div class="spec-info-item"><span class="spec-label">系列</span><span class="spec-value">${escapeHtml(pi.series || '-')}</span></div>
            <div class="spec-info-item"><span class="spec-label">型号</span><span class="spec-value">${escapeHtml(pi.model || '-')}</span></div>
            <div class="spec-info-item"><span class="spec-label">类型</span><span class="spec-value">${escapeHtml(pi.product_type || '-')}</span></div>
            <div class="spec-info-item"><span class="spec-label">技术</span><span class="spec-value">${escapeHtml(pi.cell_type || '-')}</span></div>
            <div class="spec-info-item"><span class="spec-label">功率范围</span><span class="spec-value highlight">${escapeHtml(pi.power_range || '-')}</span></div>
            ${pi.bifacial ? '<div class="spec-info-item"><span class="spec-label">双面</span><span class="spec-value highlight">✓ 双面组件</span></div>' : ''}
        </div>`;

    // === Full spec_table renderer (new universal format) ===
    const specTable = sd.spec_table || {};
    function renderFullSpecTable(st) {
        if (!st || !st.categories || !st.categories.length) return '';
        const models = st.models || [];
        const multiModel = models.length > 1;
        let html = '';
        for (const cat of st.categories) {
            html += `<h4 style="font-size:13px;font-weight:600;color:var(--text-primary);margin:12px 0 6px">${escapeHtml(cat.category)}</h4>`;
            html += '<div class="spec-table-wrap"><table class="spec-table">';
            if (multiModel) {
                html += '<thead><tr><th>参数</th>';
                models.forEach(m => { html += `<th>${escapeHtml(m)}</th>`; });
                html += '</tr></thead>';
            }
            html += '<tbody>';
            for (const p of (cat.params || [])) {
                html += '<tr>';
                html += `<td title="${escapeHtml(p.name_en || '')}">${escapeHtml(p.name)}</td>`;
                if (p.common_value && (!p.values || !p.values.length)) {
                    html += `<td class="num" ${multiModel ? `colspan="${models.length}"` : ''}>${escapeHtml(String(p.common_value))}</td>`;
                } else if (p.values && p.values.length) {
                    p.values.forEach(v => { html += `<td class="num">${escapeHtml(String(v || '-'))}</td>`; });
                } else {
                    if (multiModel) html += `<td colspan="${models.length}">-</td>`;
                    else html += '<td>-</td>';
                }
                html += '</tr>';
            }
            html += '</tbody></table></div>';
        }
        return html;
    }

    // === Legacy multi-model table renderer ===
    function renderSpecTable(title, specsList, commonSpecs, fields) {
        if (!specsList || !specsList.length) return '';
        const models = specsList.map(s => s.model || '');
        // Build table header
        let html = `<h4 style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:8px">${title}</h4>`;
        html += '<div class="spec-table-wrap"><table class="spec-table"><thead><tr><th>参数</th>';
        models.forEach(m => { html += `<th>${escapeHtml(m)}</th>`; });
        html += '</tr></thead><tbody>';
        // Per-model fields
        fields.forEach(([key, label]) => {
            const vals = specsList.map(s => s[key]);
            if (vals.some(v => v != null && v !== '')) {
                html += `<tr><td>${label}</td>`;
                vals.forEach(v => { html += `<td class="num">${escapeHtml(String(v || '-'))}</td>`; });
                html += '</tr>';
            }
        });
        html += '</tbody></table></div>';
        // Common specs below
        if (commonSpecs) {
            const commonFields = Object.entries(commonSpecs).filter(([k,v]) => v && k !== '注意');
            if (commonFields.length) {
                html += '<div class="spec-card" style="width:100%;margin-top:8px">';
                commonFields.forEach(([k, v]) => {
                    html += `<div class="spec-row"><span>${escapeHtml(k)}</span><span>${escapeHtml(String(v))}</span></div>`;
                });
                html += '</div>';
            }
        }
        return html;
    }

    // Battery specs
    const bs = sd.battery_specs || {};
    const bsList = sd.battery_specs_list || [];
    const bsModelFields = [
        ['rated_voltage', '额定电压'], ['rated_energy', '额定能量'], ['usable_energy', '可用能量'],
        ['rated_capacity', '额定容量'], ['cell_configuration', '电芯配置'],
        ['voltage_range', '电压范围'], ['max_charge_current', '最大充电电流'],
        ['max_discharge_current', '最大放电电流'], ['discharge_cutoff_voltage', '放电截止电压'],
        ['charge_cutoff_voltage', '充电截止电压'], ['cycle_life', '循环寿命'],
        ['design_life', '设计寿命'], ['dimensions', '尺寸'], ['weight', '重量'], ['installation', '安装方式'],
    ];
    // Fallback single-model fields
    const bsFields = [
        ['rated_voltage', '额定电压'], ['rated_energy', '额定能量'], ['rated_capacity', '额定容量'],
        ['cell_combination', '电芯组合'], ['cell_configuration', '电芯配置'], ['cycle_life', '循环寿命'],
        ['max_charge_current', '最大充电电流'], ['max_discharge_current', '最大放电电流'],
        ['discharge_cutoff_voltage', '放电截止电压'], ['charge_cutoff_voltage', '充电截止电压'],
        ['charge_temp_range', '充电温度'], ['discharge_temp_range', '放电温度'],
        ['storage_temp_range', '存储温度'], ['ip_class', '防护等级'],
        ['max_parallel', '最大并联数'], ['communication', '通信协议'], ['monitoring', '监控'],
    ];
    const bsRows = bsList.length > 0
        ? renderSpecTable('电池型号参数', bsList, bs, bsModelFields)
        : bsFields.filter(([k]) => bs[k]).map(([k, label]) =>
            `<div class="spec-row"><span>${label}</span><span>${escapeHtml(String(bs[k]))}</span></div>`).join('');

    // Inverter specs
    const inv = sd.inverter_specs || {};
    const invList = sd.inverter_specs_list || [];
    const invModelFields = [
        ['recommend_pv_power', '推荐PV输入功率'], ['rated_ac_output_power', '额定AC输出功率'],
        ['max_ac_output_power', '最大AC输出功率'], ['max_ac_input_power', '最大AC输入功率'],
        ['max_efficiency', '最大效率'], ['euro_efficiency', '欧洲效率'],
        ['backup_output_power', '备用输出功率'], ['backup_output_current', '备用输出电流'],
    ];
    const invFields = [
        ['inverter_type', '逆变器类型'], ['grid_type', '电网类型'],
        ['max_dc_voltage', '最大PV输入电压'], ['min_pv_voltage', '最低PV工作电压'],
        ['startup_voltage', '启动电压'], ['rated_pv_voltage', '额定PV电压'],
        ['mppt_count', 'MPPT路数'], ['strings_per_mppt', '每路组串数'],
        ['rated_ac_voltage', '额定交流电压'], ['ac_voltage_range', '交流电压范围'],
        ['rated_frequency', '额定频率'], ['battery_type', '电池类型'],
        ['battery_voltage', '电池电压'], ['max_charge_discharge_current', '最大充放电电流'],
        ['max_charge_discharge_power', '最大充放电功率'],
        ['protection_features', '保护功能'], ['surge_protection', '浪涌保护'],
        ['dc_switch_fuse', '直流开关/熔断器'],
    ];
    const invRows = invList.length > 0
        ? renderSpecTable('逆变器型号参数', invList, inv, invModelFields)
        : invFields.filter(([k]) => inv[k]).map(([k, label]) =>
            `<div class="spec-row"><span>${label}</span><span>${escapeHtml(String(inv[k]))}</span></div>`).join('');

    // Controller specs (MPPT)
    const ctrl = sd.controller_specs || {};
    const ctrlFields = [
        ['rated_charge_current', '额定充电电流'], ['max_pv_voltage', '最大PV输入电压'],
        ['max_pv_power', '最大PV输入功率'], ['battery_voltage', '电池电压'],
        ['mppt_voltage_range', 'MPPT电压范围'], ['mppt_count', 'MPPT路数'],
        ['max_efficiency', '最大效率'], ['charge_stages', '充电阶段'],
        ['equalization_voltage', '均充电压'], ['float_voltage', '浮充电压'],
        ['self_consumption', '自耗电流'], ['ip_class', '防护等级'],
        ['display', '显示屏'], ['communication', '通信接口'],
    ];
    const ctrlRows = ctrlFields.filter(([k]) => ctrl[k]).map(([k, label]) =>
        `<div class="spec-row"><span>${label}</span><span>${escapeHtml(String(ctrl[k]))}</span></div>`).join('');

    // Protection specs (fuse/breaker)
    const prot = sd.protection_specs || {};
    const protFields = [
        ['device_type', '器件类型'], ['rated_voltage', '额定电压'], ['max_voltage', '最大电压'],
        ['rated_current', '额定电流'], ['breaking_capacity', '分断能力'],
        ['current_ratings', '电流规格'], ['response_time', '响应时间'],
        ['poles', '极数'], ['tripping_curve', '脱扣曲线'],
        ['protection_level', '保护等级'], ['max_discharge_current', '最大放电电流'],
        ['nominal_discharge_current', '标称放电电流'], ['ip_class', '防护等级'],
        ['mounting', '安装方式'], ['strings_count', '组串数'],
    ];
    const protRows = protFields.filter(([k]) => prot[k]).map(([k, label]) =>
        `<div class="spec-row"><span>${label}</span><span>${escapeHtml(String(prot[k]))}</span></div>`).join('');

    // Electrical specs table (solar)
    const stc = sd.electrical_specs_stc || [];
    // Priority: spec_table (universal) > legacy formats
    const fullTableHtml = renderFullSpecTable(specTable);

    if (fullTableHtml) {
        document.getElementById('specElectricalTable').innerHTML = fullTableHtml;
    } else if (ctrlRows) {
        document.getElementById('specElectricalTable').innerHTML = `
            <h4 style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:8px">MPPT控制器参数</h4>
            <div class="spec-card" style="width:100%">${ctrlRows}</div>`;
    } else if (protRows) {
        document.getElementById('specElectricalTable').innerHTML = `
            <h4 style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:8px">保护器件参数</h4>
            <div class="spec-card" style="width:100%">${protRows}</div>`;
    } else if (stc.length > 0) {
        document.getElementById('specElectricalTable').innerHTML = `
            <h4 style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:8px">STC 电气参数</h4>
            <div class="spec-table-wrap">
                <table class="spec-table">
                    <thead><tr><th>型号</th><th>Pmpp (W)</th><th>Vmpp (V)</th><th>Impp (A)</th><th>Voc (V)</th><th>Isc (A)</th><th>效率</th></tr></thead>
                    <tbody>${stc.map(s => `<tr><td>${escapeHtml(s.model||'')}</td><td class="num">${escapeHtml(s.pmpp||'')}</td><td class="num">${escapeHtml(s.vmpp||'')}</td><td class="num">${escapeHtml(s.impp||'')}</td><td class="num">${escapeHtml(s.voc||'')}</td><td class="num">${escapeHtml(s.isc||'')}</td><td class="num">${escapeHtml(s.efficiency||'')}</td></tr>`).join('')}</tbody>
                </table>
            </div>`;
    } else {
        document.getElementById('specElectricalTable').innerHTML = '';
    }

    // Mechanical + Warranty
    const ms = sd.mechanical_specs || {};
    const w = sd.warranty || {};
    const tc = sd.temperature_coefficients || {};
    document.getElementById('specMechanical').innerHTML = `
        <div style="display:flex;gap:16px;flex-wrap:wrap">
            <div class="spec-card"><h4>机械参数</h4>
                ${ms.dimensions ? `<div class="spec-row"><span>尺寸</span><span>${escapeHtml(ms.dimensions)}</span></div>` : ''}
                ${ms.weight ? `<div class="spec-row"><span>重量</span><span>${escapeHtml(ms.weight)}</span></div>` : ''}
                ${ms.cell_count ? `<div class="spec-row"><span>电池片</span><span>${escapeHtml(ms.cell_count)}</span></div>` : ''}
                ${ms.case_material ? `<div class="spec-row"><span>外壳材料</span><span>${escapeHtml(ms.case_material)}</span></div>` : ''}
                ${ms.case_type ? `<div class="spec-row"><span>外壳类型</span><span>${escapeHtml(ms.case_type)}</span></div>` : ''}
                ${ms.glass ? `<div class="spec-row"><span>玻璃</span><span>${escapeHtml(ms.glass)}</span></div>` : ''}
                ${ms.connector ? `<div class="spec-row"><span>连接器</span><span>${escapeHtml(ms.connector)}</span></div>` : ''}
            </div>
            <div class="spec-card"><h4>温度系数</h4>
                ${tc.pmpp ? `<div class="spec-row"><span>Pmpp</span><span class="highlight">${escapeHtml(tc.pmpp)}</span></div>` : ''}
                ${tc.voc ? `<div class="spec-row"><span>Voc</span><span>${escapeHtml(tc.voc)}</span></div>` : ''}
                ${tc.isc ? `<div class="spec-row"><span>Isc</span><span>${escapeHtml(tc.isc)}</span></div>` : ''}
            </div>
            <div class="spec-card"><h4>质保</h4>
                ${w.product_warranty ? `<div class="spec-row"><span>产品质保</span><span>${escapeHtml(w.product_warranty)}</span></div>` : ''}
                ${w.power_warranty ? `<div class="spec-row"><span>功率质保</span><span>${escapeHtml(w.power_warranty)}</span></div>` : ''}
                ${w.first_year_degradation ? `<div class="spec-row"><span>首年衰减</span><span>${escapeHtml(w.first_year_degradation)}</span></div>` : ''}
                ${w.annual_degradation ? `<div class="spec-row"><span>历年衰减</span><span>${escapeHtml(w.annual_degradation)}</span></div>` : ''}
            </div>
        </div>`;

    // Features
    const features = sd.key_features || [];
    document.getElementById('specFeatures').innerHTML = features.length ? `
        <h4 style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:8px">核心卖点</h4>
        <div class="spec-features">${features.map(f => `<span class="spec-feature-tag">${escapeHtml(f)}</span>`).join('')}</div>` : '';
}
