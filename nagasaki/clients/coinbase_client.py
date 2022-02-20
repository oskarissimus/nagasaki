from decimal import Decimal
import requests


class CoinbaseClientException(Exception):
    pass


class CoinbaseClient:
    def __init__(self):
        self.base_url = "https://api.coinbase.com/v2"

    def fetch_usd_mark_price_pln(self):
        response = requests.get(f"{self.base_url}/exchange-rates?currency=USD")
        if response.status_code != 200:
            raise CoinbaseClientException(
                f"Coinbase API returned status code {response.status_code}"
            )
        response_json = response.json()
        if "data" not in response_json:
            raise CoinbaseClientException("Coinbase API returned no data")
        if "rates" not in response_json["data"]:
            raise CoinbaseClientException("Coinbase API returned no rates")
        if "PLN" not in response_json["data"]["rates"]:
            raise CoinbaseClientException("Coinbase API returned no PLN rate")
        return Decimal(response_json["data"]["rates"]["PLN"])

    def fetch_pln_mark_price_usd(self):
        response = requests.get(f"{self.base_url}/exchange-rates?currency=PLN")
        if response.status_code != 200:
            raise CoinbaseClientException(
                f"Coinbase API returned status code {response.status_code}"
            )
        response_json = response.json()
        if "data" not in response_json:
            raise CoinbaseClientException("Coinbase API returned no data")
        if "rates" not in response_json["data"]:
            raise CoinbaseClientException("Coinbase API returned no rates")
        if "USD" not in response_json["data"]["rates"]:
            raise CoinbaseClientException("Coinbase API returned no USD rate")
        return Decimal(response_json["data"]["rates"]["USD"])
