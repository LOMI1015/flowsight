from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.infrastructure.database import init_database
from app.infrastructure.redis_stream import RedisStreamPublisher


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    try:
        await RedisStreamPublisher.connect()
    except Exception:
        # 允许在无 redis 环境启动，发布阶段按配置决定是否失败
        pass
    yield
    await RedisStreamPublisher.close()

app = FastAPI(
    title='flowsight-ingestion-service',
    description='FlowSight ingestion standalone service',
    version='0.1.0',
    lifespan=lifespan,
)

app.include_router(router)
