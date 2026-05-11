<template>
  <div class="kb">
    <h2>📚 知识库</h2>

    <section class="ingest">
      <h3>添加文档</h3>
      <input v-model="title" placeholder="文档标题" />
      <input v-model="category" placeholder="分类(可选)" />
      <textarea v-model="content" placeholder="文档内容(粘贴 Markdown / 纯文本)" rows="8" />
      <button @click="ingest" :disabled="loading || !title.trim() || !content.trim()">
        {{ loading ? '处理中...' : '添加到知识库' }}
      </button>
      <div v-if="message" :class="['msg', messageType]">{{ message }}</div>
    </section>

    <section class="list">
      <h3>已收录文档({{ documents.length }})</h3>
      <button class="refresh" @click="loadList">🔄 刷新</button>
      <div v-if="documents.length === 0" class="empty">还没有文档,先添加一个吧</div>
      <table v-else>
        <thead>
          <tr><th>标题</th><th>分类</th><th>doc_id</th><th>时间</th></tr>
        </thead>
        <tbody>
          <tr v-for="d in documents" :key="d.doc_id">
            <td>{{ d.title }}</td>
            <td><span class="tag">{{ d.category }}</span></td>
            <td class="docid">{{ d.doc_id.slice(0, 8) }}…</td>
            <td>{{ d.created_at }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="search">
      <h3>检索测试</h3>
      <input v-model="query" placeholder="输入查询..." @keydown.enter="search" />
      <button @click="search">检索</button>
      <div v-if="hits.length" class="hits">
        <div v-for="(h, i) in hits" :key="i" class="hit">
          <div class="hit-head">
            <strong>{{ h.title }}</strong>
            <span class="score">{{ (h.score * 100).toFixed(1) }}%</span>
          </div>
          <div class="hit-body">{{ h.content }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const title = ref('')
const category = ref('')
const content = ref('')
const loading = ref(false)
const message = ref('')
const messageType = ref('info')
const documents = ref([])
const query = ref('')
const hits = ref([])

async function ingest() {
  loading.value = true
  message.value = ''
  try {
    const resp = await axios.post('/api/knowledge/ingest', {
      title: title.value,
      content: content.value,
      category: category.value || null,
    })
    message.value = `✅ 已添加 (doc_id: ${resp.data.doc_id.slice(0, 8)}…)`
    messageType.value = 'success'
    title.value = ''
    content.value = ''
    category.value = ''
    await loadList()
  } catch (e) {
    message.value = '❌ ' + (e.response?.data?.detail || e.message)
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}

async function loadList() {
  try {
    const resp = await axios.get('/api/knowledge/list')
    documents.value = resp.data.documents
  } catch (e) {
    console.error(e)
  }
}

async function search() {
  if (!query.value.trim()) return
  try {
    const resp = await axios.get('/api/knowledge/search', { params: { q: query.value } })
    hits.value = resp.data.hits
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadList)
</script>

<style scoped>
.kb { max-width: 900px; margin: 0 auto; }
h2 { margin-bottom: 16px; color: #1e293b; }
h3 { margin: 0 0 12px; color: #334155; font-size: 16px; }
section { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
input, textarea {
  width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1;
  border-radius: 6px; margin-bottom: 10px; font-family: inherit; font-size: 14px;
}
textarea { resize: vertical; }
button {
  padding: 10px 20px; background: #fbbf24; color: #1e293b; border: none;
  border-radius: 6px; cursor: pointer; font-weight: 600;
}
button:hover:not(:disabled) { background: #f59e0b; }
button:disabled { background: #cbd5e1; cursor: not-allowed; }
.refresh { background: #e2e8f0; color: #334155; margin-left: 8px; font-weight: 400; }
.msg { margin-top: 12px; padding: 10px 14px; border-radius: 6px; font-size: 14px; }
.msg.success { background: #ecfdf5; color: #047857; }
.msg.error { background: #fef2f2; color: #b91c1c; }
.empty { color: #94a3b8; padding: 20px; text-align: center; }
table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #e2e8f0; }
th { background: #f1f5f9; color: #64748b; font-weight: 600; font-size: 12px; }
.tag { background: #eff6ff; color: #1d4ed8; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.docid { font-family: monospace; color: #64748b; font-size: 12px; }
.hits { margin-top: 14px; display: flex; flex-direction: column; gap: 10px; }
.hit { padding: 12px; background: #f8fafc; border-left: 3px solid #fbbf24; border-radius: 6px; }
.hit-head { display: flex; justify-content: space-between; margin-bottom: 6px; }
.score { color: #047857; font-weight: 600; font-size: 12px; }
.hit-body { font-size: 13px; color: #475569; line-height: 1.6; }
</style>
