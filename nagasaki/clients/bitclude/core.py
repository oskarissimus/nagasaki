import json
from multiprocessing.connection import wait
from time import sleep
from typing import List

import requests
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


class BitcludeClient:
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

    def _get_auth_params(self):
        return {
            "id": self.bitclude_client_id,
            "key": self.bitclude_client_key,
        }

    def fetch_account_info(self) -> AccountInfo:
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

    def create_order(self, order: CreateRequestDTO) -> CreateResponseDTO:
        logger.info(f"creating {order}")
        order_params = order.get_request_params()
        auth_params = self._get_auth_params()
        params = {**order_params, **auth_params}
        response = requests.get(self.bitclude_url_base, params=params)
        if response.status_code == 200:
            parsed_response = BitcludeClient._parse_response_as_dto(
                response, CreateResponseDTO
            )
            return parsed_response
        raise BitcludeClientException(response.text)

    def cancel_order(self, order: CancelRequestDTO) -> CancelResponseDTO:
        logger.info(f"cancelling {order}")
        order_params = order.get_request_params()
        auth_params = self._get_auth_params()
        params = {**order_params, **auth_params}
        response = requests.get(self.bitclude_url_base, params=params)
        if response.status_code == 200:
            parsed_response = BitcludeClient._parse_response_as_dto(
                response, CancelResponseDTO
            )
            return parsed_response
        raise BitcludeClientException(response.text)

    def execute_action(self, action: Action):
        if action.action_type == ActionTypeEnum.CREATE:
            response = self.create_order(
                CreateRequestDTO.from_bitclude_order(action.order)
            )

        if action.action_type == ActionTypeEnum.CANCEL:
            response = self.cancel_order(
                CancelRequestDTO.from_bitclude_order(action.order)
            )

        if action.action_type == ActionTypeEnum.CANCEL_AND_WAIT:
            response = self.cancel_order(
                CancelRequestDTO.from_bitclude_order(action.order)
            )
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
        response = requests.get(f"{self.bitclude_url_base}/stats/orderbook_btcpln.json")
        if response.status_code == 200:
            parsed_response = BitcludeClient._parse_orderbook_response(response)
            return parsed_response
        raise BitcludeClientException(response.text)
