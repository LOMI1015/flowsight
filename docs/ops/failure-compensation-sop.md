# 失败处理与补偿 SOP（Phase 3）

## 1. 适用场景

- `processing-service` 消费 `dataset.ingested` 失败
- 消息超过最大重试次数，进入 DLQ：`dataset.events.dlq`

## 2. 处理步骤

1. **确认失败原因**
   - 查看 processing worker 日志
   - 查看 metadata：`ingestion.ingestion_jobs.last_error`
2. **修复根因**
   - 数据问题：修正原始文件或映射配置
   - 环境问题：数据库/Redis/网络恢复
3. **执行补偿重放**
   - 单条：
     - `python -m app.worker.compensate --message-id "<dlq-message-id>"`
   - 批量：
     - `python -m app.worker.compensate --count 10`
4. **验证结果**
   - `ingestion_jobs.status` 由 `FAILED` 变为 `RUNNING/SUCCEEDED`
   - 目标表数据按预期落库

## 3. 回滚策略

- 如果补偿后持续失败：
  - 暂停批量补偿
  - 保留 DLQ 消息
  - 仅做单条验证性重放

## 4. 审计要求

- 记录补偿操作者、时间、消息 ID、结果
- 记录根因与修复动作，形成复盘条目
