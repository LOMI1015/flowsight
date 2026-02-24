from typing import TypedDict, List


class RouteConfig(TypedDict):
    router: object
    tags: List[str]
    prefix: str
