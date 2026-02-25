# 处理任务性能基线（Phase 3）

## 1. 指标定义

- 吞吐：`processed_rows_per_minute`
- 端到端延迟：`ingested_to_succeeded_latency_ms`
- 失败率：`failed_jobs / total_jobs`
- 重试率：`retried_jobs / total_jobs`

## 2. 基线采集口径

- 数据源：`dataset.ingested` 消息 + `ingestion.ingestion_jobs` 状态
- 时间窗：15 分钟滚动窗口
- 样本要求：至少 100 个任务

## 3. 当前目标阈值（初版）

- 吞吐：>= 10,000 rows/min
- P95 延迟：<= 120,000 ms
- 失败率：<= 1%
- 重试率：<= 5%

## 4. 压测建议

- 使用同构 CSV/Excel 文件（小/中/大三档）
- 分别压测：
  - 单 worker
  - 多 worker 并发消费
- 记录资源占用（CPU/MEM/IO）与消息堆积深度

## 5. 结果记录模板

- 测试时间：
- worker 实例数：
- 平均吞吐：
- P95 延迟：
- 失败率：
- 重试率：
- 结论与优化建议：
