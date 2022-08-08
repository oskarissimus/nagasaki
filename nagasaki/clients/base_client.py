import abc
from decimal import Decimal
from typing import List, Optional, Dict, Any

import ccxt
import ccxt_unmerged  # pylint: disable=unused-import
import requests
from requests.adapters import HTTPAdapter, Retry

from nagasaki.clients.bitclude.dto import (
    AccountInfo,
    CancelRequestDTO,
    CreateRequestDTO,
    Offer,
    OrderbookResponseDTO, )
from nagasaki.clients.dto import ExchangeBalance
from nagasaki.enums.common import InstrumentTypeEnum, Symbol
from nagasaki.logger import logger
from nagasaki.models.bitclude import AccountSummary, OrderMaker


def bitclude_params_parser(params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "hidden": str(int(params["hidden"])),
        "post_only": str(int(params["post_only"])),
    }


def deribit_params_parser(params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "hidden": params["hidden"],
        "post_only": params["post_only"],
    }


PARAMS_PARSING_FUNCTIONS = {
    "deribit": deribit_params_parser,
    "bitclude": bitclude_params_parser
}

class BaseClient(abc.ABC):
    def __init__(
        self,
        exchange_id: str,
        client_id: Optional[str] = None,
        client_key: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        exchange = getattr(ccxt, exchange_id)
        self.ccxt_connector = exchange(
            {"apiKey": client_key, "uid": client_id, "secret": client_secret}
        )
        adapter = HTTPAdapter(max_retries=Retry())
        session = requests.Session()
        session.mount("https://", adapter)
        self.ccxt_connector.session = session
        self.params_parsing_function = PARAMS_PARSING_FUNCTIONS[exchange_id]

    def fetch_account_summary(self, currency: str) -> AccountSummary:
        response = self.ccxt_connector.fetch_balance({"currency": currency})
        return AccountSummary(**response["info"]["result"])

    def fetch_account_info(self) -> AccountInfo:
        logger.info("fetching account info")
        response = self.ccxt_connector.fetch_balance()
        return AccountInfo(**response["info"])

    def fetch_exchange_balance(self) -> ExchangeBalance:
        logger.info("fetching exchange balance")
        response = self.ccxt_connector.fetch_balance()
        return ExchangeBalance(**response)

    def fetch_active_offers(self) -> List[Offer]:
        logger.info("fetching active offers")
        response = self.ccxt_connector.fetch_open_orders()
        return [Offer(**offer["info"]) for offer in response]

    def create_order(self, order: OrderMaker):
        logger.info(f"creating {order}")
        self.ccxt_connector.create_order(
            **CreateRequestDTO.from_order_maker(order).to_kwargs(self.params_parsing_function)
        )

    def cancel_order(self, order: OrderMaker):
        logger.info(f"cancelling {order}")
        self.ccxt_connector.cancel_order(
            **CancelRequestDTO.from_order_maker(order).to_method_params()
        )

    def fetch_orderbook(self, symbol: Symbol) -> OrderbookResponseDTO:
        logger.info(f"fetching {symbol} orderbook")
        response = self.ccxt_connector.fetch_order_book(symbol.value)
        return OrderbookResponseDTO(**response)

    def fetch_index_price_in_usd(self, instrument: InstrumentTypeEnum) -> Decimal:
        symbol = f"{instrument.market_1}/USD:{instrument.market_1}"
        response = self.ccxt_connector.fetch_ticker(symbol)
        return Decimal(response["info"]["index_price"])
