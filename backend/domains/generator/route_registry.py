from typing import List
from domains.types import RouteConfig
from module_generator.controller.gen_controller import genController

API_V1_GENERATOR_PREFIX = '/api/v1/generator'


def get_generator_routes() -> List[RouteConfig]:
    return [
        {'router': genController, 'tags': ['代码生成'], 'prefix': API_V1_GENERATOR_PREFIX},
    ]
