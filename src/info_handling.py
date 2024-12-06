import os, sys, yt, typing
from typing import Any
from abc import ABC, abstractmethod
from enum import Enum

class EventBroker:
    """
    
    """
    
    def __init__(self):
        self.entries: dict[str, tuple[Any, Any, list["Subscriber"]]] = dict()

    def publish(self, name: str, data: Any):
        if data is not None:
            _, default, subs = self.entries.get(name, (None, None, []))
            self.entries[name] = (data, default, subs)
            self.notify(name)

    def reset(self, name: str):
        pass

    def subscribe(self, s: "Subscriber", to: list[str]):
        for name in to:
            data, reset, subs = self.entries.get(name, (None, None, []))
            subs += [s]
            self.entries[name] = (data, reset, subs)

    def notify(self, name: str):
        _, _, subs = self.entries.get(name, (None, None, []))
        for sub in subs:
            sub.notify(name)

    def query(self, name: str, default = (None, None, [])) -> Any:
        data, reset, subs = self.entries.get(name, default)
        if reset != None:
            self.entries[name] = (reset, reset, subs)
        return data

    def add_field(self, name: str, data: Any, reset: Any):
        _, _, subs = self.entries.get(name, (data, reset, []))
        self.entries[name] = (data, reset, subs)

class AuthorUser:
    def __init__(self, broker: "EventBroker"):
        self.broker = broker

class Publisher(AuthorUser):
    def __init__(self, broker: "EventBroker"):
        super().__init__(broker)
        self.broker: "EventBroker" = broker

    def add_field(self, name: str, data: Any, reset: Any):
        self.broker.add_field(name, data, reset)

    def update(self, name: str):
        pass

    def publish(self, name: str, data: Any):
        self.broker.publish(name, data)


class Subscriber(AuthorUser):
    def __init__(self, broker: "EventBroker"):
        super().__init__(broker)
        self.broker: "EventBroker" = broker

    def notify(self, name: str):
        self.handle_update(name)
    
    def query(self, name: str, default: Any = None) -> Any:
        return self.broker.query(name, default= (None, default, []))

    def subscribe(self, name: str):
        self.broker.subscribe(self, name)

    def handle_update(self, name: str):
        pass