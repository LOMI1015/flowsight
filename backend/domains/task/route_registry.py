from typing import List
from domains.types import RouteConfig


def get_task_routes() -> List[RouteConfig]:
    """
    task 领域当前仅提供调度函数，不暴露HTTP路由。
    """
    return []
