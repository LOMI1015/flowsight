from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title='flowsight-workflow-orchestrator-service',
    description='FlowSight workflow orchestrator standalone service',
    version='0.1.0',
)

app.include_router(router)
