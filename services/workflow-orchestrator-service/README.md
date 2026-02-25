# workflow-orchestrator-service

FlowSight 编排服务骨架（Phase 3 起点）。

## 本地启动

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9301 --reload
```

## 当前接口

- `GET /healthz`：健康检查
- `POST /workflows`：创建工作流任务（最小状态机）
- `GET /workflows/{workflow_job_id}`：查询工作流任务状态
