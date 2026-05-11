#!/usr/bin/env bash
set -e

echo "=== Step 1: copy .env from example ==="
if [ ! -f "backend/.env" ]; then
    cp .env.example backend/.env
    echo "[OK] backend/.env created — 请编辑填入你的 LLM_API_KEY"
else
    echo "[SKIP] backend/.env already exists"
fi

echo ""
echo "=== Step 2: install dependencies ==="
cd backend && pip install -r requirements.txt && cd ..

echo ""
echo "=== Done ==="
echo "下一步:"
echo "  1. 编辑 backend/.env 填 LLM_API_KEY"
echo "  2. 启动:cd backend && python run.py"
echo "  3. 或:docker compose up -d"
echo "  4. 访问 http://localhost:8081"
