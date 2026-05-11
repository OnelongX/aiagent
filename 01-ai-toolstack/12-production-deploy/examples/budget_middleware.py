"""Production-grade budget / 限流 / 限额中间件

3 层防御:
1. 单用户 RPS 限流(每分钟 30 次)
2. 单用户日 token 限额(100 万)
3. 单用户日成本限额(¥100)
+ 全局成本告警(¥1000/h 触发降级)

依赖:fastapi redis
"""
import os
import time
import json
import asyncio
import urllib.request
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
import redis.asyncio as aioredis


# ===================================================================
# 配置(来自 ConfigMap · 见 manifests/configmap.yaml)
# ===================================================================
MAX_RPS_PER_USER    = int(os.getenv("MAX_REQUESTS_PER_USER_PER_MIN", "30"))
MAX_TOKENS_PER_USER = int(os.getenv("MAX_TOKENS_PER_USER_PER_DAY", "1000000"))
MAX_COST_PER_USER   = float(os.getenv("MAX_COST_PER_USER_PER_DAY_RMB", "100"))
GLOBAL_ALERT_RMB    = float(os.getenv("GLOBAL_COST_ALERT_PER_HOUR_RMB", "1000"))
SLACK_WEBHOOK       = os.getenv("SLACK_WEBHOOK_URL", "")
EMERGENCY_FLAG_KEY  = "emergency:cheap_model"


# ===================================================================
# 初始化
# ===================================================================
app = FastAPI()
r:   aioredis.Redis = None


@app.on_event("startup")
async def startup():
    global r
    r = await aioredis.from_url(
        os.getenv("REDIS_URL", "redis://redis:6379/0"),
        decode_responses=True,
    )


# ===================================================================
# 限流中间件
# ===================================================================
@app.middleware("http")
async def budget_middleware(request: Request, call_next):
    # 静态路径跳过
    if not request.url.path.startswith("/api/agent"):
        return await call_next(request)

    user_id = request.headers.get("X-User-Id") or "anonymous"
    today   = datetime.now().strftime("%Y-%m-%d")
    minute  = int(time.time() // 60)
    hour    = int(time.time() // 3600)

    # ---------- 1. RPS 限流 ----------
    rps_key = f"rps:{user_id}:{minute}"
    rps     = await r.incr(rps_key)
    await r.expire(rps_key, 70)
    if rps > MAX_RPS_PER_USER:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests · 限 {MAX_RPS_PER_USER}/min",
            headers={"Retry-After": "60"},
        )

    # ---------- 2. token 限额 ----------
    tokens_key = f"tokens:{user_id}:{today}"
    tokens     = int(await r.get(tokens_key) or 0)
    if tokens > MAX_TOKENS_PER_USER:
        raise HTTPException(
            status_code=429,
            detail=f"Daily token budget exceeded · {tokens}/{MAX_TOKENS_PER_USER}",
        )

    # ---------- 3. 成本限额 ----------
    cost_key = f"cost:{user_id}:{today}"
    cost     = float(await r.get(cost_key) or 0)
    if cost > MAX_COST_PER_USER:
        raise HTTPException(
            status_code=402,
            detail=f"Daily budget exceeded · ¥{cost:.2f}/{MAX_COST_PER_USER}",
        )

    # ---------- 4. 全局降级检查 ----------
    if await r.get(EMERGENCY_FLAG_KEY) == "1":
        # 告诉下游应用切便宜模型
        request.state.use_cheap_model = True

    # ---------- 调下游 ----------
    response = await call_next(request)

    # ---------- 5. 后置更新 ----------
    used_tokens = int(response.headers.get("X-Tokens-Used", "0"))
    used_cost   = float(response.headers.get("X-Cost-RMB", "0"))
    if used_tokens:
        await r.incrby(tokens_key, used_tokens)
        await r.expire(tokens_key, 86400)
    if used_cost:
        await r.incrbyfloat(cost_key, used_cost)
        await r.expire(cost_key, 86400)
        # 累全局
        global_key = f"cost:global:{hour}"
        await r.incrbyfloat(global_key, used_cost)
        await r.expire(global_key, 7200)

    return response


# ===================================================================
# 后台:全局成本告警 · 每分钟跑
# ===================================================================
async def check_global_budget_loop():
    while True:
        try:
            hour = int(time.time() // 3600)
            cost = float(await r.get(f"cost:global:{hour}") or 0)
            if cost > GLOBAL_ALERT_RMB:
                # 1. 设置紧急 flag(下游应用切便宜模型)
                await r.set(EMERGENCY_FLAG_KEY, "1", ex=600)

                # 2. Slack 告警
                if SLACK_WEBHOOK:
                    msg = {
                        "text": f"🚨 AI 成本爆炸:¥{cost:.0f}/h(阈值 ¥{GLOBAL_ALERT_RMB})· 已切换便宜模型 10 分钟"
                    }
                    req = urllib.request.Request(
                        SLACK_WEBHOOK,
                        data=json.dumps(msg).encode(),
                        headers={"Content-Type": "application/json"},
                    )
                    urllib.request.urlopen(req)
        except Exception as e:
            print(f"check_global_budget error: {e}")

        await asyncio.sleep(60)


@app.on_event("startup")
async def start_loop():
    asyncio.create_task(check_global_budget_loop())


# ===================================================================
# 在你的 LLM 调用代码里
# ===================================================================
"""
from openai import OpenAI

@app.post("/api/agent/chat")
async def chat(request: Request, body: ChatRequest):
    # 中间件已经检查 budget · 这里专心干活
    model = "cheap" if getattr(request.state, "use_cheap_model", False) else "claude-sonnet"

    client = OpenAI(base_url="http://litellm:4000")
    resp = client.chat.completions.create(
        model=model,
        messages=body.messages,
    )

    # 算成本(简化 · 真实用 LiteLLM 自带 cost_per_token)
    cost = resp.usage.total_tokens / 1000 * 0.024     # ¥/1K token
    return JSONResponse(
        content={"answer": resp.choices[0].message.content},
        headers={
            "X-Tokens-Used": str(resp.usage.total_tokens),
            "X-Cost-RMB":    f"{cost:.4f}",
        },
    )
"""
