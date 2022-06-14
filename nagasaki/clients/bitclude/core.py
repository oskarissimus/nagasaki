import json
from datetime import datetime
from time import sleep
from typing import List

import ccxt
import ccxt_unmerged
import requests

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
from nagasaki.enums.common import MarketEnum
from nagasaki.exceptions import BitcludeClientException, CannotParseResponse
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
        self.last_500_request_times.append(datetime.now())
        self.last_500_request_times.log_request_times()
        response = requests.get(
            self.url_base,
            params={
                "method": "account",
                "action": "activeoffers",
                "id": self.client_id,
                "key": self.client_key,
            },
        )
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError as json_decode_error:
            raise CannotParseResponse(response.text) from json_decode_error
        if "success" in response_json and response_json["success"] is True:
            return [Offer(**offer) for offer in response_json["offers"]]
        raise BitcludeClientException(response_json)

    @staticmethod
    def _parse_response_as_dto(response: requests.Response, dto_class: type):
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError as json_decode_error:
            raise CannotParseResponse(response.text) from json_decode_error
        if "success" in response_json and response_json["success"] is True:
            return dto_class(**response_json)
        raise BitcludeClientException(response_json["message"])

    @staticmethod
    def _parse_orderbook_response(response: requests.Response) -> OrderbookResponseDTO:
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError as json_decode_error:
            raise CannotParseResponse(response.text) from json_decode_error
        return OrderbookResponseDTO(**response_json)

    def create_order(self, order: OrderMaker):
        try:
            self._create_order(CreateRequestDTO.from_order_maker(order))
        except ValueError as value_error:
            logger.warning(f"create_order interrupted, reason: {value_error}")

    def _create_order(self, order: CreateRequestDTO) -> CreateResponseDTO:
        logger.info(f"creating {order}")
        order_params = order.get_request_params()
        auth_params = self._auth_params
        params = {**order_params, **auth_params}
        self.last_500_request_times.append(datetime.now())
        self.last_500_request_times.log_request_times()
        response = requests.get(self.url_base, params=params)
        if response.status_code == 200:
            parsed_response = BitcludeClient._parse_response_as_dto(
                response, CreateResponseDTO
            )
            return parsed_response
        raise BitcludeClientException(response.text)

    def cancel_order(self, order: OrderMaker):
        self._cancel_order(CancelRequestDTO.from_order_maker(order))

    def _cancel_order(self, order: CancelRequestDTO) -> CancelResponseDTO:
        logger.info(f"cancelling {order}")
        order_params = order.get_request_params()
        auth_params = self._auth_params
        params = {**order_params, **auth_params}
        self.last_500_request_times.append(datetime.now())
        self.last_500_request_times.log_request_times()
        response = requests.get(self.url_base, params=params)
        if response.status_code == 200:
            parsed_response = BitcludeClient._parse_response_as_dto(
                response, CancelResponseDTO
            )
            return parsed_response
        raise BitcludeClientException(response.text)

    def cancel_and_wait(self, order: OrderMaker):
        self.cancel_order(order)
        self.wait_for_offer_cancellation(order.order_id)

    def wait_for_offer_cancellation(self, offer_id: int):
        while True:
            logger.info("waiting for offer cancellation")
            offers = self.fetch_active_offers()
            offer_numbers = [o.nr for o in offers]
            if offer_id not in offer_numbers:
                return True
            sleep(1)

    def fetch_orderbook(self, asset_symbol: MarketEnum) -> OrderbookResponseDTO:
        logger.info(f"fetching {asset_symbol} orderbook")
        # self.last_500_request_times.append(datetime.now())
        # self.last_500_request_times.log_request_times()
        asset_url_code = asset_symbol.lower()
        response = requests.get(
            f"{self.url_base}/stats/orderbook_{asset_url_code}pln.json"
        )
        if response.status_code == 200:
            parsed_response = BitcludeClient._parse_orderbook_response(response)
            return parsed_response
        raise BitcludeClientException(response.text)
