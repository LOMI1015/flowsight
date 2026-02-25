# 工作流状态机文档（Phase 3）

## 1. 范围

- 编排服务：`workflow-orchestrator-service`
- 处理服务：`processing-service`
- 元数据落点：`ingestion.datasets`、`ingestion.ingestion_jobs`

## 2. 状态定义

- `PENDING`：任务已登记，待处理
- `RUNNING`：处理服务已开始执行
- `SUCCEEDED`：处理成功完成
- `FAILED`：处理失败（可重试或进入 DLQ）

## 3. 状态流转

```text
PENDING -> RUNNING -> SUCCEEDED
                  \-> FAILED
FAILED --(retry)--> PENDING
FAILED --(exceed max retry)--> DLQ
DLQ --(manual compensate)--> PENDING
```

## 4. 触发点与责任方

- `ingestion-service`：
  - 上传登记成功后写入 `PENDING`
  - 发布 `dataset.ingested`
- `processing-service`：
  - 消费事件时更新 `RUNNING`
  - 成功后更新 `SUCCEEDED`
  - 失败时更新 `FAILED` 并触发重试/入 DLQ

## 5. 一致性约束

- 每次状态变更必须回写 `updated_at`
- 重试时递增 `retry_count`
- 错误信息截断存储到 `last_error`（避免超长字段）
