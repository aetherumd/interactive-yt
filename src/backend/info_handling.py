from typing import *
from backend.options import *

class EventBroker:
    """
    Handles incoming/outgoing requests for information.
    """
    
    def __init__(self):
        self.entries: dict[str, tuple[Any, Any, bool, list["Subscriber"]]] = dict()

    def publish(self, name: str, data: Any):
        if data is not None:
            _, default, consume, subs = self.entries.get(name, (None, None, False, []))
            self.entries[name] = (data, default, consume, subs)
            self.notify(name)

    def reset(self, name: str):
        pass

    def subscribe(self, s: "Subscriber", to: list[V3Option]):
        for name in to:
            data, reset, consume, subs = self.entries.get(name, (None, None, False, []))
            if s not in subs:
                subs += [s]
            self.entries[name] = (data, reset, consume, subs)

    def notify(self, name: V3Option):
        _, _, _, subs = self.entries.get(name, (None, None, []))
        for sub in subs:
            sub.notify(name)

    def query(self, name: V3Option) -> Any:
        data, default, consume, subs = self.entries.get(name, (None, None, False, []))
        if consume:
            self.entries[name] = (default, default, consume, subs)
        if data is None and default is not None:
            return default
        return data

    def add_field(self, name: V3Option, data: Any, default: Any, consume: bool):
        if name not in self.entries.keys():
            _, _, _, subs = self.entries.get(name, (None, None, False, []))
            self.entries[name] = (data, default, consume, subs)

class AuthorUser:
    """
    Parent class for Publisher & Subscriber. 
    
    May be unnecessary, but there could
    have been a problem in the past where multi-inheritance did not work otherwise.
    I do not remember and have no motivation to confirm this at the moment.
    12/11/2024.

    update: sounds about right, code works atm so no need to change
    1/30/25
    """

    def __init__(self, broker: "EventBroker"):
        self.broker = broker

class Publisher(AuthorUser):
    """
    Generates/collects then publishes information.
    """
    def __init__(self, broker: "EventBroker"):
        super().__init__(broker)
        self.broker: "EventBroker" = broker

    def add_field(self, option: V3Option):
        (_, (data, default),) = option.value

        if type(option) is UserAction:
            self.broker.add_field(option, data, default, True)
        else:
            self.broker.add_field(option, data, default, False)

    def update(self, name: V3Option):
        pass

    def publish(self, name: V3Option, data: Any):
        self.broker.publish(name, data)


class Subscriber(AuthorUser):
    """
    Subscribes to certain fields of its broker. When one of those fields is updated,
    the Subscriber is notified & able to query any information it pleases.
    """

    def __init__(self, broker: "EventBroker"):
        super().__init__(broker)
        self.broker: "EventBroker" = broker

    def notify(self, name: V3Option):
        self.handle_update(name)
    
    def query(self, name: V3Option, default: Any = None) -> Any:
        return self.broker.query(name)

    def subscribe(self, name: V3Option):
        self.broker.subscribe(self, name)

    def handle_update(self, name: V3Option):
        pass