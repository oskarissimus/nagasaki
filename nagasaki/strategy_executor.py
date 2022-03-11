from nagasaki.logger import logger
from nagasaki.enums.common import OrderActionEnum
from nagasaki.event_manager import EventManager
from nagasaki.models.bitclude import BitcludeEventOrderbook
from nagasaki.strategy import Strategy
from nagasaki.state import State, Orderbook


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
            logger.debug(f"{s.bid_orderbook=}")

            if orderbook_event.side == "ask":
                logger.info(f"ASK orderbook: {Orderbook(sorted(s.ask_orderbook))}")
                if len(s.ask_orderbook) > 1:
                    last_top_ask = min(s.ask_orderbook)
                    if orderbook_event.order_action == OrderActionEnum.CREATED:
                        s.ask_orderbook.append(orderbook_event.price)
                    else:
                        if orderbook_event.price in s.ask_orderbook:
                            s.ask_orderbook.remove(orderbook_event.price)
                        else:
                            logger.info(f"{orderbook_event.price} is not in orderbook")
                    current_top_ask = min(s.ask_orderbook)
                    if current_top_ask < last_top_ask:
                        # fetch wallet and active offers from api and write to state
                        self.event_manager.post_event("synchronize_bitclude_state")
                        # execute strategy
                        actions = self.strategy.get_actions_ask()
                        self.event_manager.post_event(
                            "actions_execution_on_bitclude_requested", actions
                        )
                else:
                    logger.info("empty ask orderbook")
                    if orderbook_event.order_action == OrderActionEnum.CREATED:
                        s.ask_orderbook.append(orderbook_event.price)
                    else:
                        if orderbook_event.price in s.ask_orderbook:
                            s.ask_orderbook.remove(orderbook_event.price)
                        else:
                            logger.info(f"{orderbook_event.price} is not in orderbook")
                    # fetch wallet and active offers from api and write to state
                    self.event_manager.post_event("synchronize_bitclude_state")
                    # execute strategy
                    actions = self.strategy.get_actions_ask()
                    self.event_manager.post_event(
                        "actions_execution_on_bitclude_requested", actions
                    )

            # if orderbook_event.side == "bid":
            #     logger.debug("bid orderbook changed")
            #     if orderbook_event.order_action == OrderActionEnum.CREATED:
            #         s.bid_orderbook.append(orderbook_event.price)
            #     else:
            #         if orderbook_event.price in s.bid_orderbook:
            #             s.bid_orderbook.remove(orderbook_event.price)
            #         else:
            #             logger.info(f"{orderbook_event.price} is not in orderbook")
            #     actions = self.strategy.get_actions_bid()
            #     self.event_manager.post_event(
            #         "actions_execution_on_bitclude_requested", actions
            #     )
