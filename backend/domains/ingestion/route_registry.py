from typing import List
from domains.ingestion.controller.ingestion_controller import ingestionController
from domains.types import RouteConfig

API_V1_INGESTION_PREFIX = '/api/v1/ingestion'


def get_ingestion_routes() -> List[RouteConfig]:
    return [
        {'router': ingestionController, 'tags': ['Ingestion接入'], 'prefix': API_V1_INGESTION_PREFIX},
    ]
