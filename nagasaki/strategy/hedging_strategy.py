from decimal import Decimal

from nagasaki.clients import BaseClient
from nagasaki.clients.base_client import OrderTaker
from nagasaki.database.utils import write_order_taker_to_db
from nagasaki.enums.common import SideTypeEnum, InstrumentTypeEnum
from nagasaki.state import State
from nagasaki.strategy.abstract_strategy import AbstractStrategy


def sell_order(amount: Decimal, instrument: InstrumentTypeEnum):
    return OrderTaker(
        side=SideTypeEnum.ASK,
        amount=amount,
        instrument=instrument,
    )


def buy_order(amount: Decimal, instrument: InstrumentTypeEnum):
    return OrderTaker(
        side=SideTypeEnum.BID,
        amount=amount,
        instrument=instrument,
    )


class HedgingStrategy(AbstractStrategy):
    def __init__(
        self, state: State, client: BaseClient, instrument: InstrumentTypeEnum
    ):
        self.state = state
        self.client = client
        self.instrument = instrument

    def execute(self):
        delta = self.state.grand_total_delta

        btc_mark_usd = self.state.deribit.mark_price[self.instrument.market_1]

        order = None

        if delta > 0.001:
            btcs_to_short_in_dollars = round(delta * btc_mark_usd, -1)
            order = sell_order(btcs_to_short_in_dollars, self.instrument)

        if delta < -0.001:
            btcs_to_long_in_dollars = round(-1 * delta * btc_mark_usd, -1)
            order = buy_order(btcs_to_long_in_dollars, self.instrument)

        if order:
            self.client.create_order(order)
            write_order_taker_to_db(order)
