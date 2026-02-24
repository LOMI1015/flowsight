# FlowSight API 版本规范（Phase 0 - Step 4）

## 1. 基础规则

- 所有对外 HTTP 接口必须带版本前缀：`/api/v{major}`。
- 当前基线版本：`/api/v1`。
- 禁止新增无版本前缀接口。

## 2. 域前缀规则

- `admin` 域：`/api/v1/admin/...`
- `bi` 域：`/api/v1/bi/...`
- `generator` 域：`/api/v1/generator/...`

说明：`task` 当前为函数执行域（非独立 HTTP 服务），后续独立服务后使用 `/api/v1/task/...`。

## 3. 版本演进策略

- `v1` 内允许向后兼容的增量字段扩展。
- 存在破坏性变更时，必须升级大版本（如 `v2`），并保留 `v1` 一段迁移窗口。
- 每次版本升级需提供迁移说明（字段变更、路径变更、鉴权变更）。

## 4. 当前落地状态

- 后端路由统一挂载到版本前缀：
  - `admin`：`/api/v1/admin/*`
  - `bi`：`/api/v1/bi/*`
  - `generator`：`/api/v1/generator/*`
- 前端已对现有调用路径切换到 `/api/v1` 规范。
