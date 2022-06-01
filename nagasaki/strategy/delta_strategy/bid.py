from decimal import Decimal

from nagasaki.clients.base_client import OrderMaker
from nagasaki.database.utils import write_order_maker_to_db
from nagasaki.enums.common import SideTypeEnum, InstrumentTypeEnum
from nagasaki.strategy.abstract_strategy import AbstractStrategy
from nagasaki.state import State
from nagasaki.strategy.delta_epsilon_strategy.dispatcher import StrategyOrderDispatcher

from nagasaki.strategy.delta_strategy.utils import (
    calculate_btc_value_in_pln,
    calculate_inventory_parameter,
    calculate_delta_adjusted_for_inventory,
)



def calculate_delta_price(deribit_mark_price: Decimal, delta: Decimal) -> Decimal:
    """
    delta price is distanced from deribit mark price depending on inventory parameter
    IMPORTANT NOTE: this is diffrent in ASK strategy
    """
    return deribit_mark_price * (1 - delta)


def bid_order(price: Decimal, amount: Decimal) -> OrderMaker:
    return OrderMaker(
        side=SideTypeEnum.BID,
        price=price,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PLN,
    )


class DeltaStrategyBid(AbstractStrategy):
    def __init__(self, state: State, dispatcher: StrategyOrderDispatcher):
        self.state = state
        self.dispatcher = dispatcher

    def execute(self):
        delta_price = calculate_delta_price(
            self.btc_mark_pln, self.delta_adjusted_for_inventory
        )

        desirable_price = delta_price
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
