# K8s Manifests · Production Agent 完整模板

## 文件清单

| 文件 | 用途 |
|---|---|
| `namespace.yaml` | 命名空间 |
| `deployment.yaml` | **3 副本 · 滚动 0 中断 · 三件套健康检查** |
| `service.yaml` | ClusterIP · Blue-Green 切流量 |
| `hpa.yaml` | HPA v2 · 复合指标 |
| `keda-scaledobject.yaml` | KEDA · 从 Prometheus 拉自定义指标 |
| `pdb.yaml` | PDB · `minAvailable=2` 维护期不中断 |
| `configmap.yaml` | 配置 + Secret · **钉死模型小版本** |
| `ingress.yaml` | 主流量 + Canary(权重灰度) |

## 部署顺序

```bash
# 1. 命名空间
kubectl apply -f namespace.yaml

# 2. 配置(改 secrets 真实 key 后)
kubectl apply -f configmap.yaml

# 3. 应用
kubectl apply -f deployment.yaml -f service.yaml -f pdb.yaml

# 4. 入口
kubectl apply -f ingress.yaml

# 5. 自动伸缩(选其一)
kubectl apply -f hpa.yaml             # 简单 · K8s 内置
kubectl apply -f keda-scaledobject.yaml   # 强大 · 需要 KEDA + Prometheus
```

## 验证

```bash
# 1. pod 起来了
kubectl get pods -n agent -l app=agent-api

# 2. 健康检查通了
kubectl exec -n agent <pod> -- curl localhost:8000/api/health

# 3. HPA 工作
kubectl get hpa -n agent

# 4. 压测看伸缩
hey -z 60s -c 50 https://api.example.com/api/agent
kubectl get pods -n agent -w
```

## 关键决策

- **`maxUnavailable: 0`** · 滚动期间 0 中断(不接受半秒不可用)
- **`minAvailable: 2`** · 节点维护至少留 2 个
- **`startupProbe failureThreshold: 30`** · SDK 初始化最长 150 秒(30 × 5s)
- **`terminationGracePeriodSeconds: 60`** · 等当前 LLM 调用完
- **`preStop sleep 10`** · 给 LB 时间从服务列表摘掉

## 灰度发布操作

```bash
# 1. 部署 v2(独立 Deployment + Service)
sed 's/v1.2.0/v1.3.0/g; s/agent-api/agent-api-v2/g; s/version: v1/version: v2/g' \
    deployment.yaml | kubectl apply -f -

# 2. 灰度 5%
kubectl apply -f ingress.yaml   # canary 默认 5%

# 3. 观察 30 分钟 + 跑 smoke eval
python /eval/run_eval.py --smoke --canary

# 4. 升级到 25% → 50% → 100%
kubectl annotate ingress agent-api-canary \
    nginx.ingress.kubernetes.io/canary-weight=25 --overwrite

# 5. 出问题 · 立刻回 0
kubectl annotate ingress agent-api-canary \
    nginx.ingress.kubernetes.io/canary-weight=0 --overwrite
```
