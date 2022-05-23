from datetime import datetime
import json
from time import sleep
from typing import List

import requests

from nagasaki.clients.base_client import OrderMaker, BaseClient
from nagasaki.clients.bitclude.dto import (
    AccountInfo,
    Offer,
    OrderbookResponseDTO,
    Ticker,
    CancelRequestDTO,
    CancelResponseDTO,
    CreateRequestDTO,
    CreateResponseDTO,
)
from nagasaki.enums.common import ActionTypeEnum
from nagasaki.event_manager import EventManager
from nagasaki.exceptions import BitcludeClientException, CannotParseResponse
from nagasaki.logger import logger
from nagasaki.models.bitclude import Action


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
        bitclude_url_base: str,
        bitclude_client_id: str,
        bitclude_client_key: str,
        event_manager: EventManager = None,
    ):
        self.bitclude_url_base = bitclude_url_base
        self.bitclude_client_id = bitclude_client_id
        self.bitclude_client_key = bitclude_client_key
        self.event_manager = event_manager or EventManager()
        self.last_500_request_times = RequestTimesRingBuffer(500)
        self._auth_params = {
            "id": self.bitclude_client_id,
            "key": self.bitclude_client_key,
        }

    def fetch_account_info(self) -> AccountInfo:
        logger.info("fetching account info")
        self.last_500_request_times.append(datetime.now())
        self.last_500_request_times.log_request_times()
        response = requests.get(
            self.bitclude_url_base,
            params={
                "method": "account",
                "action": "info",
                "id": self.bitclude_client_id,
                "key": self.bitclude_client_key,
            },
        )
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError as json_decode_error:
            logger.info(response.text)
            raise CannotParseResponse() from json_decode_error
        if response_json["success"] is True:
            return AccountInfo(**response_json)
        raise BitcludeClientException(response_json)

    def fetch_ticker_btc_pln(self) -> Ticker:
        response = requests.get(f"{self.bitclude_url_base}/stats/ticker.json")
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError as json_decode_error:
            raise CannotParseResponse(response.text) from json_decode_error
        return Ticker(**response_json["btc_pln"])

    def fetch_active_offers(self) -> List[Offer]:
        logger.info("fetching active offers")
        self.last_500_request_times.append(datetime.now())
        self.last_500_request_times.log_request_times()
        response = requests.get(
            self.bitclude_url_base,
            params={
                "method": "account",
                "action": "activeoffers",
                "id": self.bitclude_client_id,
                "key": self.bitclude_client_key,
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
        self._create_order(CreateRequestDTO.from_order_maker(order))

    def _create_order(self, order: CreateRequestDTO) -> CreateResponseDTO:
        logger.info(f"creating {order}")
        order_params = order.get_request_params()
        auth_params = self._auth_params
        params = {**order_params, **auth_params}
        self.last_500_request_times.append(datetime.now())
        self.last_500_request_times.log_request_times()
        response = requests.get(self.bitclude_url_base, params=params)
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
        response = requests.get(self.bitclude_url_base, params=params)
        if response.status_code == 200:
            parsed_response = BitcludeClient._parse_response_as_dto(
                response, CancelResponseDTO
            )
            return parsed_response
        raise BitcludeClientException(response.text)

    def cancel_and_wait(self, order: OrderMaker):
        self.cancel_order(order)
        self.wait_for_offer_cancellation(order.order_id)

    def execute_action(self, action: Action):
        if action.action_type == ActionTypeEnum.CREATE:
            self.create_order(CreateRequestDTO.from_bitclude_order(action.order))

        if action.action_type == ActionTypeEnum.CANCEL:
            self.cancel_order(CancelRequestDTO.from_bitclude_order(action.order))

        if action.action_type == ActionTypeEnum.CANCEL_AND_WAIT:
            self.cancel_order(CancelRequestDTO.from_bitclude_order(action.order))
            self.wait_for_offer_cancellation(action.order.order_id)

    def execute_actions_list(self, actions: List[Action]):
        for action in actions:
            self.execute_action(action)

    def wait_for_offer_cancellation(self, offer_id: int):
        while True:
            logger.info("waiting for offer cancellation")
            offers = self.fetch_active_offers()
            offer_numbers = [o.nr for o in offers]
            if offer_id not in offer_numbers:
                return True
            sleep(1)

    def fetch_orderbook(self) -> OrderbookResponseDTO:
        logger.info("fetching orderbook")
        # self.last_500_request_times.append(datetime.now())
        # self.last_500_request_times.log_request_times()
        response = requests.get(f"{self.bitclude_url_base}/stats/orderbook_btcpln.json")
        if response.status_code == 200:
            parsed_response = BitcludeClient._parse_orderbook_response(response)
            return parsed_response
        raise BitcludeClientException(response.text)
