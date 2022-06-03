from decimal import Decimal

from nagasaki.enums.common import SideTypeEnum
from nagasaki.state import State
from nagasaki.strategy.calculators.delta_calculator import DeltaCalculator
from nagasaki.strategy.calculators.epsilon_calculator import EpsilonCalculator
from nagasaki.strategy.delta_epsilon_strategy.dispatcher import StrategyOrderDispatcher
from nagasaki.strategy.market_making_strategy import MarketMakingStrategy


class DeltaEpsilonStrategyBid(MarketMakingStrategy):
    def __init__(
        self, state: State, dispatcher: StrategyOrderDispatcher, epsilon: Decimal = None
    ):
        epsilon = epsilon or Decimal("0.01")
        super(DeltaEpsilonStrategyBid, self).__init__(
            state,
            dispatcher,
            side=SideTypeEnum.BID,
            delta_calculator=DeltaCalculator(),
            epsilon_calculator=EpsilonCalculator(epsilon),
        )
