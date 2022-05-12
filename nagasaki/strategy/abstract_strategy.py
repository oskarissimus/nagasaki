from abc import ABC, abstractmethod


class AbstractStrategy(ABC):
    @abstractmethod
    def get_actions(self):
        pass


class StrategyException(Exception):
    pass
