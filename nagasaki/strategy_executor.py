from typing import List

from nagasaki.event_manager import EventManager
from nagasaki.logger import logger
from nagasaki.models.bitclude import BitcludeEventOrderbook
from nagasaki.state import State
from nagasaki.strategy.abstract_strategy import AbstractStrategy


class StrategyExecutor:
    """
    does side-effects on state
    generates events to execute actions
    """

    def __init__(
        self,
        strategies: List[AbstractStrategy],
        event_manager: EventManager,
        state: State,
    ):
        self.strategies = strategies
        self.event_manager = event_manager
        self.state = state

    def on_strategy_execution_requested(self):
        logger.debug("strategy execution requested")
        for strategy in self.strategies:
            strategy.execute()
