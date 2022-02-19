from nagasaki.logger import logger
from nagasaki.enums import OrderActionEnum
from nagasaki.event_manager import EventManager
from nagasaki.schemas import BitcludeEventOrderbook
from nagasaki.strategy import Strategy
from nagasaki.state import State


class StrategyExecutor:
    """
    does side-effects on state
    generates events to execute actions
    """

    def __init__(self, strategy: Strategy, event_manager: EventManager, state: State):
        self.strategy = strategy
        self.event_manager = event_manager
        self.state = state

    def on_orderbook_changed(self, orderbook_event: BitcludeEventOrderbook):
        s = self.state
        logger.debug("orderbook changed")
        if orderbook_event.symbol == "BTC_PLN":
            logger.debug("BTC_PLN orderbook changed")
            logger.info(f"{s.bid_orderbook=}")
            logger.debug(f"{s.ask_orderbook=}")

            if orderbook_event.side == "ask":
                logger.debug("ask orderbook changed")
                if orderbook_event.order_action == OrderActionEnum.CREATED:
                    s.ask_orderbook.append(orderbook_event.price)
                else:
                    if orderbook_event.price in s.ask_orderbook:
                        s.ask_orderbook.remove(orderbook_event.price)
                    else:
                        print(f"{orderbook_event.price} is not in orderbook")

            if orderbook_event.side == "bid":
                logger.debug("bid orderbook changed")
                if orderbook_event.order_action == OrderActionEnum.CREATED:
                    s.bid_orderbook.append(orderbook_event.price)
                else:
                    if orderbook_event.price in s.bid_orderbook:
                        s.bid_orderbook.remove(orderbook_event.price)
                    else:
                        print(f"{orderbook_event.price} is not in orderbook")
                actions = self.strategy.get_actions_bid()
                self.event_manager.post_event(
                    "actions_execution_on_bitclude_requested", actions
                )
