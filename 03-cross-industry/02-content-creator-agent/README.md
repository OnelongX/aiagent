# 自媒体写作 + 脚本 Agent —— Claude 当编辑 / 风格守门员 / 复盘师

> 实战复盘 · AI 工具栈 · 跨行业平移 第 2 篇
>
> 把"自己的写作流程"做成 Agent。
> 一致性 + 不重复 + 越写越准 = 真正的护城河。

---


<div align="center">

<a href="https://github.com/OnelongX/aiagent">
<img src="../../assets/wechat-qrcode.png" width="160" alt="公众号:iamonelong" />
</a>

📖 **本文同步发布于公众号「实战复盘」** · 微信号:`iamonelong`
🌐 [完整代码仓库 · github.com/OnelongX/aiagent](https://github.com/OnelongX/aiagent)
💡 endpoint 选型:[docs/livetoken.md](../../docs/livetoken.md)

</div>

---

## I. 一个 meta 视角

这一篇有个很特别的视角:**我手动跑过去 17 次的工作流,就是这个 Agent 的雏形** ——

> 选题 → 大纲 → 正文 → PIL 配图 → 标题摘要 → WeChat 推送

把这个流程拆开,就是一个完整的自媒体 Agent。**用 Claude 当大脑,Hooks 当编辑红线,Subagent 当各工种**。

**本文从选题到发布的工作流,正是文章描述的 Agent —— 写出这篇文章本身,就是它运行的第一个证据。**

---

## II. 两类内容 · 不同节奏

| 维度 | 公众号长文 | 短视频脚本 |
|---|---|---|
| 长度 | 2000-5000 字 | 30s - 3min(口播 200-1500 字) |
| 结构 | 罗马数字章节 / 表格 / 代码块 | 钩子(3s)→ 主线 → 转折 → 结尾 |
| 节奏 | 段落清晰 · 信息密度高 | 单句信息密度低 · 节奏感强 |
| 视觉 | PIL 配图 5 张 | 分镜 + B-roll + 字幕 |
| 发布 | WeChat MP API | 抖音 / 视频号 / B 站 |

**关键**:**两类不能共用 prompt**。长文用"沉稳硬核"调性,脚本必须"短句 + 钩子 + 反差"。

---

## III. 整体架构 · 7 段流水线

```
选题  →  大纲  →  写作  →  视觉  →  多平台改写  →  发布  →  数据回流
miner    outline  writer   visual   adapter         publisher  analyst
```

每段对应一个 Subagent。最关键的创新:

**把"自己"做成 Agent 的输入** —— 历史文章库 + 文风 embedding + 已用过的选题,全部喂给 Agent,确保新内容**不重复、风格一致、接续主线**。

---

## IV. 25 工具 · 5 类

### A. 选题挖掘

```python
@tool("fetch_industry_news", "拉行业资讯",
      {"industry": str, "days": int})
async def fetch_industry_news(args):
    # NewsAPI / 雪球 / 36氪 / X 列表
    return await news_api.fetch(...)

@tool("search_my_history", "查自己历史 + 去重",
      {"topic": str})
async def search_my_history(args):
    # 自己的 Qdrant 索引(过往 17 篇)
    hits = qdrant.search(args["topic"], filter={"author": "me"})
    return {"existing": hits, "is_duplicate": len(hits) > 0}

@tool("mining_comments", "挖评论区找选题",
      {"article_id": str, "min_likes": int})
async def mining_comments(args):
    comments = wx_api.get_comments(args["article_id"])
    return cluster_comments(comments)

@tool("analyze_competitor", "竞品账号选题分析", {...})
@tool("hot_keyword_trend", "热度趋势(微信指数/百度指数)", {...})
```

### B. 长文写作

```python
@tool("generate_outline", "生成大纲",
      {"topic": str, "target_length": int,
       "style": str, "must_cover": list, "persona": str})
async def generate_outline(args):
    return call_claude_opus(
        system=f"你是【{args['persona']}】栏目的总编。",
        prompt=outline_prompt(args))

@tool("write_article", "正文撰写",
      {"outline": dict, "style_examples": list})
async def write_article(args):
    """传入 3 篇风格样本 → 风格控制"""
    return call_claude_sonnet(
        system=style_lock_prompt(args["style_examples"]),
        prompt=write_prompt(args))

@tool("polish_article", "润色 · 句式平衡", {...})
@tool("generate_title_candidates", "10 个候选标题 A/B", {...})
@tool("generate_digest", "摘要 ≤120 字", {...})
@tool("generate_keywords", "关键词", {...})
```

### C. 视频脚本

```python
@tool("generate_video_outline", "视频大纲",
      {"topic": str, "duration_sec": int, "platform": str})
async def generate_video_outline(args):
    structure = {
        "douyin":    ["3s 钩子", "主线", "反转", "CTA"],
        "shipinhao": ["5s 钩子", "主线", "升华"],
        "bilibili":  ["开场", "铺垫", "主线", "细节", "结尾"],
    }[args["platform"]]
    return call_claude(...)

@tool("generate_video_script", "口播稿(含分镜)",
      {"outline": dict, "duration_sec": int})
async def generate_video_script(args):
    return {
        "scenes": [
            {"time": "0-3s", "voiceover": "...",
             "visual": "...", "subtitle": "..."},
        ]
    }

@tool("estimate_duration", "估时(中文 4.5 字/秒)",
      {"voiceover": str})
async def estimate_duration(args):
    chars = count_chinese(args["voiceover"])
    return {"seconds": chars / 4.5,
            "fit": chars / 4.5 <= TARGET_DURATION}

@tool("generate_teleprompter", "提词器版本(换气符)", {...})
@tool("generate_storyboard", "分镜稿", {...})
```

### D. 视觉工具

```python
@tool("generate_pil_code", "生成 PIL 配图代码",
      {"article": str, "n": int, "style": str})
async def generate_pil_code(args):
    """Claude 看完文章后,自动出 N 张图的 Python 代码
       这就是我一直手写的 gen.py"""
    return call_claude(
        system=PIL_TEMPLATE_PROMPT,
        prompt=f"为这篇文章生成 {args['n']} 张 1080×600 配图。"
               f"主色调避开最近 5 篇 · 区分识别度。",
        examples=load_recent_gen_py(3))   # ← 自己学自己

@tool("render_images", "执行 PIL 代码 → PNG",
      {"code": str, "out_dir": str})
async def render_images(args):
    exec_safe(args["code"])
    return list_pngs(args["out_dir"])

@tool("generate_cover_prompt", "封面 prompt(MJ/SD)", {...})
```

### E. 多平台 + 发布

```python
@tool("adapt_xhs", "改写小红书版", {...})
@tool("adapt_x_thread", "改写 X thread", {...})
@tool("adapt_zhihu", "改写知乎", {...})
@tool("publish_wechat", "推 WeChat 草稿", {...})
@tool("publish_xhs", "推小红书", {...})
@tool("post_x_thread", "发 X thread", {...})
@tool("publish_video_draft", "传抖音/视频号", {...})
```

---

## V. 8 个 Subagent · 流水线

```python
agents = {
    "topic-miner": AgentDefinition(
        prompt="拉行业资讯 + 竞品 + 评论挖选题 → "
               "search_my_history 去重 → 给 5 个候选标注重复风险。",
        tools=["fetch_industry_news", "search_my_history",
               "mining_comments", "analyze_competitor",
               "hot_keyword_trend"],
        model="haiku"),

    "outline-writer": AgentDefinition(
        prompt="风格匹配(读历史 3 篇样本) → generate_outline。"
               "罗马数字章节 + 表格 + 代码块。",
        tools=["search_my_history", "generate_outline"],
        model="opus"),     # ← 重思考用 Opus

    "article-writer": AgentDefinition(
        prompt="write_article → polish_article 至少 1 轮。"
               "字数偏差 > 15% 重写。",
        tools=["write_article", "polish_article"],
        model="sonnet"),

    "video-writer": AgentDefinition(
        prompt="generate_video_outline → generate_video_script → "
               "estimate_duration · 超时回头改 → "
               "generate_storyboard + generate_teleprompter。",
        tools=["generate_video_outline", "generate_video_script",
               "estimate_duration", "generate_storyboard",
               "generate_teleprompter"],
        model="sonnet"),

    "visual-coder": AgentDefinition(
        prompt="generate_pil_code → render_images。"
               "主色调避开最近 5 篇。"
               "渲染失败 → 修 Python 错重试,最多 3 次。",
        tools=["generate_pil_code", "render_images"],
        model="sonnet"),

    "multi-channel-adapter": AgentDefinition(
        prompt="一稿多发:adapt_xhs / adapt_x_thread / adapt_zhihu。"
               "每个平台调性不同,不能直接复制。",
        tools=["adapt_xhs", "adapt_x_thread", "adapt_zhihu"],
        model="sonnet"),

    "publisher": AgentDefinition(
        prompt="publish_wechat → publish_xhs → post_x_thread。"
               "每平台 5 分钟间隔(防限流)。",
        tools=["publish_wechat", "publish_xhs", "post_x_thread"],
        model="haiku"),

    "analyst": AgentDefinition(
        prompt="T+1 拉数据:阅读 / 留存 / 转发 / 涨粉。"
               "对比历史 P30。低于 P30 → 落 DSAT 队列。",
        tools=["get_article_stats", "compare_to_history",
               "write_dsat_review"],
        model="sonnet"),
}
```

---

## VI. 风格控制 · 三层守门

**直接告诉 Claude"写得像我"是没用的**。风格不是描述出来的,是**对比**出来的。

### 第 1 层:Few-shot 例子(基础)

每次 `write_article` 传 3 篇风格样本,让 Claude 模仿。

### 第 2 层:Style Embedding(进阶)

把过去 17 篇做成 embedding 库,新文写完后跟历史风格做相似度打分:

```python
@tool("check_style_consistency", "风格一致性打分",
      {"new_article": str})
async def check_style_consistency(args):
    new_emb = embed(args["new_article"])
    historical = load_my_embeddings()
    score = cosine(new_emb, historical.mean(axis=0))
    return {"score": score, "below_threshold": score < 0.75}
```

低于阈值 → 回头改。

### 第 3 层:Persona Lock(根本)

写一份**自己的 prompt 档案**,固化在 `system_prompt`,不动:

```markdown
# 行业观察 · Persona
- 称呼自己"我"
- 不喊口号,数据先行
- 罗马数字章节,表格密集
- 每章末尾 1 句金句收尾
- 禁词:绝对、肯定、必将、革命性
- 偏好词:基本面、纪律、边界、闭环
- 收尾必带"升华"或"总结"段
- 落款:实战复盘 · 关键词列表 · 本文仅供学习参考
```

---

## VII. 6 条 Hooks · 编辑红线

```python
hooks = {
  # 1. 选题重复 → 拦
  "PostToolUse:search_my_history":
      block if is_duplicate,

  # 2. 标题 > 64 字 → 改(WeChat 限制)
  "PostToolUse:generate_title_candidates":
      rewrite if any(len(t) > 64 for t in titles),

  # 3. 摘要 > 120 字 → 改
  "PostToolUse:generate_digest":
      rewrite if len(digest) > 120,

  # 4. 风格一致性 < 0.75 → 打回
  "PostToolUse:write_article":
      regenerate if style_score < 0.75,

  # 5. 视频时长偏差 > 15% → 打回
  "PostToolUse:generate_video_script":
      regenerate if abs(actual - target) / target > 0.15,

  # 6. 敏感词监控
  "PostToolUse:write_article":
      block_or_replace if forbidden_words_hit,
}
```

---

## VIII. 多平台改写 · 调性差异

| 平台 | 调性 | 长度 | 配图 | 标签 |
|---|---|---|---|---|
| 公众号 | 深度 + 结构 | 2000-5000 字 | 5 张 PIL 图 | 文末关键词 |
| 小红书 | 种草 + emoji | 500-1500 字 | 5-9 张图 | #话题 5-10 |
| X / Twitter | 短句 + 数据 | 1500 字 thread | 1-2 图 | hashtag 2-3 |
| 知乎 | 干货 + 引证 | 3000+ 字 | 嵌入式 | 话题 3-5 |
| B 站 / 视频号 | 口播 + 字幕 | 视频 30s-10min | 分镜稿 | 标签 + 封面 |

**每平台专门 prompt** —— `adapt_xhs` 不是简单截短,是重写。

---

## IX. 数据回流 · DSAT 闭环

```python
# T+1 数据拉取
stats = get_article_stats(yesterday_articles)
for s in stats:
    if s.read_count < historical_p30:
        analyst.review(s, reason="低于 P30")
        possible_causes = [
            "标题太软",  "选题撞车",  "发布时段错",
            "封面图弱", "首图太抽象",
        ]
```

**DSAT 闭环是真正的护城河** —— 写得多不重要,写得**越来越准**重要。

---

## X. 3 周落地

| 周 | 目标 | 交付 |
|---|---|---|
| **W1** | 长文 + PIL 图 自动化 | topic-miner + outline + writer + visual + publish-wechat |
| **W2** | 多平台改写 | adapt_xhs / x_thread / zhihu + publisher |
| **W3** | 视频脚本 + 数据回流 | video-writer + storyboard + analyst + DSAT |

**关键**:W1 不上数据回流也行。先把长文流水线跑通,产出稳定后再加分析。

---

## XI. 四个工程坑

### 坑 1:Claude 写久了"塌方"

写第 N 篇时,Claude 会不自觉模仿前几篇的开头、结尾、用词。风格一致是好事,**自我重复就是坏事**。

对策:每周强制注入 3 篇风格变体样本(高温度生成或人工写),避免陷入局部最优。

### 坑 2:配图代码语法错 → 整篇卡住

PIL 代码偶尔写错(中文字体路径 / API 误用)。**沙箱执行 + 异常自修复**:

```python
for attempt in range(3):
    try:
        exec_safe(code)
        break
    except Exception as e:
        code = call_claude(f"修这个错: {e}\n\n原代码:\n{code}")
```

### 坑 3:多平台同步发 → 限流封号

抖音 / 小红书 / X 都有"短时间多平台同内容"识别,会限流。**强制 5-30 分钟间隔 + 每平台改写差异 > 30%**。

### 坑 4:选题去重不能只看标题

标题不同但内容雷同,读者一看就烦。**用 embedding 去重,不用标题字面**。本文跟历史 cosine > 0.85 → 直接打回。

---

## XII. 升华

| 维度 | 手动写 | Agent 写 |
|---|---|---|
| 周期 | 一篇 4-6 小时 | **30 分钟** |
| 一稿多发 | 各平台手改 | **自动改写** |
| 选题 | 凭灵感 | **资讯 + 评论 + 竞品综合挖** |
| 风格 | 全靠自觉 | **embedding 打分 + persona 锁** |
| 数据回流 | 看个大概 | **DSAT 闭环 + 历史对比** |

**核心认知**:自媒体写作 Agent 真正的护城河,不是"会写",是 **"会保持一致 + 不重复 + 越写越准"**。

- 一致性靠 **persona lock + 风格 embedding 校验**
- 不重复靠 **历史 KB 向量去重**
- 越写越准靠 **DSAT 闭环 + T+1 数据回流**

**Claude 不只是写手 —— 还要当自己的编辑、风格守门员、数据复盘师**。一个角色搞不定,得用 Subagent 分工。

---

## XIII. Meta 时刻

这篇文章从选题到发布的工作流,正是文章描述的 Agent。

写出这篇文章本身,就是它运行的第一个证据。

下一步,自动化:
- 选题不再手动喂,从订阅源 + 评论 + 趋势自动捞
- 配图不再每次写 gen.py,Claude 看完文章自动出
- 一稿多发不再手改,改写工具自动跑
- 数据不再凭感觉看,DSAT 自动落队列

**用 Agent 写"如何用 Agent 写文章"的文章** —— 这是工程化最干净的自证。

---

实战复盘 · AI 工具栈 · 跨行业平移 第 2 篇
关键词:Claude Agent SDK · 自媒体写作 · 视频脚本 · 风格 embedding · DSAT 闭环 · 多平台改写 · Persona Lock
本文仅供学习参考。
