import itertools
from typing import List

from nagasaki.logger import logger
from nagasaki.enums.common import OrderActionEnum
from nagasaki.event_manager import EventManager
from nagasaki.models.bitclude import BitcludeEventOrderbook
from nagasaki.strategy.abstract_strategy import AbstractStrategy
from nagasaki.state import State


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

    def on_orderbook_changed(self, orderbook_event: BitcludeEventOrderbook):
        if orderbook_event.symbol == "BTC_PLN":
            if orderbook_event.side == "ask":
                self.event_manager.post_event("synchronize_bitclude_state")
                self.event_manager.post_event("strategy_execution_requested")

    def on_strategy_execution_requested(self):
        logger.debug("strategy execution requested")
        actions = list(
            itertools.chain.from_iterable(
                strategy.get_actions() for strategy in self.strategies
            )
        )
        self.event_manager.post_event("actions_execution_requested", actions)
