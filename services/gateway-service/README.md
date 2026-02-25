# gateway-service

FlowSight 网关最小实现（Nginx）。

## 已接入路由

- `/api/v1/ingestion/` -> `ingestion-service:9201`

## 本地运行（compose）

```bash
cd services/gateway-service
docker compose up -d
```

## 健康检查

- `GET http://localhost:8080/healthz`
