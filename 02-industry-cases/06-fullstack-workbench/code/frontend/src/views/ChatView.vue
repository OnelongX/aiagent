<template>
  <div class="chat">
    <h2>💬 聊天</h2>
    <div class="messages">
      <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
        <div class="role">{{ m.role === 'user' ? '我' : 'AI' }}</div>
        <div class="content">{{ m.content }}</div>
        <div v-if="m.refs && m.refs.length" class="refs">
          <div class="refs-title">📎 引用来源</div>
          <div v-for="(r, j) in m.refs" :key="j" class="ref-item">
            [{{ j + 1 }}] {{ r.title }} (片段 #{{ r.chunk_index }} · 相似度 {{ (r.score * 100).toFixed(1) }}%)
          </div>
        </div>
      </div>
    </div>
    <div class="input-area">
      <textarea
        v-model="input"
        @keydown.enter.exact.prevent="send"
        placeholder="问点什么... (Enter 发送, Shift+Enter 换行)"
        :disabled="loading"
      />
      <button @click="send" :disabled="loading || !input.trim()">
        {{ loading ? '思考中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const input = ref('')
const messages = ref([])
const loading = ref(false)

async function send() {
  if (!input.value.trim()) return
  const userMsg = input.value.trim()
  messages.value.push({ role: 'user', content: userMsg })
  input.value = ''
  loading.value = true

  // 占位 AI 回复
  const aiMsg = { role: 'assistant', content: '', refs: [] }
  messages.value.push(aiMsg)

  try {
    const history = messages.value
      .slice(0, -1)
      .map(m => ({ role: m.role, content: m.content }))

    const resp = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMsg, history }),
    })

    if (!resp.ok) throw new Error('HTTP ' + resp.status)

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const data = line.slice(6)
        if (data === '[DONE]') break
        try {
          const obj = JSON.parse(data)
          if (obj.type === 'references') {
            aiMsg.refs = obj.data
          } else if (obj.type === 'delta') {
            aiMsg.content += obj.data
          }
        } catch (e) {
          console.warn('parse error', e)
        }
      }
    }
  } catch (e) {
    aiMsg.content = '❌ ' + e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat { max-width: 900px; margin: 0 auto; }
h2 { margin-bottom: 16px; color: #1e293b; }
.messages { display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; min-height: 60vh; }
.msg { padding: 14px 18px; border-radius: 12px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.msg.user { background: #eff6ff; align-self: flex-end; max-width: 70%; }
.msg.assistant { background: #fff; max-width: 85%; }
.role { font-size: 12px; color: #64748b; margin-bottom: 6px; }
.content { white-space: pre-wrap; line-height: 1.7; color: #1e293b; }
.refs { margin-top: 12px; padding-top: 12px; border-top: 1px dashed #cbd5e1; font-size: 12px; }
.refs-title { color: #64748b; margin-bottom: 6px; }
.ref-item { color: #475569; padding: 2px 0; }
.input-area { display: flex; gap: 10px; }
textarea {
  flex: 1; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px;
  resize: vertical; min-height: 80px; font-family: inherit; font-size: 14px;
}
button {
  padding: 12px 24px; background: #fbbf24; color: #1e293b; border: none;
  border-radius: 8px; font-weight: 600; cursor: pointer; transition: background 0.15s;
}
button:hover:not(:disabled) { background: #f59e0b; }
button:disabled { background: #cbd5e1; cursor: not-allowed; }
</style>
