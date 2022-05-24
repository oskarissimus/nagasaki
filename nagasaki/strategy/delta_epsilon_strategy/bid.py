from decimal import Decimal

from nagasaki.clients.base_client import OrderMaker
from nagasaki.database.utils import write_order_maker_to_db
from nagasaki.enums.common import SideTypeEnum, InstrumentTypeEnum
from nagasaki.strategy.abstract_strategy import AbstractStrategy, StrategyException
from nagasaki.state import State
from nagasaki.strategy.delta_epsilon_strategy.dispatcher import StrategyOrderDispatcher


def calculate_btc_value_in_pln(btc: Decimal, price: Decimal) -> Decimal:
    return btc * price


def calculate_inventory_parameter(
    total_pln: Decimal, total_btc_value_in_pln: Decimal
) -> Decimal:
    wallet_sum_in_pln = total_pln + total_btc_value_in_pln
    pln_to_sum_ratio = total_btc_value_in_pln / wallet_sum_in_pln  # values from 0 to 1
    return pln_to_sum_ratio * 2 - 1


def calculate_delta_adjusted_for_inventory(inventory_parameter):
    A = Decimal("-0.0035")
    B = Decimal("0.0055")
    res = A * inventory_parameter + B
    if res <= 0:
        raise StrategyException(f"Delta is too small for inventory parameter: {res}")
    return res


def calculate_delta_price(deribit_mark_price: Decimal, delta: Decimal) -> Decimal:
    """
    delta price is distanced from deribit mark price depending on inventory parameter
    """
    return deribit_mark_price * (1 - delta)


def calculate_epsilon_price(top_bid: Decimal, epsilon: Decimal) -> Decimal:
    """
    epsilon price is distanced from bitclude top ask by epsilon in PLN
    """
    return top_bid + epsilon


def bid_order(price: Decimal, amount: Decimal) -> OrderMaker:
    return OrderMaker(
        side=SideTypeEnum.BID,
        price=price,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PLN,
    )


class DeltaEpsilonStrategyBid(AbstractStrategy):
    def __init__(
        self, state: State, dispatcher: StrategyOrderDispatcher, epsilon: Decimal = None
    ):
        self.state = state
        self.dispatcher = dispatcher
        self.epsilon = epsilon or Decimal("0.01")

    def get_actions(self):
        delta_price = calculate_delta_price(
            self.btc_mark_pln, self.delta_adjusted_for_inventory
        )
        epsilon_price = calculate_epsilon_price(self.top_bid, self.epsilon)

        desirable_price = max(delta_price, epsilon_price)
        desirable_amount = self.total_pln / desirable_price
        desirable_order = bid_order(desirable_price, desirable_amount)

        self.dispatcher.dispatch(desirable_order)
        write_order_maker_to_db(desirable_order)

    @property
    def top_bid(self):
        return max(self.state.bitclude.orderbook_rest.bids, key=lambda x: x.price).price

    @property
    def total_pln(self):
        return self.state.bitclude.account_info.plns

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

    @property
    def delta_adjusted_for_inventory(self):
        return calculate_delta_adjusted_for_inventory(self.inventory_parameter)
