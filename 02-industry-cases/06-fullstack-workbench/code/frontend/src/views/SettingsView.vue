<template>
  <div class="settings">
    <h2>⚙️ 设置</h2>

    <section>
      <h3>当前配置</h3>
      <div class="kv-list">
        <div class="kv"><span>App</span><code>{{ config.app_name }} v{{ config.app_version }}</code></div>
        <div class="kv"><span>LLM Endpoint</span><code>{{ config.llm_api_base }}</code></div>
        <div class="kv"><span>Model</span><code>{{ config.llm_model }}</code></div>
        <div class="kv"><span>Embedding</span><code>{{ config.embedding_model }}</code></div>
      </div>
      <p class="hint">
        改配置请编辑 <code>backend/.env</code>(参考 <code>.env.example</code>),改完重启 backend。
      </p>
    </section>

    <section>
      <h3>请求日志(最近 50 条)</h3>
      <button @click="loadLogs">🔄 刷新</button>
      <table>
        <thead>
          <tr><th>时间</th><th>方法</th><th>路径</th><th>状态</th><th>耗时(ms)</th></tr>
        </thead>
        <tbody>
          <tr v-for="(l, i) in logs.slice().reverse()" :key="i">
            <td class="ts">{{ l.timestamp }}</td>
            <td><span :class="['method', l.method.toLowerCase()]">{{ l.method }}</span></td>
            <td class="path">{{ l.path }}</td>
            <td><span :class="['status', statusClass(l.status)]">{{ l.status }}</span></td>
            <td>{{ l.duration_ms }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const config = ref({})
const logs = ref([])

function statusClass(s) {
  if (s >= 500) return 'err'
  if (s >= 400) return 'warn'
  return 'ok'
}

async function loadConfig() {
  const resp = await axios.get('/api/settings/config')
  config.value = resp.data
}

async function loadLogs() {
  // 关键纪律:前后端字段名统一 timestamp,不是 time
  const resp = await axios.get('/api/settings/logs', { params: { limit: 50 } })
  logs.value = resp.data.logs
}

onMounted(async () => {
  await loadConfig()
  await loadLogs()
})
</script>

<style scoped>
.settings { max-width: 900px; margin: 0 auto; }
h2 { margin-bottom: 16px; color: #1e293b; }
h3 { margin: 0 0 12px; color: #334155; font-size: 16px; }
section { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.kv-list { display: flex; flex-direction: column; gap: 8px; }
.kv { display: flex; justify-content: space-between; padding: 8px 12px; background: #f8fafc; border-radius: 6px; }
.kv span { color: #64748b; }
.kv code { color: #1e293b; font-family: monospace; font-size: 13px; }
.hint { margin-top: 12px; color: #64748b; font-size: 13px; }
.hint code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
button { padding: 8px 16px; background: #e2e8f0; color: #334155; border: none; border-radius: 6px; cursor: pointer; margin-bottom: 12px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }
th { background: #f1f5f9; color: #64748b; font-size: 12px; }
.ts { font-family: monospace; color: #64748b; font-size: 12px; }
.method { padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.method.get { background: #ecfdf5; color: #047857; }
.method.post { background: #eff6ff; color: #1d4ed8; }
.path { font-family: monospace; color: #1e293b; }
.status { padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.status.ok { background: #ecfdf5; color: #047857; }
.status.warn { background: #fef3c7; color: #92400e; }
.status.err { background: #fef2f2; color: #b91c1c; }
</style>
