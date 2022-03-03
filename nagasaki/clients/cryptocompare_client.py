import requests
import pandas as pd
import json
from decimal import Decimal


class CannotParseResponse(Exception):
    pass


class CryptocompareClientException(Exception):
    pass


class CryptocompareClient:
    def __init__(self, base_url: str = "https://min-api.cryptocompare.com/data"):
        self.base_url = base_url

    def fetch_usd_mark_price_pln(self):
        response = requests.get(f"{self.base_url}/price?fsym=USD&tsyms=PLN")
        return response.json()["PLN"]

    def fetch_histominute_data(self):
        # url is https://min-api.cryptocompare.com/data/v2/histominute?fsym=USD&tsym=PLN&limit=10
        response = requests.get(
            f"{self.base_url}/histominute?fsym=USD&tsym=PLN&limit=20"
        )
        if response.status_code != 200:
            raise CryptocompareClientException(
                f"Cryptocompare API returned status code {response.status_code}"
            )
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError:
            logger.info(response.text)
            raise CannotParseResponse()
        # logger.info(response)
        return response_json

    def calculate_mean_of_mids_from_last_20_minutes(self, data):
        # logger.info(data)
        if "Data" not in data:
            raise CryptocompareClientException(f"No data in response")

        data_frame = pd.DataFrame(data["Data"])

        # keep only high and low columns
        if "high" not in data_frame.columns:
            raise CryptocompareClientException(f"No high column in response")
        if "low" not in data_frame.columns:
            raise CryptocompareClientException(f"No low column in response")

        data_frame = data_frame[["high", "low"]]

        # create a new column 'mid' with the mean of high and low
        data_frame["mid"] = (data_frame["high"] + data_frame["low"]) / 2

        # calculate mean of mid column
        return Decimal(data_frame["mid"].mean())
