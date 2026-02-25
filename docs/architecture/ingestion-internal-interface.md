# Ingestion 领域内部接口文档（Phase 1）

## 1. 对外接口（单体内领域入口）

### `POST /api/v1/ingestion/datasets/upload`

- 鉴权：需要登录态（复用 admin 鉴权）
- 参数（`multipart/form-data`）：
  - `file`: 上传文件
  - `dataset_id`: 数据集标识（幂等键组成）
  - `dataset_version`: 版本号（默认 `v1`）
- 返回：
  - `code/msg/success/time/error_code`
  - `data`（文件路径、文件名、访问地址）

## 2. 领域应用服务接口

### `IngestionService.ingest_upload_file(...)`

- 输入：
  - `request`
  - `file`
  - `query_db`
  - `current_user`
  - `dataset_id`
  - `dataset_version`
- 行为：
  1. 幂等检查（Redis：`dataset_id + dataset_version`）
  2. 文件落盘并记录 `sys_upload`
  3. 调用文件解析并批量入库
  4. 发布 `dataset.ingested` 事件
  5. 缓存幂等结果并返回

## 3. 事件接口

### 发布事件：`dataset.ingested`

- 事件模型：`EventMessage`
- 关键字段：
  - `event_id`
  - `event_type`
  - `occurred_at`
  - `trace_id`
  - `producer`
  - `dataset_id`
  - `dataset_version`
  - `payload`

### 订阅处理

- 启动时通过 `register_ingestion_event_handlers()` 注册处理器。
- 当前默认处理器为日志消费（可平滑替换为编排逻辑）。

## 4. 幂等接口定义

- 键：`ingestion:idempotency:{dataset_id}:{dataset_version}`
- 锁：`{key}:lock`
- 语义：
  - 命中结果缓存：直接返回历史处理结果
  - 命中处理中锁：拒绝重复处理并提示稍后重试
  - 首次成功：写入结果缓存（TTL 24h）

## 5. 兼容说明

- 旧接口 `POST /api/v1/admin/common/upload` 仍可用。
- 旧接口内部已委派到 `IngestionService`，保证行为一致且便于平滑迁移。
