from decimal import Decimal

import pydantic

from nagasaki.enums.common import SideTypeEnum
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.state import State


class DeltaCalculator:
    def __init__(self, delta_1: Decimal = None, delta_2: Decimal = None):
        runtime_config = RuntimeConfig()
        try:
            self.delta_1 = delta_1 or runtime_config.delta_when_pln_only
            self.delta_2 = delta_2 or runtime_config.delta_when_btc_only
            assert self.delta_1 >= 0
            assert self.delta_2 >= 0
        except (pydantic.ValidationError, FileNotFoundError):
            pass

        self.delta_1 = self.delta_1 or Decimal("0.0005")
        self.delta_2 = self.delta_2 or Decimal("0.002")

    def calculate(self, state: State, side: SideTypeEnum) -> Decimal:
        mark_price = state.deribit.btc_mark_usd * state.usd_pln
        inventory_parameter = self.inventory_parameter(state)
        if side == SideTypeEnum.ASK:
            delta_price = self.calculate_ask(mark_price, inventory_parameter)
        else:
            delta_price = self.calculate_bid(mark_price, inventory_parameter)
        logger.info(f"{delta_price=:.0f}")
        return delta_price

    def calculate_ask(self, mark_price, inventory_parameter):
        return mark_price * (1 + self.inventory_adjusted_delta(inventory_parameter))

    def calculate_bid(self, mark_price, inventory_parameter):
        return mark_price * (1 - self.inventory_adjusted_delta(inventory_parameter))

    def inventory_adjusted_delta(self, inventory_parameter):
        """
        delta(inventory_parameter) is a linear function with two
        known points: (-1, delta_1) and (1, delta_2)

        as inv_param goes from -1 to 1 (changes by 2), delta changes by
        delta_x - delta_1:
        (inv_param - (-1)/(1-(-1)) = (delta_x - delta_1)/(delta_2 - delta_1)
        (inv_param + 1)/2 = (delta_x - delta_1)/(delta_2 - delta_1)

        solving for delta_x:
        delta_x = delta_1 + (delta_2 - delta_1) * (inv_param + 1)/2

        """
        assert inventory_parameter >= -1
        assert inventory_parameter <= 1

        return self.delta_1 + ((inventory_parameter + 1) / 2) * (
            self.delta_2 - self.delta_1
        )

    def inventory_parameter(self, state):
        mark_price = state.deribit.btc_mark_usd * state.usd_pln
        balances = state.bitclude.account_info.balances
        total_pln = balances["PLN"].active + balances["PLN"].inactive
        total_btc = balances["BTC"].active + balances["BTC"].inactive

        total_btc_value_in_pln = calculate_btc_value_in_pln(total_btc, mark_price)
        return calculate_inventory_parameter(total_pln, total_btc_value_in_pln)


def calculate_btc_value_in_pln(btc: Decimal, price: Decimal) -> Decimal:
    return btc * price


def calculate_inventory_parameter(
    total_pln: Decimal, total_btc_value_in_pln: Decimal
) -> Decimal:
    wallet_sum_in_pln = total_pln + total_btc_value_in_pln
    pln_to_sum_ratio = total_btc_value_in_pln / wallet_sum_in_pln  # values from 0 to 1
    return pln_to_sum_ratio * 2 - 1
