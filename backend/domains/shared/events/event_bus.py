from collections import defaultdict
from typing import Awaitable, Callable, Dict, List, Protocol
from domains.shared.events.event_models import EventMessage
from utils.log_util import logger

EventHandler = Callable[[EventMessage], Awaitable[None]]


class EventBus(Protocol):
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        ...

    async def publish(self, event: EventMessage) -> None:
        ...


class InProcessEventBus:
    """
    进程内事件总线（最小实现）：
    - 订阅：按 event_type 注册处理器
    - 发布：串行分发给所有处理器
    """

    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if handler in self._handlers[event_type]:
            return
        self._handlers[event_type].append(handler)

    async def publish(self, event: EventMessage) -> None:
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            logger.info(f'event skipped: type={event.event_type}, event_id={event.event_id}')
            return

        for handler in handlers:
            try:
                await handler(event)
            except Exception as exc:
                logger.exception(
                    f'event handler failed: type={event.event_type}, event_id={event.event_id}, error={exc}'
                )
