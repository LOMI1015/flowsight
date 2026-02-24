# FlowSight 后端架构升级实施路线图

> 目标：基于当前后台管理代码，逐步升级为“采集 -> 处理 -> 存储 -> 标注 -> 可视化”的数据中台微服务架构。

---

## 1. 技术选型总览（建议版本）

### 1.1 核心技术栈

- **后端框架**：FastAPI（统一 API 风格，便于拆服务）
- **数据库**：PostgreSQL（事务 + JSONB + 分区）
- **缓存/轻量队列**：Redis（缓存、分布式锁、Streams）
- **对象存储**：MinIO（S3 兼容，承载原始文件和中间产物）
- **任务编排（初期）**：APScheduler（沿用当前能力）
- **任务执行（中期）**：独立 Worker（消费 Redis Streams）
- **网关**：Nginx（统一入口、反向代理、限流）
- **容器化**：Docker Compose（开发）+ Kubernetes（生产演进）

### 1.2 中期可升级组件（按复杂度引入）

- **消息队列升级**：Kafka（大吞吐、多消费者场景）
- **编排升级**：Prefect / Airflow（复杂 DAG、回填补数）
- **可观测性**：
  - Prometheus（指标）
  - Grafana（看板）
  - Loki（日志）
  - OpenTelemetry（链路追踪）

---

## 2. 目标微服务清单（按业务边界）

- `gateway-service`
  - 统一入口、路由、鉴权转发、限流、灰度
- `iam-admin-service`
  - 用户/角色/权限/组织/系统配置/审计日志
- `ingestion-service`
  - 文件/API/第三方源接入，数据集登记，投递处理任务
- `workflow-orchestrator-service`
  - 工作流编排、重试策略、失败补偿、告警触发
- `processing-service`
  - 清洗、校验、标准化、映射、去重、脱敏
- `storage-metadata-service`
  - 数据集元数据、血缘、版本、状态管理
- `labeling-service`
  - 标注任务分配、标注结果、质检、协作记录
- `bi-query-service`
  - 读模型聚合、看板查询、统计接口
- `notification-service`（可后置）
  - 站内消息、邮件、Webhook、告警通知

---

## 3. 数据链路与事件规范（统一标准）

### 3.1 标准流程

1. `ingestion-service` 接收入湖请求
2. 原始文件落 MinIO，元数据入库
3. 发布事件 `dataset.ingested`
4. `processing-service` 消费并处理
5. 发布事件 `dataset.processed` / `dataset.process.failed`
6. `storage-metadata-service` 更新状态与版本
7. `bi-query-service` 刷新读模型
8. 前端只读取 `bi-query-service`

### 3.2 事件命名建议

- `dataset.ingested`
- `dataset.validated`
- `dataset.processed`
- `dataset.process.failed`
- `dataset.version.published`
- `labeling.task.created`
- `labeling.task.completed`
- `workflow.job.retrying`
- `workflow.job.deadlettered`

### 3.3 事件体基础字段（必须）

- `event_id`（全局唯一）
- `event_type`
- `occurred_at`（ISO8601）
- `trace_id`（链路追踪）
- `producer`
- `dataset_id`
- `dataset_version`
- `payload`（业务字段）

---

## 4. 开发与拆分步骤（完整执行 List）

## Phase 0：基线治理（1 周）

- [x] 梳理现有模块边界（admin / bi / task / generator）
- [x] 输出领域边界文档（谁负责哪些表、接口、事件）
- [x] 统一配置管理（按服务拆分 `.env` 模板）
- [x] 加入 API 版本规范（如 `/api/v1/...`）
- [x] 确定统一错误码与响应结构
- [x] 加入基础日志规范（trace_id、user_id、dataset_id）

**交付物**
- [x] `docs/architecture/domain-boundary.md`
- [x] `docs/standards/api-error-code.md`
- [x] `docs/standards/logging-trace.md`

**验收标准**
- [x] 各模块职责清晰，无新增跨域 DAO 直接调用

**验收记录（2026-02-24）**
- 已完成边界梳理与 owner 清单（表/接口/事件），职责归属清晰。
- 已完成按服务拆分的 `.env` 模板与配置管理规范文档。
- 已落地 `/api/v1` 版本化路由策略，并完成前端核心接口同步。
- 已统一错误码与响应结构（含稳定 `error_code` 字段）。
- 已落地日志三元组规范：`trace_id`、`user_id`、`dataset_id`。

---

## Phase 1：模块化单体（1~2 周）

- [x] 在单体内先按领域重组目录（不拆进程）
- [x] 抽象应用服务层（禁止 Controller 直连 DAO）
- [ ] 将“上传 + 解析 + 入库”链路从通用逻辑独立为 ingestion domain
- [ ] 定义内部事件总线接口（先可用进程内实现）
- [ ] 增加幂等键机制（`dataset_id + version`）

**交付物**
- [ ] `docs/architecture/modular-monolith.md`
- [ ] ingestion 领域内部接口文档

**验收标准**
- [ ] 核心数据上传流程可独立测试、可重复执行

---

## Phase 2：拆出第一个微服务 ingestion（2~3 周）

- [ ] 新建 `services/ingestion-service`
- [ ] 提供接口：创建数据集、上传文件、查询接入任务状态
- [ ] 文件只负责入湖与登记，不做重处理
- [ ] 引入 Redis Streams：发布 `dataset.ingested`
- [ ] 单独数据库 schema（如 `ingestion`）
- [ ] 网关接入新服务路由

**交付物**
- [ ] ingestion OpenAPI 文档
- [ ] Redis Stream topic 约定文档
- [ ] 服务 Dockerfile / compose 配置

**验收标准**
- [ ] ingestion 服务可独立部署与扩缩容
- [ ] 失败重试不产生重复数据（幂等通过）

---

## Phase 3：拆编排与处理（3~6 周）

- [ ] 新建 `workflow-orchestrator-service`
- [ ] 新建 `processing-service`（worker 形态）
- [ ] 将处理逻辑从管理服务迁移到 processing
- [ ] 配置重试策略（指数退避 + 最大重试次数）
- [ ] 配置死信队列（DLQ）与人工补偿机制
- [ ] 打通状态回写到 metadata（`PENDING/RUNNING/FAILED/SUCCEEDED`）

**交付物**
- [ ] 工作流状态机文档
- [ ] 失败处理与补偿 SOP
- [ ] 处理任务性能基线（吞吐/延迟）

**验收标准**
- [ ] 单任务失败不影响全局队列消费
- [ ] 异常任务可追踪、可回放、可补偿

---

## Phase 4：拆查询与标注服务（2~4 周）

- [ ] 新建 `bi-query-service`，构建读模型
- [ ] 新建 `labeling-service`，实现标注任务生命周期
- [ ] BI 查询不再直连事务处理表
- [ ] 标注结果通过事件更新到读模型

**交付物**
- [ ] BI 读模型结构设计
- [ ] 标注服务接口文档与权限矩阵

**验收标准**
- [ ] 看板查询延迟稳定
- [ ] 标注全流程可审计（谁在何时改了什么）

---

## Phase 5：治理与生产化（持续）

- [ ] 接入 Prometheus/Grafana（接口、队列、任务指标）
- [ ] 接入集中日志（结构化日志 + 检索）
- [ ] 接入链路追踪（跨服务 trace）
- [ ] 建立 CI/CD（测试、镜像、部署、回滚）
- [ ] 建立压测基线与容量规划
- [ ] 编写运行手册（告警、故障演练、应急预案）

**交付物**
- [ ] `docs/ops/runbook.md`
- [ ] `docs/ops/alert-rules.md`
- [ ] `docs/ops/capacity-plan.md`

**验收标准**
- [ ] 可观测性覆盖关键链路
- [ ] 具备可回滚与故障恢复能力

---

## 5. 数据库拆分策略（强建议）

- 每个服务拥有自己的 schema 或独立库
- 禁止跨服务写库，跨服务用 API/事件
- 统一主键策略（UUID 或雪花 ID）
- 所有“状态更新”保留事件日志表，支持追溯
- 大表尽早分区（按日期/租户）
- 读写分离优先从 BI 查询开始

---

## 6. API 与安全规范（必须执行）

- JWT 鉴权统一在 gateway 处理，服务做二次鉴权校验
- 服务间通信使用服务凭证（而非用户 Token）
- 上传文件做 MIME + 扩展名双重校验
- 敏感字段（手机号、身份证、token）统一脱敏与加密存储
- 接口幂等：创建/重试类接口必须支持 `Idempotency-Key`
- 关键操作保留审计日志（who/when/what/before/after）

---

## 7. 测试清单（每阶段都要有）

- [ ] 单元测试：领域逻辑、状态机、幂等
- [ ] 集成测试：服务间 API + 事件投递
- [ ] 端到端测试：上传 -> 处理 -> 看板可见
- [ ] 回归测试：权限、任务调度、导入导出
- [ ] 性能测试：高并发上传、批处理吞吐、慢查询
- [ ] 混沌测试：消息重复、消息丢失、服务重启

---

## 8. 推荐目录结构（演进后的仓库）

```text
flowsight/
  services/
    gateway-service/
    iam-admin-service/
    ingestion-service/
    workflow-orchestrator-service/
    processing-service/
    storage-metadata-service/
    labeling-service/
    bi-query-service/
    notification-service/
  packages/
    common-auth/
    common-events/
    common-logging/
    common-models/
  deployments/
    docker-compose/
    k8s/
  docs/
    architecture/
    standards/
    ops/
```

---

## 9. 90 天里程碑（可直接排期）

- **第 1~2 周**：Phase 0 + Phase 1（边界治理 + 模块化）
- **第 3~5 周**：Phase 2（ingestion 独立服务上线）
- **第 6~9 周**：Phase 3（编排与处理拆分上线）
- **第 10~12 周**：Phase 4 + Phase 5（查询/标注 + 治理完善）

---

## 10. 当前代码到目标架构的映射（便于迁移）

- `module_admin` -> `iam-admin-service`（优先拆权限、用户、审计）
- `module_bi` -> `bi-query-service`（逐步改为读模型）
- `module_task` + `config/get_scheduler.py` -> `workflow-orchestrator-service`
- `module_admin/service/common_service.py` 上传处理逻辑 -> `ingestion-service` + `processing-service`
- 本地上传目录逻辑 -> MinIO 统一对象存储（逐步迁移）

---

## 11. 决策原则（避免后期架构漂移）

- 先稳定边界，再拆进程
- 优先拆“高变更、高耗时、高耦合”模块
- 优先事件解耦，减少同步强依赖
- 每次只拆一个服务并可回滚
- 文档、监控、测试与代码同时交付

---

## 12. 命名规范（Naming Convention）

## 12.1 仓库与服务命名

- 仓库目录统一使用 `kebab-case`：`services/ingestion-service`
- Python 包名统一使用 `snake_case`：`ingestion_service`
- 服务名格式：`<domain>-service`，示例：`bi-query-service`
- 网关路由前缀统一：`/api/v1/<domain>/...`

## 12.2 文件与模块命名

- 控制器：`*_controller.py`
- 服务层：`*_service.py`
- 数据访问层：`*_dao.py`
- 数据模型：
  - 持久化模型：`*_do.py`
  - 请求响应模型：`*_vo.py`
- 工具类：`*_util.py`
- 配置：`settings.py`、`env.py`、`constants.py`

## 12.3 类、函数、变量命名

- 类名：`PascalCase`，如 `DatasetIngestionService`
- 函数/方法名：`snake_case`，如 `create_dataset_version`
- 变量名：`snake_case`，如 `dataset_version`
- 常量名：`UPPER_SNAKE_CASE`，如 `MAX_RETRY_TIMES`
- 布尔变量：前缀 `is_` / `has_` / `can_`，如 `is_deleted`

## 12.4 数据库命名

- 表名：`snake_case`，建议加域前缀，如 `ing_dataset`
- 字段名：`snake_case`，时间统一：`created_at`、`updated_at`
- 主键统一：`id`（业务唯一键另设 `*_code` 或 `*_idempotency_key`）
- 状态字段统一：`status`（枚举值需文档化）
- 索引命名：
  - 普通索引：`idx_<table>_<field>`
  - 唯一索引：`uk_<table>_<field>`

## 12.5 API 与事件命名

- REST 路径使用名词复数：`/datasets`、`/jobs`
- 避免动词路径：使用 HTTP 方法表达动作
- 事件名统一：`domain.entity.action`，如 `dataset.version.published`
- 事件字段统一小写下划线，保留 `trace_id`

## 12.6 命名反例（避免）

- 不要混用 `camelCase` 和 `snake_case`（后端代码统一 `snake_case`）
- 不要出现 `data1`、`temp2`、`newObj` 等无语义变量名
- 不要使用缩写黑话（除行业标准缩写：`id`、`url`、`api`）

---

## 13. 开发过程中的语法与工程规范

## 13.1 Python 语法与代码风格

- 统一 Python 版本（建议 3.11+）
- 统一格式化和静态检查：`ruff + ruff format`
- 公共函数必须补充类型注解
- 复杂返回值定义 Pydantic 模型，避免返回裸 `dict`
- 不允许吞异常：`except Exception` 后必须记录上下文并抛出业务异常
- 禁止 `eval` 处理外部输入（调度目标应改为白名单映射）

## 13.2 FastAPI 分层规范

- Controller 只做参数校验、鉴权和响应封装
- Service 承载业务逻辑，不直接依赖 Request 对象（尽量）
- DAO 只负责数据访问，不包含业务分支逻辑
- 跨服务调用统一走客户端层（`clients/`），不散落在 service 内

## 13.3 数据与事务规范

- 一次业务操作只在一个服务内事务提交
- 跨服务一致性使用事件最终一致，避免分布式事务
- 所有写接口支持幂等键（`Idempotency-Key`）
- 大批量写入必须分批并可重试（记录批次游标）

## 13.4 消息与任务规范

- 每个消费者必须实现幂等消费（事件去重表或缓存）
- 消费失败进入重试队列，超过阈值进入 DLQ
- 任务状态必须可观测：`PENDING/RUNNING/SUCCEEDED/FAILED`
- 任务日志必须包含：`trace_id`、`job_id`、`dataset_id`

## 13.5 API 规范

- 成功响应格式统一（`code/message/data/trace_id`）
- 错误码分层：系统错误、业务错误、权限错误、参数错误
- 分页参数统一：`page_num`、`page_size`
- 时间字段统一 UTC 存储，输出 ISO8601

## 13.6 Git 与开发流程规范

- 分支命名：`feature/<domain>-<topic>`、`fix/<domain>-<topic>`
- Commit 建议：`feat:`、`fix:`、`refactor:`、`docs:`、`test:`
- PR 必须包含：变更说明、影响范围、测试结果、回滚方案
- 禁止“功能开发 + 大规模重构”混在一个 PR

## 13.7 测试与质量门禁

- 新增逻辑必须带单元测试
- 跨服务改动必须带集成测试
- 发布前必须跑端到端冒烟（采集到看板）
- CI 门禁：lint 通过 + 测试通过 + 构建成功

---

## 14. 详细开发任务表（采集 -> 可视化）

> 说明：每个阶段均给出三类内容：**新增功能**、**可复用现有代码**、**需去除/替换的冗余**。

## Stage A：数据采集（Ingestion）

**新增功能**
- [ ] 数据集管理：创建数据集、版本、来源渠道（文件/API）
- [ ] 上传会话管理：分片上传、断点续传、重试
- [ ] MinIO 入湖：原始文件统一落对象存储
- [ ] 采集任务状态：`CREATED/UPLOADING/INGESTED/FAILED`
- [ ] 采集事件发布：`dataset.ingested`

**可复用现有代码**
- [ ] 复用 `backend/module_admin/service/common_service.py` 的上传校验思路
- [ ] 复用 `backend/module_admin/service/file_data_service.py` 的文件读取/批处理思路
- [ ] 复用 `backend/utils/upload_util.py` 的扩展名校验、文件工具函数
- [ ] 复用 `backend/config/env.py` 中 MinIO/Upload 配置结构

**需去除/替换的冗余**
- [ ] 去除“上传后直接写本地目录”为主流程（保留兼容开关）
- [ ] 去除上传成功后立即做重处理的同步逻辑（改为异步事件）
- [ ] 去除硬编码表名与列映射（改为数据集模板配置）

---

## Stage B：数据校验与标准化（Validation & Standardization）

**新增功能**
- [ ] Schema 注册中心（字段定义、类型、约束）
- [ ] 数据质量规则（空值率、唯一性、枚举合法性）
- [ ] 标准化映射（字段别名 -> 标准字段）
- [ ] 校验报告输出（错误行、错误原因、可修复建议）
- [ ] 发布事件：`dataset.validated` / `dataset.validation.failed`

**可复用现有代码**
- [ ] 复用 `file_data_service` 的列映射机制（升级为模板化）
- [ ] 复用现有日志工具 `backend/utils/log_util.py`

**需去除/替换的冗余**
- [ ] 去除列映射硬编码在服务方法中的实现
- [ ] 去除“异常即全量失败”的单一策略（改为可配置：严格/宽松）

---

## Stage C：数据处理（Processing）

**新增功能**
- [ ] 处理任务 Worker：消费 `dataset.ingested`
- [ ] 清洗规则：去重、类型转换、字段修正、脱敏
- [ ] 批处理框架：批次游标、断点续跑
- [ ] 处理结果写入 ODS/DWD（按层落表）
- [ ] 发布事件：`dataset.processed` / `dataset.process.failed`

**可复用现有代码**
- [ ] 复用 `backend/module_admin/service/file_data_service.py` 的分批入库逻辑
- [ ] 复用 `backend/config/get_scheduler.py` 的任务状态记录思路
- [ ] 复用 `backend/module_admin/service/job_service.py` 的任务管理思想

**需去除/替换的冗余**
- [ ] 去除 `eval` 形式的任务目标执行（改为显式函数注册表）
- [ ] 去除处理逻辑散落在管理域服务中的实现（统一迁移到 processing）
- [ ] 去除单体内“同步串行处理”路径（改为异步队列）

---

## Stage D：元数据与存储治理（Metadata & Storage）

**新增功能**
- [ ] 元数据服务：数据集、版本、血缘、分区、生命周期
- [ ] 数据目录与检索（按业务域、标签、时间）
- [ ] 数据权限模型（数据集级别 RBAC）
- [ ] 状态机：`PENDING/RUNNING/SUCCEEDED/FAILED/PUBLISHED`
- [ ] 数据版本发布：`dataset.version.published`

**可复用现有代码**
- [ ] 复用 `module_admin` 的 RBAC 基础能力（用户、角色、权限）
- [ ] 复用已有 PostgreSQL 与 Redis 配置和连接管理

**需去除/替换的冗余**
- [ ] 去除跨模块直接查写对方表的做法
- [ ] 去除状态字段语义不统一的历史实现（统一状态枚举）

---

## Stage E：标注协作（Labeling）

**新增功能**
- [ ] 标注任务创建与分配（按角色/技能组）
- [ ] 标注工作台 API（领取、提交、驳回、复审）
- [ ] 质检抽检机制（准确率、召回率、一致性）
- [ ] 标注结果版本化与审计日志
- [ ] 发布事件：`labeling.task.created` / `labeling.task.completed`

**可复用现有代码**
- [ ] 复用 `module_admin` 的用户组织体系和权限鉴权
- [ ] 复用日志和操作记录能力用于审计

**需去除/替换的冗余**
- [ ] 去除“标注状态只在前端内存维护”的临时实现
- [ ] 去除不可追溯的覆盖更新（改为版本追加）

---

## Stage F：可视化与查询（BI Query & Visualization）

**新增功能**
- [ ] 构建 `bi-query-service` 读模型（面向看板）
- [ ] 聚合查询接口（趋势、漏斗、对比、分布）
- [ ] 看板缓存策略（热指标缓存 + 过期刷新）
- [ ] 权限隔离查询（租户/部门/角色维度）
- [ ] 指标口径文档化与版本管理

**可复用现有代码**
- [ ] 复用 `backend/module_bi/service/console_service.py` 的指标查询思路
- [ ] 复用 `backend/module_bi/controller/console_controller.py` 的接口结构

**需去除/替换的冗余**
- [ ] 去除 BI 直接查询事务处理表的路径（改查读模型）
- [ ] 去除查询 SQL 分散硬编码（集中到查询仓储层）

---

## Stage G：编排、告警与运维（Orchestration & Ops）

**新增功能**
- [ ] 工作流编排中心（依赖关系、重试、补偿）
- [ ] 告警规则（任务失败率、堆积长度、延迟阈值）
- [ ] 可观测性三件套（metrics/log/trace）
- [ ] 运维面板（任务拓扑、失败重跑、DLQ 处理）

**可复用现有代码**
- [ ] 复用 `backend/config/get_scheduler.py` 的调度基础
- [ ] 复用 `module_admin` 中 job / job_log 管理逻辑

**需去除/替换的冗余**
- [ ] 去除“单进程调度承载全部工作流”的架构瓶颈
- [ ] 去除日志中缺失 `trace_id` 的历史埋点方式

---

## 15. 建议的任务执行顺序（落地优先级）

- P0（必须先做）
  - [ ] Stage A 采集服务化
  - [ ] Stage C 处理异步化
  - [ ] Stage D 元数据统一
- P1（稳定后做）
  - [ ] Stage F 读模型与可视化解耦
  - [ ] Stage G 可观测与告警补齐
- P2（业务扩展）
  - [ ] Stage E 标注协作体系

