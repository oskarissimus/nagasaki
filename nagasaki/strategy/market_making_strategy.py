from decimal import Decimal

from nagasaki.clients.base_client import OrderMaker
from nagasaki.database.utils import write_order_maker_to_db
from nagasaki.enums.common import SideTypeEnum, InstrumentTypeEnum
from nagasaki.strategy.abstract_strategy import AbstractStrategy
from nagasaki.strategy.calculators.delta_calculator import DeltaCalculator
from nagasaki.strategy.calculators.epsilon_calculator import EpsilonCalculator
from nagasaki.strategy.dispatcher import StrategyOrderDispatcher
from nagasaki.state import State
from nagasaki.logger import logger


def calculate_btc_value_in_pln(btc: Decimal, price: Decimal) -> Decimal:
    return btc * price


def calculate_inventory_parameter(
    total_pln: Decimal, total_btc_value_in_pln: Decimal
) -> Decimal:
    wallet_sum_in_pln = total_pln + total_btc_value_in_pln
    pln_to_sum_ratio = total_btc_value_in_pln / wallet_sum_in_pln  # values from 0 to 1
    return pln_to_sum_ratio * 2 - 1


def make_order(price: Decimal, amount: Decimal, side: SideTypeEnum) -> OrderMaker:
    return OrderMaker(
        side=side,
        price=price,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PLN,
    )


class MarketMakingStrategy(AbstractStrategy):
    def __init__(
        self,
        state: State,
        dispatcher: StrategyOrderDispatcher,
        side: SideTypeEnum = None,
        delta_calculator: DeltaCalculator = None,
        epsilon_calculator: EpsilonCalculator = None,
    ):
        self.state = state
        self.dispatcher = dispatcher
        self.epsilon_calculator = epsilon_calculator
        self.delta_calculator = delta_calculator
        self.side = side

    def execute(self):
        self.log_prices()
        order = make_order(self.best_price, self.amount, self.side)

        self.dispatcher.dispatch(order)
        write_order_maker_to_db(order)

    @property
    def best_price(self):
        if not self.delta_price:
            return self.epsilon_price

        if not self.epsilon_price:
            return self.delta_price

        best_func = max if self.side == SideTypeEnum.ASK else min
        return best_func(self.delta_price, self.epsilon_price)

    @property
    def delta_price(self):
        if not self.delta_calculator:
            return None
        return self.delta_calculator.calculate(self.state, self.side)

    @property
    def epsilon_price(self):
        if not self.epsilon_calculator:
            return None
        return self.epsilon_calculator.calculate(self.top, self.side)

    @property
    def top(self):
        if self.side == SideTypeEnum.ASK:
            return self.top_ask
        return self.top_bid

    @property
    def top_ask(self):
        return min(self.state.bitclude.orderbook_rest.asks, key=lambda x: x.price).price

    @property
    def top_bid(self):
        return max(self.state.bitclude.orderbook_rest.bids, key=lambda x: x.price).price

    @property
    def amount(self):
        if self.side == SideTypeEnum.ASK:
            return self.total_btc
        return self.total_pln / self.best_price

    @property
    def total_btc(self):
        return (
            self.state.bitclude.account_info.balances["BTC"].active
            + self.state.bitclude.account_info.balances["BTC"].inactive
        )

    @property
    def total_pln(self):
        return (
            self.state.bitclude.account_info.balances["PLN"].active
            + self.state.bitclude.account_info.balances["PLN"].inactive
        )

    @property
    def btc_mark_pln(self):
        return self.state.deribit.btc_mark_usd * self.state.usd_pln

    @property
    def inventory_parameter(self):
        balances = self.state.bitclude.account_info.balances
        total_pln = balances["PLN"].active + balances["PLN"].inactive
        total_btc = balances["BTC"].active + balances["BTC"].inactive

        total_btc_value_in_pln = calculate_btc_value_in_pln(
            total_btc, self.btc_mark_pln
        )
        return calculate_inventory_parameter(total_pln, total_btc_value_in_pln)

    def log_prices(self):
        if self.epsilon_price:
            logger.info(f"{self.epsilon_price=:.0f}")
        if self.delta_price:
            logger.info(f"{self.delta_price=:.0f}")

        logger.info(f"{self.best_price=:.0f}")
