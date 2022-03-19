from abc import ABC, abstractmethod


class AbstractStrategy(ABC):
    @abstractmethod
    def get_actions_bid(self):
        pass

    @abstractmethod
    def get_actions_ask(self):
        pass


class StrategyException(Exception):
    pass
