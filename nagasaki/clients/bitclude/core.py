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


class BitcludeClient(BaseClient):
    """
    Client holds ccxt connector and credentials. It makes requests and parses them into models.
    """

    def __init__(
        self,
        client_id: str,
        client_key: str,
    ):
        self.ccxt_connector = ccxt.bitclude({"apiKey": client_key, "uid": client_id})
        adapter = HTTPAdapter(max_retries=Retry())
        session = requests.Session()
        session.mount("https://", adapter)
        self.ccxt_connector.session = session

    def fetch_account_info(self) -> AccountInfo:
        logger.info("fetching account info")
        response = self.ccxt_connector.fetch_balance()
        return AccountInfo(**response["info"])

    def fetch_active_offers(self) -> List[Offer]:
        logger.info("fetching active offers")
        response = self.ccxt_connector.fetch_open_orders()
        return [Offer(**offer["info"]) for offer in response]

    def create_order(self, order: OrderMaker):
        logger.info(f"creating {order}")
        response = self.ccxt_connector.create_order(
            **CreateRequestDTO.from_order_maker(order).to_method_params()
        )
        return response

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



