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
        self.calculators = [delta_calculator, epsilon_calculator]
        self.side = side

    def execute(self):
        order = make_order(self.best_price, self.amount, self.side)
        self.dispatcher.dispatch(order)
        write_order_maker_to_db(order)

    @property
    def best_price(self):
        best_func = max if self.side == SideTypeEnum.ASK else min
        all_prices = [
            calculator.calculate(self.state, self.side)
            for calculator in self.calculators
        ]
        best_price = best_func(all_prices)
        logger.info(f"{best_price=:.0f}")
        return best_price

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
