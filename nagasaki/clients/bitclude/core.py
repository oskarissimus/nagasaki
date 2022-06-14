from datetime import datetime
from typing import List

import ccxt
import ccxt_unmerged
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from nagasaki.clients.base_client import BaseClient, OrderMaker
from nagasaki.clients.bitclude.dto import (
    AccountInfo,
    CancelRequestDTO,
    CancelResponseDTO,
    CreateRequestDTO,
    CreateResponseDTO,
    Offer,
    OrderbookResponseDTO,
)
from nagasaki.enums.common import Symbol
from nagasaki.logger import logger


class RequestTimesRingBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer: List[datetime] = []

    def append(self, value):
        if len(self.buffer) == self.size:
            self.buffer.pop(0)
        self.buffer.append(value)

    def get_request_rate_per_second_for_last_minute(self):
        requests_newer_than_1_minute = [
            request_time
            for request_time in self.buffer
            if (datetime.now() - request_time).seconds < 60
        ]
        return len(requests_newer_than_1_minute) / 60

    def get_difference_between_last_two_requests(self):
        if len(self.buffer) < 2:
            return None
        return self.buffer[-1] - self.buffer[-2]

    def get_minimum_difference_between_any_two_requests(self):
        if len(self.buffer) < 2:
            return None
        return min(
            [self.buffer[i] - self.buffer[i - 1] for i in range(1, len(self.buffer))]
        )

    def get_requests_number_in_last_10_minutes(self):
        requests_newer_than_10_minutes = [
            request_time
            for request_time in self.buffer
            if (datetime.now() - request_time).seconds < 600
        ]
        return len(requests_newer_than_10_minutes)

    def get_requests_rate_per_10_minutes_for_last_1_minute(self):
        requests_newer_than_1_minute = [
            request_time
            for request_time in self.buffer
            if (datetime.now() - request_time).seconds < 60
        ]
        return len(requests_newer_than_1_minute) * 10

    def log_request_times(self):
        logger.info(self.get_requests_number_in_last_10_minutes())
        logger.info(self.get_requests_rate_per_10_minutes_for_last_1_minute())


class BitcludeClient(BaseClient):
    """
    Client holds url, and credentials. It makes requests and parses them into models.
    """

    def __init__(
        self,
        client_id: str,
        client_key: str,
        url_base: str = "https://api.bitclude.com",
    ):
        self.url_base = url_base
        self.client_id = client_id
        self.client_key = client_key
        self.last_500_request_times = RequestTimesRingBuffer(500)

        self.ccxt_connector = ccxt.bitclude({"apiKey": client_key, "uid": client_id})
        adapter = HTTPAdapter(max_retries=Retry())
        session = requests.Session()
        session.mount("https://", adapter)
        self.ccxt_connector.session = session

        self._auth_params = {
            "id": self.client_id,
            "key": self.client_key,
        }

    def fetch_account_info(self) -> AccountInfo:
        logger.info("fetching account info")
        response = self.ccxt_connector.fetch_balance()
        return AccountInfo(**response["info"])

    def fetch_active_offers(self) -> List[Offer]:
        logger.info("fetching active offers")
        response = self.ccxt_connector.fetch_open_orders()
        return [Offer(**offer["info"]) for offer in response]

    def create_order(self, order: OrderMaker) -> CreateResponseDTO:
        logger.info(f"creating {order}")
        response = self.ccxt_connector.create_order(
            **CreateRequestDTO.from_order_maker(order).to_method_params()
        )
        return CreateResponseDTO(**response["info"])

    def cancel_order(self, order: OrderMaker) -> CancelResponseDTO:
        logger.info(f"cancelling {order}")
        response = self.ccxt_connector.cancel_order(
            **CancelRequestDTO.from_order_maker(order).to_method_params()
        )
        return CancelResponseDTO(**response)

    def fetch_orderbook(self, symbol: Symbol) -> OrderbookResponseDTO:
        logger.info(f"fetching {symbol} orderbook")
        response = self.ccxt_connector.fetch_order_book(symbol.value)
        return OrderbookResponseDTO(**response)
