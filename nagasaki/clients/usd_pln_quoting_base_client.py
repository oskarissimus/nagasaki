from abc import ABC, abstractmethod
from decimal import Decimal

# pylint: disable=too-few-public-methods
class UsdPlnQuotingBaseClient(ABC):
    @abstractmethod
    def fetch_usd_pln_quote(self) -> Decimal:
        pass
