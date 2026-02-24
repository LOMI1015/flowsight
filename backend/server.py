from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.env import AppConfig
from config.get_db import init_create_table, init_admin_user
from config.get_redis import RedisUtil
from config.get_scheduler import SchedulerUtil
from domains.route_registry import get_all_domain_routes
from exceptions.handle import handle_exception
from middlewares.handle import handle_middleware
from sub_applications.handle import handle_sub_applications
from utils.common_util import worship
from utils.log_util import logger


# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f'{AppConfig.app_name}开始启动')
    worship()
    await init_create_table()
    await init_admin_user()  # 初始化超级管理员
    app.state.redis = await RedisUtil.create_redis_pool()
    await RedisUtil.init_sys_dict(app.state.redis)
    await RedisUtil.init_sys_config(app.state.redis)
    await SchedulerUtil.init_system_scheduler()
    logger.info(f'{AppConfig.app_name}启动成功')
    yield
    await RedisUtil.close_redis_pool(app)
    await SchedulerUtil.close_system_scheduler()


# 初始化FastAPI对象
app = FastAPI(
    title=AppConfig.app_name,
    description=f'{AppConfig.app_name}接口文档',
    version=AppConfig.app_version,
    lifespan=lifespan,
)

# 挂载子应用
handle_sub_applications(app)
# 加载中间件处理方法
handle_middleware(app)
# 加载全局异常处理方法
handle_exception(app)


# 加载路由列表（按领域装配）
for controller in get_all_domain_routes():
    app.include_router(
        router=controller.get('router'),
        tags=controller.get('tags'),
        prefix=controller.get('prefix'),
    )
