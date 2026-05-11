<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">AI Workbench</div>
      <nav>
        <router-link to="/chat" class="nav-item">💬 聊天</router-link>
        <router-link to="/knowledge" class="nav-item">📚 知识库</router-link>
        <router-link to="/settings" class="nav-item">⚙️ 设置</router-link>
      </nav>
      <div class="footer">
        <a href="https://github.com/OnelongX/aiagent" target="_blank">GitHub</a>
      </div>
    </aside>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; }
.layout { display: flex; height: 100vh; }
.sidebar {
  width: 220px; background: #0f172a; color: #cbd5e1;
  display: flex; flex-direction: column; padding: 20px 0;
}
.brand { padding: 0 20px 24px; color: #fbbf24; font-size: 18px; font-weight: 700; }
nav { flex: 1; }
.nav-item {
  display: block; padding: 12px 20px; color: #cbd5e1;
  text-decoration: none; transition: background 0.15s;
}
.nav-item:hover { background: #1e293b; color: #fff; }
.router-link-active { background: #1e293b; color: #fbbf24; }
.footer { padding: 16px 20px; border-top: 1px solid #1e293b; font-size: 12px; }
.footer a { color: #64748b; text-decoration: none; }
.main { flex: 1; overflow: auto; background: #f8fafc; padding: 24px; }
</style>
