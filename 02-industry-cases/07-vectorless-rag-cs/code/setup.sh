#!/usr/bin/env bash
# 一键 setup:克隆 PageIndex(MIT 开源,Vectify AI) + 配置 .env
set -e

echo "=== Step 1: clone PageIndex ==="
if [ ! -d "PageIndex" ]; then
    git clone https://github.com/VectifyAI/PageIndex.git
    echo "[OK] PageIndex cloned to ./PageIndex/"
else
    echo "[SKIP] PageIndex already exists"
fi

echo ""
echo "=== Step 2: copy .env from example ==="
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "[OK] .env created — 请编辑填入你的 API key"
else
    echo "[SKIP] .env already exists"
fi

echo ""
echo "=== Step 3: install Python dependencies ==="
pip install -r requirements.txt
echo "[OK] dependencies installed"

echo ""
echo "=== Done ==="
echo "下一步:"
echo "  1. 编辑 .env 填入你的 CHATGPT_API_KEY"
echo "  2. 启动:python run.py  (或 docker compose up -d)"
echo "  3. 访问 http://localhost:8000"
