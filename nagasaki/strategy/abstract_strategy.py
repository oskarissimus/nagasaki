from abc import ABC, abstractmethod

from nagasaki.models.bitclude import Order


class AbstractStrategy(ABC):
    @abstractmethod
    def execute(self) -> Order:
        pass


class StrategyException(Exception):
    pass
