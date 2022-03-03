import json
from time import sleep
from typing import List, Union
from xmlrpc.client import Boolean
from nagasaki.logger import logger
import requests
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.exceptions import BitcludeClientException, CannotParseResponse
from nagasaki.clients.bitclude.models import (
    AccountHistory,
    AccountHistoryItem,
    AccountInfo,
    ActionBuyActionsResponseDTO,
    ActionResponseDTO,
    ActionSellActionsResponseDTO,
    Offer,
    Ticker,
)
from nagasaki.models.bitclude import Action
from nagasaki.utils.common import round_decimals_down
import datetime
from nagasaki.event_manager import EventManager


class BitcludeClient:
    """
    Client holds url, and credentials. It makes requests and parses them into models.
    """

    def __init__(
        self,
        bitclude_url_base: str,
        bitclude_client_id: str,
        bitclude_client_key: str,
        event_manager: EventManager,
    ):
        self.bitclude_url_base = bitclude_url_base
        self.bitclude_client_id = bitclude_client_id
        self.bitclude_client_key = bitclude_client_key
        self.event_manager = event_manager

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
        else:
            raise BitcludeClientException(response_json)

    def fetch_ticker_btc_pln(self) -> Ticker:
        response = requests.get(f"{self.bitclude_url_base}/stats/ticker.json")
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError as json_decode_error:
            raise CannotParseResponse(response.text) from json_decode_error
        return Ticker(**response_json["btc_pln"])

    def create_order(
        self,
        amount_in_btc,
        rate,
        order_type,
        dry_run=False,
        hidden=True,
        post_only=True,
    ) -> Union[Offer, bool]:
        if order_type in ("buy", "sell"):
            rounded_amount_in_btc = round_decimals_down(amount_in_btc, 4)
            if dry_run:
                logger.info("DRY_RUN: ")
            if rounded_amount_in_btc == 0:
                logger.info(
                    f"too_small_order_amount_{order_type}_rate={rate:.0f}"
                    f"too_small_order_amount_{order_type}_amount={amount_in_btc:.8f}"
                )
                return False
            logger.info(
                f"created_order_{order_type}_rate={rate:.0f}"
                f"created_order_{order_type}_amount={amount_in_btc:.8f}"
            )
            if dry_run:
                return True

            response = requests.get(
                self.bitclude_url_base,
                params={
                    "method": "transactions",
                    "action": order_type,
                    "market1": "btc",
                    "market2": "pln",
                    "amount": rounded_amount_in_btc,
                    "rate": rate,
                    "post_only": "1" if post_only else "0",
                    "hidden": "1" if hidden else "0",
                    "id": self.bitclude_client_id,
                    "key": self.bitclude_client_key,
                },
            )
            try:
                response_json = response.json()
            except json.decoder.JSONDecodeError as json_decode_error:
                raise CannotParseResponse(response.text) from json_decode_error
            if response_json["success"] is True:
                parsed_reponse = ActionResponseDTO(**response_json)
                side = None
                if isinstance(parsed_reponse.actions, ActionSellActionsResponseDTO):
                    side = "ask"
                if isinstance(parsed_reponse.actions, ActionBuyActionsResponseDTO):
                    side = "bid"
                offer = Offer(
                    nr=parsed_reponse.actions.order,
                    currency1="btc",
                    currency2="pln",
                    amount=rounded_amount_in_btc,
                    price=rate,
                    id_user_open="myself",
                    time_open=datetime.datetime.now(),
                    offertype=side,
                )
                logger.info(f"CreateOrder: {parsed_reponse.actions.order}")
                self.event_manager.post_event("created_order", offer)
                return offer
            logger.info(response_json)
            return False
        else:
            logger.info("order type must be buy or sell")
            return False

    def create_order_sell(self, amount_in_btc, rate, dry_run=False, hidden=True):
        return self.create_order(
            amount_in_btc, rate, "sell", dry_run=dry_run, hidden=hidden, post_only=True
        )

    def create_order_buy(self, amount_in_btc, rate, dry_run=False, hidden=True):
        return self.create_order(
            amount_in_btc, rate, "buy", dry_run=dry_run, hidden=hidden, post_only=True
        )

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

    def cancel_offer(self, offer: Offer, dry_run=False):
        if dry_run:
            logger.info("DRY RUN: ")
        logger.info(
            f"cancelling {offer.offertype=} {offer.price=:.0f} {offer.amount=:.8f} {offer.nr=}"
        )
        if dry_run:
            return True
        response = requests.get(
            self.bitclude_url_base,
            params={
                "method": "transactions",
                "action": "cancel",
                "order": offer.nr,
                "typ": offer.offertype,
                "id": self.bitclude_client_id,
                "key": self.bitclude_client_key,
            },
        )
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError as json_decode_error:
            raise CannotParseResponse(response.text) from json_decode_error
        if response_json["success"] is True:
            return response_json
        logger.info(response_json)
        return False

    def wait_for_offer_cancellation(self, offer: Offer):
        while True:
            offers = self.fetch_active_offers()
            offer_numbers = [o.nr for o in offers]
            logger.info("waiting for offer cancellation")
            logger.info(offers)
            logger.info(offer)
            if offer.nr not in offer_numbers:
                return True
            sleep(1)

    def fetch_account_history(self) -> AccountHistory:
        response = requests.get(
            self.bitclude_url_base,
            params={
                "method": "account",
                "action": "history",
                "id": self.bitclude_client_id,
                "key": self.bitclude_client_key,
            },
        )
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError as json_decode_error:
            raise CannotParseResponse(response.text) from json_decode_error
        if response_json["success"] is True:
            return AccountHistory(
                items=[AccountHistoryItem(**item) for item in response_json["history"]]
            )
        raise BitcludeClientException(response_json)

    def execute_action(self, action: Action):
        if action.action_type == ActionTypeEnum.CREATE:
            order_type = "buy" if action.order.side == SideTypeEnum.BID else "sell"
            created_order = self.create_order(
                amount_in_btc=action.order.amount,
                rate=action.order.price,
                order_type=order_type,
            )

        if action.action_type == ActionTypeEnum.CANCEL:
            offer_to_cancel = Offer(
                nr=action.order.order_id,
                currency1="btc",
                currency2="pln",
                id_user_open="papiez_polak",
                amount=action.order.amount,
                price=action.order.price,
                offertype=action.order.side,
                time_open=datetime.datetime.now(),
            )
            self.cancel_offer(offer_to_cancel)

    def execute_actions_list(self, actions: List[Action]):
        for action in actions:
            self.execute_action(action)
