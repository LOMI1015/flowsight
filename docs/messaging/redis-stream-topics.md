# Redis Stream Topic 约定（Phase 2）

## 1. Stream Key

- 默认：`dataset.events`
- 环境变量：`INGESTION_DATASET_INGESTED_STREAM_KEY`

## 2. 生产事件

### `dataset.ingested`

- 生产者：`ingestion-service`
- 触发时机：文件入湖并登记成功后

字段约定：

- `event_type`：固定 `dataset.ingested`
- `event_id`：事件唯一 ID
- `occurred_at`：事件时间（UTC ISO8601）
- `dataset_id`：数据集 ID
- `dataset_version`：数据集版本
- `ingestion_job_id`：接入任务 ID
- `object_key`：对象存储键（raw 路径）
- `file_size`：文件字节大小
- `status`：当前任务状态（`REGISTERED`）

## 3. 消费建议

- consumer group 示例：`processing-group`
- 幂等建议：以 `event_id` 去重，或以 `dataset_id + dataset_version + ingestion_job_id` 去重
- 重试建议：失败消息进入 pending list，达到阈值后转入死信流（DLQ）
