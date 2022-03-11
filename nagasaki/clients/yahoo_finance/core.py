from decimal import Decimal
import requests
from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient
from nagasaki.clients.yahoo_finance.dto import Model


class YahooFinanceClientException(Exception):
    pass


# pylint: disable=too-few-public-methods
class YahooFinanceClient(UsdPlnQuotingBaseClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://yfapi.net"

    def _fetch_finance_quote(self) -> Model:
        params = {"region": "GB", "lang": "en", "symbols": "USDPLN=X"}
        headers = {"x-api-key": self.api_key}
        response = requests.request(
            "GET",
            f"{self.base_url}/v6/finance/quote",
            headers=headers,
            params=params,
        )

        if response.status_code == 200:
            return Model(**response.json())
        raise YahooFinanceClientException(
            f"Error fetching quote: {response.status_code}"
        )

    def fetch_usd_pln_quote(self) -> Decimal:
        finance_quote = self._fetch_finance_quote()
        return finance_quote.quoteResponse.result[0].regularMarketPrice
