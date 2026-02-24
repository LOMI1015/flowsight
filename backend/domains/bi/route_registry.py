from typing import List
from domains.types import RouteConfig
from module_bi.controller.console_controller import consoleController

API_V1_BI_PREFIX = '/api/v1/bi'


def get_bi_routes() -> List[RouteConfig]:
    return [
        {'router': consoleController, 'tags': ['BI数据模块'], 'prefix': API_V1_BI_PREFIX},
    ]
