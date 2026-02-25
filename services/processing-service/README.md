# processing-service

FlowSight 处理服务（worker 形态）骨架。

## 本地启动

```bash
pip install -r requirements.txt
python -m app.worker.main
```

## 当前能力

- 作为 Redis Stream consumer 运行
- 消费 `dataset.ingested` 事件
- 执行文件解析与目标表入库（从管理服务迁移）
- 输出处理日志并 ACK 消息

## 可配置项

- `PROCESSING_REDIS_URL`（默认 `redis://127.0.0.1:6379/0`）
- `PROCESSING_STREAM_KEY`（默认 `dataset.events`）
- `PROCESSING_CONSUMER_GROUP`（默认 `processing-group`）
- `PROCESSING_CONSUMER_NAME`（默认自动生成）
- `PROCESSING_BLOCK_MS`（默认 `5000`）
- `PROCESSING_BATCH_SIZE`（默认 `10`）
- `PROCESSING_DB_URL`（默认 `postgresql+asyncpg://flowsight:flowsight@127.0.0.1:5432/flowsight`）
- `PROCESSING_DATA_LAKE_ROOT`（默认 `/app/data-lake`）
- `PROCESSING_TARGET_SCHEMA`（默认 `ods`）
- `PROCESSING_TARGET_TABLE`（默认 `ods_doudian_chat_session_all_dd`）
- `PROCESSING_METADATA_SCHEMA`（默认 `ingestion`）
- `PROCESSING_METADATA_DATASET_TABLE`（默认 `datasets`）
- `PROCESSING_METADATA_JOB_TABLE`（默认 `ingestion_jobs`）
- `PROCESSING_MAX_RETRY_COUNT`（默认 `3`）
- `PROCESSING_RETRY_BACKOFF_BASE_SECONDS`（默认 `2`）
- `PROCESSING_RETRY_BACKOFF_MAX_SECONDS`（默认 `60`）
- `PROCESSING_DLQ_STREAM_KEY`（默认 `dataset.events.dlq`）

## 重试策略

- 处理失败后触发重试，最大次数由 `PROCESSING_MAX_RETRY_COUNT` 控制。
- 退避算法为指数退避：
  - `wait = base * 2^(retry_count-1)`
  - 最大等待不超过 `PROCESSING_RETRY_BACKOFF_MAX_SECONDS`
- 重试消息会携带 `retry_count` 字段并重新写回 stream。

## 状态回写（metadata）

- 回写目标：`ingestion` schema（可配置）
- 状态流转：
  - 上传登记后：`PENDING`
  - 开始处理：`RUNNING`
  - 处理成功：`SUCCEEDED`
  - 处理失败：`FAILED`

## DLQ 与人工补偿

- 超过最大重试次数的消息会写入 DLQ stream（默认 `dataset.events.dlq`）。
- 手工补偿（重放）命令：

```bash
# 重放指定消息
python -m app.worker.compensate --message-id "<dlq-message-id>"

# 重放前 N 条消息
python -m app.worker.compensate --count 10
```
