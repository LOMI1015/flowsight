from domains.shared.events.event_models import EventMessage
from domains.shared.events.registry import get_event_bus
from utils.log_util import logger

DATASET_INGESTED = 'dataset.ingested'


async def on_dataset_ingested(event: EventMessage) -> None:
    logger.info(
        f'event consumed: type={event.event_type}, event_id={event.event_id}, '
        f'dataset_id={event.dataset_id}, trace_id={event.trace_id}'
    )


def register_ingestion_event_handlers() -> None:
    event_bus = get_event_bus()
    event_bus.subscribe(DATASET_INGESTED, on_dataset_ingested)
