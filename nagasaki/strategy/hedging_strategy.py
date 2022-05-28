from nagasaki.clients import BaseClient
from nagasaki.clients.base_client import OrderTaker
from nagasaki.database.utils import write_order_taker_to_db
from nagasaki.enums.common import SideTypeEnum, InstrumentTypeEnum
from nagasaki.state import State
from nagasaki.strategy.abstract_strategy import AbstractStrategy


def sell_order(amount):
    return OrderTaker(
        side=SideTypeEnum.ASK,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
    )


def buy_order(amount):
    return OrderTaker(
        side=SideTypeEnum.BID,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
    )


class HedgingStrategy(AbstractStrategy):
    def __init__(self, state: State, client: BaseClient):
        self.state = state
        self.client = client

    def execute(self):
        delta = self.state.grand_total_delta

        btc_mark_usd = self.state.deribit.btc_mark_usd

        order = None

        if delta > 0.001:
            btcs_to_short_in_dollars = round(delta * btc_mark_usd, -1)
            order = sell_order(btcs_to_short_in_dollars)

        if delta < -0.001:
            btcs_to_long_in_dollars = round(-1 * delta * btc_mark_usd, -1)
            order = buy_order(btcs_to_long_in_dollars)

        if order:
            self.client.create_order(order)
            write_order_taker_to_db(order)
