from abc import ABC, abstractmethod

from nagasaki.clients.base_client import Order


class AbstractStrategy(ABC):
    @abstractmethod
    def execute(self) -> Order:
        pass


class StrategyException(Exception):
    pass
