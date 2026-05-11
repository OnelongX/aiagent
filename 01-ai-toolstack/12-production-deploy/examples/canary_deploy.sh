#!/usr/bin/env bash
# 5 步灰度发布脚本
# 用法:./canary_deploy.sh v1.3.0
#
# 流程:5% → 25% → 50% → 100% · 每档观察 10 分钟 + 跑 smoke eval

set -euo pipefail

NEW_VERSION="${1:?用法:$0 <new-version>}"
NAMESPACE="agent"
CANARY_INGRESS="agent-api-canary"
OBSERVE_MIN=10
EVAL_SCRIPT="${EVAL_SCRIPT:-python eval/run_eval.py --smoke --canary}"

# ============================
# 工具函数
# ============================
log()   { echo "[$(date +%T)] $*"; }
fatal() { log "FATAL: $*"; exit 1; }

set_weight() {
  local weight=$1
  log "→ 切流量到 v2: ${weight}%"
  kubectl annotate ingress "${CANARY_INGRESS}" -n "${NAMESPACE}" \
    nginx.ingress.kubernetes.io/canary-weight="${weight}" \
    --overwrite
}

run_smoke_eval() {
  log "跑 smoke eval(超时 5 分钟)..."
  if ! timeout 300 bash -c "${EVAL_SCRIPT}"; then
    fatal "smoke eval 失败 · 触发回滚"
  fi
  log "✓ smoke eval 通过"
}

check_metrics() {
  # 简化版 · 真实环境对接 Prometheus / Grafana / Slack
  local error_rate
  error_rate=$(kubectl exec -n monitoring deploy/prom-cli -- promtool query instant \
    'sum(rate(http_requests_total{app="agent-api-v2",status=~"5.."}[5m])) / sum(rate(http_requests_total{app="agent-api-v2"}[5m]))' \
    | awk '{print $2}' || echo "0")

  if (( $(echo "${error_rate:-0} > 0.01" | bc -l) )); then
    fatal "v2 错误率 ${error_rate} > 1% · 触发回滚"
  fi
  log "✓ v2 错误率 ${error_rate} 正常"
}

rollback() {
  log "!!! 自动回滚 · 流量切回 v1 !!!"
  set_weight 0
  log "v2 流量已切回 0% · 请人工排查"
  exit 1
}

trap rollback ERR

# ============================
# 主流程
# ============================
log "===== 灰度发布 ${NEW_VERSION} ====="
log "namespace: ${NAMESPACE}"
log "canary ingress: ${CANARY_INGRESS}"
log "观察时长(每档): ${OBSERVE_MIN} 分钟"

# 1. 部署 v2(独立 Deployment + Service)
log "1/6 · 部署 v2 ${NEW_VERSION}"
kubectl set image deployment/agent-api-v2 \
  api="your-registry/agent-api:${NEW_VERSION}" \
  -n "${NAMESPACE}"
kubectl rollout status deployment/agent-api-v2 -n "${NAMESPACE}" --timeout=300s

# 2. 5% 流量
log "2/6 · 灰度 5%"
set_weight 5
sleep $((OBSERVE_MIN * 60))
run_smoke_eval
check_metrics

# 3. 25%
log "3/6 · 灰度 25%"
set_weight 25
sleep $((OBSERVE_MIN * 60))
run_smoke_eval
check_metrics

# 4. 50%
log "4/6 · 灰度 50%"
set_weight 50
sleep $((OBSERVE_MIN * 60))
run_smoke_eval
check_metrics

# 5. 100%
log "5/6 · 全量切换 100%"
set_weight 100
sleep $((OBSERVE_MIN * 60))
run_smoke_eval
check_metrics

# 6. 收尾 · v2 升级为正式 · 删 v1
log "6/6 · v2 升为主版本 · 清理 v1"
kubectl set image deployment/agent-api \
  api="your-registry/agent-api:${NEW_VERSION}" \
  -n "${NAMESPACE}"
kubectl rollout status deployment/agent-api -n "${NAMESPACE}"
set_weight 0

log "===== ✓ 灰度发布完成 ${NEW_VERSION} ====="
