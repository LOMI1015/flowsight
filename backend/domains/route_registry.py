from typing import List
from domains.admin.route_registry import get_admin_routes
from domains.bi.route_registry import get_bi_routes
from domains.generator.route_registry import get_generator_routes
from domains.task.route_registry import get_task_routes
from domains.types import RouteConfig


def get_all_domain_routes() -> List[RouteConfig]:
    return [
        *get_admin_routes(),
        *get_bi_routes(),
        *get_generator_routes(),
        *get_task_routes(),
    ]
