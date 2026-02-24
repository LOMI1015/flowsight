# FlowSight 配置管理规范（Phase 0 - Step 3）

## 1. 目标

- 统一环境变量管理方式，避免配置散落在单体与前端文件中。
- 按服务拆分 `.env` 模板，支持后续微服务独立部署。
- 明确“共享配置”与“服务私有配置”的边界，降低误配风险。

## 2. 目录约定

- 共享模板：`env-templates/.env.shared.example`
- 服务模板：`env-templates/.env.<service-name>.example`
- 实际运行文件（不入库）：`.env.<service-name>.<env>`，例如 `.env.iam-admin-service.dev`

## 3. 使用流程

- 复制共享模板并填充基础设施连接信息。
- 复制目标服务模板并填充服务私有变量。
- 合并加载顺序建议：`shared -> service`，同名变量以后者覆盖前者。

## 4. 命名规范

- 使用 `UPPER_SNAKE_CASE`。
- 共享连接参数统一前缀：
  - `DB_*`（数据库）
  - `REDIS_*`（缓存）
  - `MINIO_*`（对象存储）
  - `OTEL_*`（可观测性）
- 服务私有参数使用语义前缀，如 `JWT_*`、`CORS_*`、`RATE_LIMIT_*`。

## 5. 边界规则

- 禁止将密钥、密码、Token 直接提交到仓库。
- 禁止不同服务复用同一 `.env` 文件。
- 禁止服务读取不属于自身边界的私有变量。
- 新增配置项必须同步更新对应 `.env.<service>.example`。

## 6. 当前模板映射

- `iam-admin-service`：认证、RBAC、系统配置、系统任务控制面
- `bi-query-service`：读模型查询
- `generator-service`：代码生成元数据与模板渲染
- `task-worker-service`：任务执行函数运行时
- `ingestion-service`：接入与入湖
- `workflow-orchestrator-service`：编排与重试控制
- `processing-service`：处理流水线执行
- `storage-metadata-service`：数据集元数据与版本
- `labeling-service`：标注任务生命周期
- `notification-service`：消息通知
- `gateway-service`：统一入口与路由转发
- `frontend-web`：前端构建与 API 地址
