from decimal import Decimal

from dependency_injector.wiring import inject

from nagasaki.clients import BaseClient
from nagasaki.clients.base_client import OrderTaker
from nagasaki.database.utils import write_order_taker_to_db
from nagasaki.enums.common import InstrumentTypeEnum, MarketEnum, SideTypeEnum
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
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
        self,
        client: BaseClient,
        instrument: InstrumentTypeEnum,
        bitclude_state: BitcludeState,
        deribit_state: DeribitState,
        yahoo_finance_state: YahooFinanceState,
    ):
        self.client = client
        self.instrument = instrument
        self.bitclude_state = bitclude_state
        self.deribit_state = deribit_state
        self.yahoo_finance_state = yahoo_finance_state

    @inject
    def execute(self):
        delta = self.grand_total_delta()
        logger.info(f"Grand Total Δ: {delta:.8f}")

        btc_mark_usd = self.deribit_state.mark_price[self.instrument.market_1]

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

    def grand_total_delta(self) -> Decimal:
        runtime_config = RuntimeConfig()
        currency = MarketEnum(runtime_config.market_making_instrument.market_1)
        bitclude_assets = self.bitclude_state.account_info.assets_total(currency)
        deribit_total_delta = (
            self.deribit_state.account_summary.margin_balance
            + self.deribit_state.account_summary.delta_total
        )
        return bitclude_assets + deribit_total_delta
