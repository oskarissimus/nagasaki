from decimal import Decimal
from typing import Dict

from pydantic import BaseModel


class ExchangeBalance(BaseModel):
    """
    Balance model containing active and inactive balances in
    form of a dict containing 'free', 'used' and 'total' keys.
    """

    free: Dict[str, Decimal]
    total: Dict[str, Decimal]
    used: Dict[str, Decimal]


class ExchangeBalances(BaseModel):
    """
    Balances of all exchanges
    """

    exchange_balances: Dict[str, ExchangeBalance]


class MarkPrices(BaseModel):
    """
    Mark prices of all currencies
    """

    prices: Dict[str, Decimal]
