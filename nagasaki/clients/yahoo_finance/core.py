from decimal import Decimal

import requests
from retry import retry

from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient
from nagasaki.clients.yahoo_finance.dto import Model
from nagasaki.logger import logger
from nagasaki.scrapers.yahoo_finance_api import scrape_api_key


class YahooFinanceClientException(Exception):
    pass


# pylint: disable=too-few-public-methods
class YahooFinanceClient(UsdPlnQuotingBaseClient):
    def __init__(
        self,
        api_key: str,
        email: str,
        password: str,
        url_base: str = "https://yfapi.net",
    ):
        self.api_key = api_key
        self.url_base = url_base
        self.email = email
        self.password = password

    @retry(YahooFinanceClientException, tries=3)
    def _fetch_finance_quote(self) -> Model:
        params = {"region": "GB", "lang": "en", "symbols": "USDPLN=X"}
        headers = {"x-api-key": self.api_key}
        response = requests.request(
            "GET",
            f"{self.url_base}/v6/finance/quote",
            headers=headers,
            params=params,
        )

        if response.status_code == 200:
            return Model(**response.json())

        if response.status_code == 403:
            self.api_key = scrape_api_key(self.email, self.password)

        raise YahooFinanceClientException(
            f"Error fetching quote: {response.status_code}"
        )

    def fetch_usd_pln_quote(self) -> Decimal:
        finance_quote = self._fetch_finance_quote()
        price = finance_quote.quoteResponse.result[0].regularMarketPrice
        logger.info(f"Fetched USD/PLN quote: {price}")
        return price
