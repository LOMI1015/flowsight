# ingestion-service OpenAPI 说明

服务地址示例：`http://localhost:9201`

OpenAPI JSON:

- `GET /openapi.json`

Swagger UI:

- `GET /docs`

Redoc:

- `GET /redoc`

## 核心接口

### `POST /datasets`

- 说明：创建数据集
- 请求体：
  - `dataset_name` (string, required)
  - `dataset_version` (string, optional, default `v1`)
- 响应：
  - `dataset_id`
  - `dataset_version`
  - `status` (`CREATED`)

### `POST /datasets/{dataset_id}/upload`

- 说明：上传文件并登记接入任务（只入湖与登记，不做重处理）
- 请求：
  - path: `dataset_id`
  - form-data: `file`
- 幂等策略：
  - 幂等键：`dataset_id + dataset_version + original_filename`
  - 命中已存在任务时直接返回历史任务结果
- 响应：
  - `ingestion_job_id`
  - `status` (`REGISTERED`)
  - `object_key`
  - `file_size`

### `GET /datasets/{dataset_id}/ingestions/{ingestion_job_id}`

- 说明：查询接入任务状态
- 响应：
  - `dataset_id`
  - `ingestion_job_id`
  - `status`
  - `object_key`
  - `created_at` / `updated_at`
