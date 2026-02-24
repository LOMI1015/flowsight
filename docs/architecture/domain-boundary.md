# FlowSight 领域边界（Phase 0 基线版）

> 目的：基于当前前后端代码，明确 `admin / bi / task / generator` 的边界与 owner（表、接口、事件），作为后续拆分微服务的基线。

## 1. 边界梳理范围

- 后端：`backend/module_admin`、`backend/module_bi`、`backend/module_generator`、`backend/module_task`
- 前端：`frontend/src/views`、`frontend/src/router/modules`、`frontend/src/api`
- 启动与装配：`backend/server.py`、`backend/config/get_scheduler.py`

## 2. 当前模块边界总览

| 模块 | 核心职责 | 后端接口前缀（现状） | 主要数据归属 | 前端覆盖（现状） |
| --- | --- | --- | --- | --- |
| admin | 认证鉴权、用户角色菜单、组织与字典、系统配置、日志、任务管理、缓存/在线监控 | `/api/v1/admin/login`、`/api/v1/admin/logout`、`/api/v1/admin/getInfo`、`/api/v1/admin/getRouters`、`/api/v1/admin/system/*`、`/api/v1/admin/monitor/*`、`/api/v1/admin/common/*` | `sys_user`、`sys_role`、`sys_menu`、`sys_dept`、`sys_dict_*`、`sys_config`、`sys_notice`、`sys_logininfor`、`sys_oper_log`、`sys_job`、`sys_job_log`、`sys_upload` | 已覆盖 `system/*`、`auth/*` 页面 |
| bi | 看板聚合查询（读模型） | `/api/v1/bi/data/console`、`/api/v1/bi/data/console/chart` | 只读 `dm.dm_group_count_by_day` | 有 `dashboard/console` 页面，但尚未发现对应 API 接入 |
| generator | 元数据导入、代码预览/生成、建表与同步 | `/api/v1/generator/tool/gen/*` | `gen_table`、`gen_table_column`（并读取业务库元数据） | 暂无独立页面与 API 封装 |
| task | 定时任务执行函数集合（被调度） | 无独立 HTTP 控制器（由调度器通过 `invoke_target` 调用） | 无独立业务表（执行记录落 `sys_job_log`） | 无 |

## 3. 模块依赖关系（现状）

### 3.1 已存在依赖

- `bi -> admin`：复用 `LoginService.get_current_user` 作为统一鉴权入口。
- `generator -> admin`：复用鉴权、审计注解与用户模型。
- `admin(job) -> task`：任务白名单以 `module_task` 为执行域，调度器加载 `module_task` 中函数。

### 3.2 边界判断

- 当前代码基本满足“DAO 未跨域直接调用”原则。
- 但存在“跨域依赖落在业务模块内部”的耦合（如 `bi/generator` 直接依赖 `module_admin.service.login_service`），后续应下沉为共享能力层（shared kernel）。

## 4. 领域归属与责任声明（基线）

### 4.1 admin 边界

- **负责**：身份认证、RBAC、系统配置、系统监控、任务配置与日志、通用上传。
- **拥有**：`sys_*` 系统表与相关接口。
- **不负责**：BI 读模型聚合、代码生成逻辑实现、任务执行函数业务。

### 4.2 bi 边界

- **负责**：只读查询与看板聚合，不承载事务写入。
- **拥有**：`/data/*` 查询接口定义与返回模型。
- **不负责**：用户权限模型维护、任务调度配置、代码生成元数据维护。

### 4.3 generator 边界

- **负责**：代码生成配置、模板渲染、元数据导入与同步。
- **拥有**：`gen_*` 元数据表与 `/tool/gen/*` 接口。
- **不负责**：运行期业务任务执行、BI 查询逻辑。

### 4.4 task 边界

- **负责**：被调度函数实现（同步/异步任务执行单元）。
- **拥有**：任务执行函数命名空间（`module_task.*`）。
- **不负责**：任务编排配置、任务审计持久化（这部分属于 admin）。

## 5. 约束规则（参考行业规范）

- **单向依赖**：业务域只能依赖共享能力层，禁止直接依赖其他域的 Service/DAO。
- **数据所有权**：每张表有且仅有一个“写入责任域”；跨域访问通过 API/事件，不允许跨域写库。
- **接口归属**：接口前缀与责任域一一对应（`/system|/monitor|/common -> admin`，`/data -> bi`，`/tool/gen -> generator`）。
- **任务执行隔离**：`task` 仅提供可执行函数，调度、审计、权限放在 `admin`（未来可拆至 orchestrator/worker）。
- **前后端一致性**：前端按域维护 API 客户端（`api/admin`、`api/bi`、`api/generator`、`api/task`），避免跨域混放。

## 6. 发现的边界风险（待下一步处理）

- 前端现有接口路径与后端真实路径存在偏差（例如前端使用 `/api/user/list`，后端为 `/system/user/list` 语义）。
- 前端尚未形成 `bi/generator/task` 的 API 模块分层，当前以系统管理页面为主。
- `bi/generator` 复用 `module_admin` 内部服务做鉴权，建议抽离为共享鉴权组件，降低未来拆服务成本。

## 7. Owner 清单（表）

说明：owner 指“唯一写入责任域”；其他域仅允许读，且需通过 API/事件或受控查询访问。

| 表/数据对象 | 当前 owner | 写权限 | 允许读取方 | 备注 |
| --- | --- | --- | --- | --- |
| `sys_user` | admin | admin | bi/generator/task（通过鉴权上下文） | 用户主数据 |
| `sys_role` | admin | admin | bi/generator/task（通过鉴权上下文） | 角色权限 |
| `sys_menu` | admin | admin | frontend（经 `/getRouters`） | 菜单路由 |
| `sys_dept` | admin | admin | admin | 组织结构 |
| `sys_post` | admin | admin | admin | 岗位 |
| `sys_dict_type`、`sys_dict_data` | admin | admin | admin/generator | 字典与任务分组、执行器 |
| `sys_config` | admin | admin | admin | 系统参数 |
| `sys_notice` | admin | admin | admin | 通知公告 |
| `sys_logininfor`、`sys_oper_log` | admin | admin | admin | 审计日志 |
| `sys_job`、`sys_job_log` | admin | admin | task（执行态） | 调度配置与执行日志 |
| `sys_upload` | admin | admin | admin | 上传文件元数据 |
| `gen_table`、`gen_table_column` | generator | generator | admin（只读）、generator | 代码生成元数据 |
| `dm.dm_group_count_by_day` | bi（读模型域） | 非本系统写入 | bi | 当前由 BI 查询只读消费 |

## 8. Owner 清单（接口）

说明：按前缀归属单一责任域，避免“一个接口多个 owner”。

| 接口前缀/资源 | owner | 典型接口 | 说明 |
| --- | --- | --- | --- |
| `/api/v1/admin/login`、`/api/v1/admin/logout`、`/api/v1/admin/getInfo`、`/api/v1/admin/getRouters` | admin | 登录/登出/用户信息/动态路由 | 认证与会话 |
| `/api/v1/admin/system/user` | admin | 用户列表、导入导出、资料维护 | 身份与用户管理 |
| `/api/v1/admin/system/role` | admin | 角色、数据权限、用户授权 | RBAC |
| `/api/v1/admin/system/menu` | admin | 菜单树、角色菜单、增删改查 | 菜单与权限点 |
| `/api/v1/admin/system/dept`、`/api/v1/admin/system/post` | admin | 组织与岗位管理 | 组织模型 |
| `/api/v1/admin/system/dict`、`/api/v1/admin/system/config` | admin | 字典与参数管理 | 配置中心能力 |
| `/api/v1/admin/system/notice` | admin | 通知公告管理 | 系统内容 |
| `/api/v1/admin/monitor/*` | admin | 日志、在线、任务、缓存、服务器 | 监控与任务控制面 |
| `/api/v1/admin/common/*` | admin | 上传、下载、资源访问 | 通用文件服务 |
| `/api/v1/bi/data/console`、`/api/v1/bi/data/console/chart` | bi | 控制台指标与图表查询 | BI 读模型查询 |
| `/api/v1/generator/tool/gen/*` | generator | 导入表、预览代码、生成代码 | 生成器能力 |
| `module_task.*`（函数入口） | task | `job()`、`async_job()` | 非 HTTP，供调度器调用 |

## 9. Owner 清单（事件）

### 9.1 当前事件现状（代码已存在）

| 事件类型 | owner | 触发方 | 消费方 | 现状 |
| --- | --- | --- | --- | --- |
| `scheduler.job.submitted` | admin | APScheduler listener | admin（写 `sys_job_log`） | 已实现（内部事件） |
| `scheduler.job.executed` | admin | APScheduler listener | admin（更新 `sys_job_log`） | 已实现（内部事件） |
| `scheduler.job.error` | admin | APScheduler listener | admin（更新失败日志） | 已实现（内部事件） |
| `scheduler.job.missed` | admin | APScheduler listener | admin（更新失败日志） | 已实现（内部事件） |

### 9.2 目标业务事件（Phase 1+ 规划 owner）

| 业务事件名 | owner | producer | 主要 consumer | 用途 |
| --- | --- | --- | --- | --- |
| `dataset.ingested` | ingestion（未来） | ingestion-service | processing-service | 接入完成通知 |
| `dataset.processed` | processing（未来） | processing-service | storage-metadata/bi-query | 处理成功回写 |
| `dataset.process.failed` | processing（未来） | processing-service | workflow-orchestrator/notification | 失败补偿与告警 |
| `dataset.version.published` | storage-metadata（未来） | storage-metadata-service | bi-query | 读模型刷新 |
| `labeling.task.created` | labeling（未来） | labeling-service | notification/bi-query | 标注任务建立 |
| `labeling.task.completed` | labeling（未来） | labeling-service | bi-query | 标注结果入读模型 |

## 10. 跨域访问准入规则（执行口径）

- 禁止跨域 DAO 直接调用；跨域必须走“公开 API 或事件”。
- 允许跨域复用的仅限共享能力（鉴权、日志、通用响应模型），并逐步下沉到 shared kernel。
- BI 域保持只读查询，不写系统事务表。
- task 域不持有业务写库职责，仅提供可执行函数；任务配置与日志落库由 admin 域负责。
- 新增接口必须先声明 owner，再落代码；owner 不明确不得合并。

## 11. 本步骤验收结论

- 已完成“领域边界文档（谁负责哪些表、接口、事件）”并形成 owner 清单。
- 文档可直接用于 Phase 0 验收项“职责清晰、避免跨域直连”的评审基线。
