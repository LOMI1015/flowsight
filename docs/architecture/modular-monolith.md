# FlowSight 模块化单体说明（Phase 1）

## 1. 目标

在不拆分进程的前提下，把单体应用改造为“按领域装配、按应用层调用”的结构，为后续微服务拆分降低迁移成本。

## 2. 当前目录分层（后端）

- 领域装配层：`backend/domains/*`
  - `admin`、`bi`、`generator`、`ingestion`、`task`、`shared`
- 路由统一注册：`backend/domains/route_registry.py`
- 入口：`backend/server.py`（仅负责生命周期与装配，不直连具体控制器清单）

## 3. 应用层约束

- Controller 不直接依赖 DAO。
- Controller 统一从 `domains/<domain>/application/services.py` 引用应用服务。
- DAO 访问限制在 service/application 层内部。

## 4. 已落地关键点

- 路由装配从 `server.py` 抽离到各领域 `route_registry.py`。
- `module_admin/module_bi/module_generator` 控制器已切换到应用层导入。
- 新增 `ingestion` 领域，承接“上传 + 解析 + 入库”链路。
- 新增进程内事件总线（`domains/shared/events`）。
- ingestion 上传链路已接入幂等机制（`dataset_id + dataset_version`）。

## 5. 版本与路径

- admin: `/api/v1/admin/*`
- bi: `/api/v1/bi/*`
- generator: `/api/v1/generator/*`
- ingestion: `/api/v1/ingestion/*`

## 6. 下一步建议

- 把 ingestion 的表写入与事件投递进一步解耦为独立应用服务对象。
- 用契约测试固定 `domains/*/application/services.py` 的输入输出。
- 在 Phase 2 按既有领域边界直接提升为独立服务进程。
