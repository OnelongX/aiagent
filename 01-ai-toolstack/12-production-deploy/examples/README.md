# Examples · Production Agent 配套脚本

| 文件 | 用途 |
|---|---|
| `litellm-config.yaml`       | LiteLLM 多 endpoint fallback + cache + budget |
| `canary_deploy.sh`          | 5 步灰度发布脚本(5% → 100% · 自动 rollback) |
| `budget_middleware.py`      | FastAPI 中间件:RPS + token + 成本三层限流 + 全局告警 |
| `Dockerfile.prod`           | 生产级镜像(多阶段 / 非 root / tini / healthcheck) |

## 跑通顺序

```bash
# 1. 起 LiteLLM Router(配 fallback)
docker run -p 4000:4000 -v $PWD/litellm-config.yaml:/config.yaml \
    ghcr.io/berriai/litellm:main \
    --config /config.yaml

# 2. 构建 Docker 镜像
docker build -f Dockerfile.prod -t agent-api:v1.2.0 .

# 3. 推到 registry · K8s 拉
docker tag agent-api:v1.2.0 your-registry/agent-api:v1.2.0
docker push your-registry/agent-api:v1.2.0

# 4. apply manifests
kubectl apply -f ../manifests/

# 5. 灰度上线 v1.3.0
./canary_deploy.sh v1.3.0
```

## 关键设计要点

### LiteLLM Router

- **3 个 endpoint per model**(主备备)· livetoken / 官方 / Bedrock
- **跨模型 fallback** · claude 全挂 → GPT → Gemini
- **不要 fallback 私有 LLM 到公有云** · 涉密任务宁可失败也别泄密
- **Redis 缓存** · prompt caching 省 75% 钱(配合 Gemini Caches API)

### budget_middleware

- **3 层防御** · RPS / token / 成本各自独立
- **后置计费** · 调完 LLM 才知道 token 数 · 用响应 header 传递
- **全局降级** · 成本爆炸自动设 `emergency:cheap_model` flag · 10 分钟自动恢复

### canary_deploy.sh

- **5% → 25% → 50% → 100%** · 4 档逐步放量
- **每档 10 分钟观察 + 跑 smoke eval**
- **任何一档失败 trap ERR → 自动回 0%**
- **smoke eval 接 #11 examples/07_full_pipeline.py**

### Dockerfile.prod

- **多阶段** · 镜像从 1.2GB 压到 380MB
- **非 root** · uid 10001 · K8s SecurityContext 要求
- **tini** · 处理 SIGTERM · 配合 K8s graceful shutdown
- **timeout-graceful-shutdown 60s** · 等当前 LLM 调用完
