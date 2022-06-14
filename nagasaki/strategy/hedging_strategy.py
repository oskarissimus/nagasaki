from decimal import Decimal

from nagasaki.clients import BaseClient
from nagasaki.clients.base_client import OrderTaker
from nagasaki.enums.common import InstrumentTypeEnum, MarketEnum, SideTypeEnum, Symbol
from nagasaki.logger import logger
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState
from nagasaki.strategy.abstract_strategy import AbstractStrategy


def sell_order(amount: Decimal, instrument: InstrumentTypeEnum, symbol: Symbol):
    return OrderTaker(
        side=SideTypeEnum.ASK,
        amount=amount,
        instrument=instrument,
        symbol=symbol,
    )


def buy_order(amount: Decimal, instrument: InstrumentTypeEnum, symbol: Symbol):
    return OrderTaker(
        side=SideTypeEnum.BID,
        amount=amount,
        instrument=instrument,
        symbol=symbol,
    )


class HedgingStrategy(AbstractStrategy):
    def __init__(
        self,
        client: BaseClient,
        instrument: InstrumentTypeEnum,
        symbol: Symbol,
        grand_total_delta_max: Decimal,
        grand_total_delta_min: Decimal,
        bitclude_state: BitcludeState,
        deribit_state: DeribitState,
        yahoo_finance_state: YahooFinanceState,
    ):
        self.client = client
        self.instrument = instrument
        self.symbol = symbol
        self.grand_total_delta_max = grand_total_delta_max
        self.grand_total_delta_min = grand_total_delta_min
        self.bitclude_state = bitclude_state
        self.deribit_state = deribit_state
        self.yahoo_finance_state = yahoo_finance_state

    def execute(self) -> OrderTaker:
        delta = self.grand_total_delta()
        logger.info(f"Grand Total Δ: {delta:.8f} {self.instrument.market_1}")

        mark_price_usd = self.deribit_state.mark_price[self.instrument.market_1]

        order = None

        if delta > self.grand_total_delta_max:
            btcs_to_short_in_dollars = Decimal(round(delta * mark_price_usd, -1))
            order = sell_order(btcs_to_short_in_dollars, self.instrument, self.symbol)

        if delta < self.grand_total_delta_min:
            btcs_to_long_in_dollars = Decimal(round(-1 * delta * mark_price_usd, -1))
            order = buy_order(btcs_to_long_in_dollars, self.instrument, self.symbol)

        if order:
            self.client.create_order(order)

        return order

    def grand_total_delta(self) -> Decimal:
        currency = MarketEnum(self.instrument.market_1)
        bitclude_assets = self.bitclude_state.account_info.assets_total(currency)
        deribit_total_delta = (
            self.deribit_state.account_summary.margin_balance
            + self.deribit_state.account_summary.delta_total
        )
        return bitclude_assets + deribit_total_delta
