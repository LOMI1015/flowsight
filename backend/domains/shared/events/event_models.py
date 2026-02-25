from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class EventMessage:
    event_id: str
    event_type: str
    occurred_at: str
    trace_id: str
    producer: str
    dataset_id: str
    dataset_version: str
    payload: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def build(
        cls,
        *,
        event_id: str,
        event_type: str,
        trace_id: str,
        producer: str,
        dataset_id: str = '-',
        dataset_version: str = 'v1',
        payload: Dict[str, Any] | None = None,
    ) -> 'EventMessage':
        return cls(
            event_id=event_id,
            event_type=event_type,
            occurred_at=datetime.utcnow().isoformat(),
            trace_id=trace_id,
            producer=producer,
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            payload=payload or {},
        )
