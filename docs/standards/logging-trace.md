# FlowSight 基础日志规范（Phase 0 - Step 6）

## 1. 目标

- 所有请求链路日志统一携带 `trace_id`、`user_id`、`dataset_id`。
- 保证跨模块排障时可按三元组快速检索。

## 2. 字段定义

- `trace_id`：请求链路唯一标识，由中间件在请求进入时生成。
- `user_id`：当前登录用户 ID。未登录或无法识别时为 `-`。
- `dataset_id`：数据集标识。优先读取 `X-Dataset-Id` 请求头，其次读取 `dataset_id` 查询参数；无值时为 `-`。

## 3. 注入策略

- `trace_id` 与 `dataset_id` 在 `trace_middleware` 中统一初始化。
- `user_id` 在鉴权成功后写入链路上下文（`LoginService.get_current_user`）。
- 响应头回传 `request-id` 与 `trace-id`，便于前后端联合排障。

## 4. 日志输出格式

日志输出顺序统一为：

- 时间
- `trace_id`
- `user_id`
- `dataset_id`
- 级别
- 代码位置
- 消息

示例：

```text
2026-02-24 23:59:59.123 | a1b2c3... | 1001 | ds_20260224_01 | INFO | module:func:123 - 获取成功
```

## 5. 开发约束

- 控制器/服务层记录日志时不再手工拼接上述字段，由日志上下文自动注入。
- 业务代码新增日志应使用结构化、可检索语义（避免仅输出“执行失败”）。
- 跨服务调用时建议透传 `trace-id` 与 `X-Dataset-Id`。
