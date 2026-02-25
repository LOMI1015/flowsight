from domains.shared.events.event_bus import InProcessEventBus

_event_bus = InProcessEventBus()


def get_event_bus() -> InProcessEventBus:
    return _event_bus
