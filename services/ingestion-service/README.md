# ingestion-service

FlowSight 第一个独立服务骨架（Phase 2 起点）。

## 目录

- `app/main.py`：FastAPI 入口
- `app/api/routes.py`：基础路由
- `app/schemas/dataset.py`：领域请求/响应模型
- `requirements.txt`：服务依赖

## 本地启动

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9201 --reload
```

或使用 compose：

```bash
docker compose up -d
```

## 当前接口

- `GET /healthz`：健康检查
- `POST /datasets`：创建数据集
- `POST /datasets/{dataset_id}/upload`：上传文件
- `GET /datasets/{dataset_id}/ingestions/{ingestion_job_id}`：查询接入任务状态

## 上传语义

- 上传接口只负责**入湖与登记**：
  - 原始文件落盘到 `data-lake/raw/...`
  - 写入接入任务登记（状态 `REGISTERED`）
- 不在 ingestion-service 内做解析、清洗、转换等重处理逻辑。

说明：当前为最小可运行实现，状态存储为进程内内存；后续会替换为数据库与消息队列实现。

## Redis Streams 事件

- 上传登记成功后发布事件：`dataset.ingested`
- 默认 stream key：`dataset.events`
- 可配置环境变量：
  - `INGESTION_REDIS_URL`（默认 `redis://127.0.0.1:6379/0`）
  - `INGESTION_DATASET_INGESTED_STREAM_KEY`（默认 `dataset.events`）
  - `INGESTION_EVENT_PUBLISH_REQUIRED`（默认 `false`，为 `true` 时发布失败将返回 503）

## 数据库与 Schema

- 服务启动时自动初始化数据库表结构。
- PostgreSQL 下会自动创建并使用独立 schema：`ingestion`（可通过 `INGESTION_DB_SCHEMA` 覆盖）。
- 可配置环境变量：
  - `INGESTION_DB_URL`（例如 `postgresql+asyncpg://user:pass@host:5432/dbname`）
  - `INGESTION_DB_SCHEMA`（默认 `ingestion`）
