#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地同步脚本 — 把 E:\自媒体\ 下的文章批量同步到 GitHub 仓库

用法:
  python sync_to_github.py            # 同步所有
  python sync_to_github.py codex      # 只同步包含 codex 的
  python sync_to_github.py --dry      # 只看变更不推送

需要先在仓库根目录(本仓库)运行。
依赖:git + Python 3.8+
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 文章目录映射:E:\自媒体\<src> → <repo_dst>
MAPPING = {
    "Codex配置教程":       "01-ai-toolstack/01-codex-cli",
    "Codex三端通用":       "01-ai-toolstack/02-codex-multi-platform",
    "Claude全家桶配置":    "01-ai-toolstack/03-claude-suite",
    "opencode配置教程":    "01-ai-toolstack/04-opencode",
    "HermesOpenClaw配置":  "01-ai-toolstack/05-hermes-openclaw",
    "ClaudeAgentSDK教程":  "01-ai-toolstack/06-claude-agent-sdk",
    "家庭绿电助手":         "02-industry-cases/01-home-solar-advisor",
    "合同审查助手":         "02-industry-cases/02-contract-review",
    "企业知识库问答":       "02-industry-cases/03-enterprise-kb-qa",
    "企业客服系统":         "02-industry-cases/04-customer-service",
    "绿电电商客服":         "02-industry-cases/05-solar-ecommerce",
    "二手手机Agent":        "03-cross-industry/01-used-phone-agent",
    "写作脚本Agent":        "03-cross-industry/02-content-creator-agent",
    "Agent行业综述":        "04-survey",
}

SOURCE_ROOT = r"E:\自媒体"
REPO_ROOT = Path(__file__).parent.resolve()

# 公众号引导卡片(插在 article.md 顶部)
WECHAT_CARD = """<div align="center">

📖 **本文同步发布于公众号「实战复盘」** · 每周更新 AI Agent 行业落地实战
🌐 完整代码仓库:[github.com/OnelongX/aiagent](https://github.com/OnelongX/aiagent)
💡 endpoint 选型推荐:[docs/endpoints.md](../../docs/endpoints.md)

</div>

---

"""


def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=True)
    if check and r.returncode != 0:
        print(f"[FAIL] {cmd}\n{r.stderr}")
        sys.exit(1)
    return r.stdout


def has_wechat_card(content):
    return "本文同步发布于公众号" in content[:600]


def inject_card(article_path, output_path):
    """读 article.md,在顶部注入公众号引导卡片,写到目标 README.md"""
    with open(article_path, "r", encoding="utf-8") as f:
        body = f.read()

    if has_wechat_card(body):
        # 已经有了,不重复
        new = body
    else:
        # 卡片放在 H1 后面、引用块前面
        # 找第一个 H1 行
        lines = body.splitlines(keepends=True)
        out = []
        injected = False
        for i, line in enumerate(lines):
            out.append(line)
            if not injected and line.startswith("# "):
                # H1 之后插入卡片
                # 跳过紧跟着的空行/引用块
                injected = True
                # 找下一个非引用、非空行的位置
                j = i + 1
                while j < len(lines) and (
                    lines[j].strip() == "" or
                    lines[j].lstrip().startswith(">") or
                    lines[j].lstrip().startswith("---")
                ):
                    out.append(lines[j])
                    j = j + 1
                # 在这里插入卡片
                out.append("\n" + WECHAT_CARD)
                # 把剩下的复制过去
                out.extend(lines[j:])
                break
        new = "".join(out) if injected else WECHAT_CARD + body

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new)


def sync_one(src_name, dst_subpath, dry=False):
    src_dir = Path(SOURCE_ROOT) / src_name
    dst_dir = REPO_ROOT / dst_subpath

    if not src_dir.is_dir():
        print(f"[SKIP] {src_name} not found")
        return False

    dst_dir.mkdir(parents=True, exist_ok=True)
    (dst_dir / "images").mkdir(exist_ok=True)

    changes = 0

    # README.md(注入公众号卡片)
    article = src_dir / "article.md"
    if article.exists():
        target = dst_dir / "README.md"
        if dry:
            print(f"  [DRY] would update README.md")
        else:
            inject_card(article, target)
            changes += 1

    # gen.py(原样复制)
    gen = src_dir / "gen.py"
    if gen.exists():
        target = dst_dir / "gen.py"
        if not dry:
            shutil.copy2(gen, target)
            changes += 1

    # images
    for png in src_dir.glob("*.png"):
        target = dst_dir / "images" / png.name
        if not dry:
            shutil.copy2(png, target)
            changes += 1

    print(f"  → {dst_subpath} ({changes} files)")
    return changes > 0


def main():
    args = sys.argv[1:]
    dry = "--dry" in args
    if dry:
        args.remove("--dry")
    filter_kw = args[0].lower() if args else None

    print(f"sync_to_github · {'DRY RUN' if dry else 'WRITE'}")
    print(f"source: {SOURCE_ROOT}")
    print(f"repo:   {REPO_ROOT}")
    if filter_kw:
        print(f"filter: {filter_kw}")
    print()

    any_changed = False
    for src, dst in MAPPING.items():
        if filter_kw and filter_kw not in src.lower() and filter_kw not in dst.lower():
            continue
        print(f"[{src}]")
        if sync_one(src, dst, dry):
            any_changed = True

    if dry or not any_changed:
        print("\nDone (no commit).")
        return

    # git status
    print("\n=== git status ===")
    status = run("git status --short", cwd=REPO_ROOT, check=False)
    print(status)
    if not status.strip():
        print("nothing changed.")
        return

    # auto commit
    print("\n=== auto commit ===")
    files_changed = len([l for l in status.splitlines() if l.strip()])
    msg = f"sync: update {files_changed} files from WeChat workflow"
    run("git add -A", cwd=REPO_ROOT)
    run(f'git commit -m "{msg}"', cwd=REPO_ROOT)
    print(f"[OK] committed: {msg}")
    print("\nrun: git push   # 推到远端")


if __name__ == "__main__":
    main()
