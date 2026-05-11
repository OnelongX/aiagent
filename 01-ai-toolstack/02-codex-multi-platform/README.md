# Codex 三端通用配置 —— 一份 config.toml,跑遍 CLI / 桌面 app / VS Code 插件

> **TL;DR**:Codex 其实不只是 CLI。它有 **3 个端**:**CLI / 桌面 app / VS Code 插件**。**3 个端共享同一份 `~/.codex/config.toml`** —— 你配一次,3 个端全部生效,不用在每个端的设置面板里重新配 API key。这是 Codex 一个**很多人没意识到的福利**。


<div align="center">

📖 **本文同步发布于公众号「实战复盘」** · 每周更新 AI Agent 行业落地实战
🌐 完整代码仓库:[github.com/OnelongX/aiagent](https://github.com/OnelongX/aiagent)
💡 endpoint 选型推荐:[docs/endpoints.md](../../docs/endpoints.md)

</div>

---

承接上一篇《Codex CLI 配置完整教程》。

上一篇讲了 CLI 的配置。这一篇讲一个**更实用的事**:**那一份配置文件,3 个端都用**。

---

## 一、Codex 其实有 3 个端

很多人知道 Codex CLI,但不知道**官方还做了另外 2 个端**:

| 端 | 形态 | 适合 |
|---|---|---|
| **Codex CLI** | 终端命令行 | 服务器 / 远程开发 / 重度 prompt |
| **Codex 桌面 app** | GUI 客户端(独立窗口) | 离开 IDE 的快速对话 / 不想敲命令 |
| **VS Code 插件** | IDE 内嵌侧边栏 | 写代码同时随时呼出 AI |

**3 个端都是 OpenAI 官方维护的**——不是第三方包装,功能 + 模型选择基本一致。

---

## 二、关键真相:3 个端共享一份配置

这是上一篇没明说的事。

```
~/.codex/config.toml
```

**这份文件 = 3 个端的共同配置中枢**。

也就是说:

- 你在 CLI 里配的 `base_url = "https://livetoken.top"` →
- **桌面 app 启动时直接读到** →
- **VS Code 插件加载时也直接读到**

**不用在每个端的"设置 → API"面板里重新填 key**。

---

## 三、为什么这件事很重要

**实际开发中,3 个端常常切换使用**:

- 写 PR commit 信息 → 在 CLI 里跑
- 调试一个奇怪的 bug → 桌面 app 里慢慢聊
- 写代码 / 重构 / 改注释 → VS Code 插件里实时

**如果配置不共享**,你要做的事:
1. CLI 配一次
2. 桌面 app 设置面板里再配一次
3. VS Code 插件设置里又配一次
4. 升级 API key 的时候,**3 个地方都要改**
5. 切换 base_url 的时候,**3 个地方都要改**

**3 端通用 = 维护成本 / 3**。

---

## 四、配置共享的 4 个具体收益

| 收益 | 解释 |
|---|---|
| **改一次 base_url · 3 端同步** | 切换第三方提供商时,只改 1 个文件 |
| **API key 集中管理** | 全部走 `OPENAI_API_KEY` 环境变量,3 端都读 |
| **模型偏好统一** | reasoning_effort 在 3 个端表现一致 |
| **沙箱策略一致** | sandbox_mode 在 3 端都生效,不会出现"VS Code 里 AI 能写文件,CLI 里不能"的混乱 |

**这是企业 / 团队部署时的福利** —— 团队管理员维护 1 份 config 模板,所有人 3 端通用。

---

## 五、3 个端各自的特点

虽然共享配置,但 3 个端**各有侧重**:

### Codex CLI

- **最快进入交互**:`cd 项目目录 → codex` → 几秒就到对话
- **支持完整 plan 模式**:复杂任务 AI 会先列计划再执行
- **服务器友好**:SSH 远程开发场景必备
- **缺点**:终端 UI 看长输出有点累

### Codex 桌面 app

- **聊天体验最好**:像 ChatGPT 桌面版那样,可以随时 alt-tab 出来用
- **可以打开多个会话**:每个项目一个标签
- **复制 / 粘贴方便**:屏幕大,看推理摘要舒服
- **缺点**:跟 IDE 切换有点割裂

### VS Code 插件

- **侧边栏内嵌**:写代码时不用切窗
- **直接选中代码 → 问 AI**:右键 / 快捷键秒发
- **看 diff 友好**:AI 改的代码直接 in-line 看
- **缺点**:VS Code 之外的项目用不上

---

## 六、3 端使用场景对照

| 场景 | 推荐端 |
|---|---|
| 写一个全新模块 / 重构 | **VS Code 插件** |
| 调一个奇怪的 bug,想跟 AI 慢慢聊 | **桌面 app** |
| 服务器上看日志 / 远程开发 | **CLI** |
| 跑一个 plan 模式任务,要 AI 全自动 | **CLI** |
| 写文档 / README / 注释 | **VS Code 插件** |
| 周末非工作时间,随手问个技术问题 | **桌面 app** |
| 团队脚本化任务(自动化 PR review 等) | **CLI** |

**1 份配置 + 3 个端 = 各种场景都覆盖**。

---

## 七、配置一致性的实战收益

我自己实测下来,**3 端通用最爽的一点**:

**调试同一个问题时可以来回切端**。

比如:
- VS Code 插件里 AI 改代码 → 改完发现需要跑测试 → 切到 CLI 用 plan 模式让 AI 自己跑测试 + 看结果
- CLI 里 AI 跑出报错 → 复制报错内容到桌面 app 慢慢聊
- 桌面 app 聊出方案 → 切回 VS Code 让 AI 直接改代码

**整个过程上下文不变(用同一个 base_url 同一个 model 同一个 reasoning_effort)**。

如果不通用,3 个端可能用不同模型 / 不同 provider,**对话上下文会割裂**。

---

## 八、还没配过的从这里开始

如果你完全没配过 Codex:

1. 先看上一篇《Codex CLI 配置完整教程》—— 把 `~/.codex/config.toml` 配好
2. 然后下载桌面 app(OpenAI 官网) + 装 VS Code 插件
3. 启动 3 个端,会发现**不需要再配第二次**

**前置条件**:`~/.codex/config.toml` 配置好 + 环境变量 `OPENAI_API_KEY` 设了。

---

## 九、已经配过 CLI 的读者:0 改动迁移

如果你已经在 CLI 里跑通:

1. 下载桌面 app → 启动 → 自动读 config → 直接用
2. VS Code 插件 → 装上 → 自动读 config → 直接用

**不用任何额外配置**。

我配好的那份指向 livetoken.top 的 config,在 3 个端都生效——**没改任何东西**。

---

## 升华

> 一份 config.toml · 3 个端通用 ·
>
> **这是 Codex 体系的隐藏福利**。

很多文档没专门讲这个事——大家以为每个端都要单独配。

**实际上 OpenAI 设计 Codex 时就把"配置中枢"放在 `~/.codex/` 目录** —— 故意让 3 个端共享。

知道了这个事:
- 切换 base_url 只改 1 个文件
- 团队管理员维护 1 份模板,所有人 3 端通用
- 工作流可以无缝切端 + 上下文一致

**省下来的不是时间,是注意力**。

---

## 留言钩子

评论区聊一下:

- 你 3 个端都装了吗?
- 哪个端用得最多?
- 有没有发现 3 端**配置不一致**的坑?
- 还想看 Cursor / Cline / Continue 的多端共享教程吗?

**遇到问题留言**,我看到会回。

---

## FAQ

**Q1:Codex 桌面 app 和 VS Code 插件在哪下载?**
都在 OpenAI 官网 → Codex 产品页。桌面 app 有 Mac / Windows / Linux 三版;VS Code 插件在 VS Code Marketplace 搜 `Codex` 安装。

**Q2:3 端通用是不是真的不用配第二次?**
是。前提是 `~/.codex/config.toml` 已经配好,且 `OPENAI_API_KEY` 环境变量设好。**3 个端启动时都读这两个**。

**Q3:能不能让 3 个端用不同的 base_url?**
可以,但要在 config 里配多 provider,然后 3 个端启动时通过命令行参数 / 设置面板**指定不同 provider**。但默认情况下 3 端共享同一个 `model_provider`。

**Q4:VS Code 插件 vs 桌面 app vs CLI,哪个最强?**
**功能一致 · 形态不同**。CLI 最适合自动化 / 脚本化;桌面 app 适合慢慢聊;VS Code 插件适合在 IDE 里实时改代码。**3 个一起用,工作流最完整**。

**Q5:配置共享后,API 调用会重复计费吗?**
不会。**3 个端是独立的请求方,但用同一个 API key**——你的实际消耗是"3 个端实际请求的总和",不是 ×3。

**Q6:我用 livetoken.top 是 3 端都能用吗?**
能。我自己配了 livetoken,3 个端都跑通了。**因为 OpenAI 兼容协议是统一的**——只要 base_url 是 OpenAI 兼容的,3 个端都按 OpenAI 协议发请求。

**Q7:能在 Mac 上跑桌面 app + Linux 服务器跑 CLI 吗?**
能,但配置不会自动同步——本地 Mac 的 `~/.codex/config.toml` 跟服务器是两份独立的。**可以用 dotfiles / git 同步配置目录**。

**Q8:Cursor / Cline / Continue 也支持类似的"多端通用配置"吗?**
不一样。**Cursor 是独立产品**(自己的配置);**Cline / Continue 是 VS Code 插件**(各自配置)。**3 端通用是 Codex 体系特有的福利**。

---

*实战复盘 · Codex CLI 进阶 · 配置一次 · 3 端通用*

*关键词:Codex、Codex CLI、Codex 桌面 app、Codex VS Code 插件、config.toml、多端配置、OpenAI 官方*

*本文仅供学习参考*
