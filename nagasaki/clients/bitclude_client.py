from os import wait
import requests
from typing import List, Dict
from pydantic import BaseModel
from nagasaki.enums import (
    ActionTypeEnum,
    OrderActionEnum,
    SideTypeEnum,
)
from nagasaki.utils import round_decimals_down
import json
import datetime
from time import sleep
from nagasaki.schemas import Action


class BitcludeClientException(Exception):
    pass


class CannotParseResponse(BitcludeClientException):
    pass


# https://github.com/samuelcolvin/pydantic/issues/1303
class HashableBaseModel(BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class Ticker(BaseModel):
    ask: float
    bid: float


class Balance(BaseModel):
    active: float
    inactive: float


class AccountInfo(BaseModel):
    balances: Dict[str, Balance]


class AccountHistoryItem(HashableBaseModel):
    currency1: str
    currency2: str
    amount: float
    time_close: datetime.datetime
    price: float
    fee_taker: int
    fee_maker: int
    type: str
    action: str


class Offer(BaseModel):
    nr: str
    currency1: str
    currency2: str
    amount: float
    price: float
    id_user_open: str
    time_open: datetime.datetime
    offertype: str


class BitcludeClient:
    def __init__(
        self, bitclude_url_base: str, bitclude_client_id: str, bitclude_client_key: str
    ):
        self.bitclude_url_base = bitclude_url_base
        self.bitclude_client_id = bitclude_client_id
        self.bitclude_client_key = bitclude_client_key
        self.active_offers: List[Offer] = []
        self.account_info: AccountInfo = None

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
        except json.decoder.JSONDecodeError:
            print(response.text)
            raise CannotParseResponse()
        if response_json["success"] == True:
            return AccountInfo(**response_json)
        else:
            raise BitcludeClientException(response_json)

    def get_bitclude_btcs(self, account_info: AccountInfo) -> float:
        """
        B_active - nie są w zleceniach
        B_inactive - są w zleceniach
        return B_active + B_inactive
        """
        btc_active = account_info.balances["BTC"].active
        btc_inactive = account_info.balances["BTC"].inactive
        return btc_active + btc_inactive

    def get_bitclude_btcs_inactive(self, account_info: AccountInfo) -> float:
        return account_info.balances["BTC"].inactive

    def get_bitclude_btcs_active(self, account_info: AccountInfo) -> float:
        return account_info.balances["BTC"].active

    def get_bitclude_plns(self, account_info: AccountInfo) -> float:
        pln_active = account_info.balances["PLN"].active
        pln_inactive = account_info.balances["PLN"].inactive
        return pln_active + pln_inactive

    def get_bitclude_plns_active(self, account_info: AccountInfo) -> float:
        return account_info.balances["PLN"].active

    def fetch_ticker_btc_pln(self):
        response = requests.get(f"{self.bitclude_url_base}/stats/ticker.json")
        try:
            response_json = response.json()
        except json.decoder.JSONDecodeError:
            print(response.text)
            raise CannotParseResponse()
        return Ticker(**response_json["btc_pln"])

    def create_order(
        self,
        amount_in_btc,
        rate,
        order_type,
        dry_run=False,
        hidden=True,
        post_only=True,
    ):
        if order_type in ("buy", "sell"):
            rounded_amount_in_btc = round_decimals_down(amount_in_btc, 4)
            if dry_run:
                print("DRY_RUN: ", end="")
            if rounded_amount_in_btc == 0:
                print(
                    f"attempted_order_{order_type}_rate={rate:.0f}",
                    f"attempted_order_{order_type}_amount={amount_in_btc:.8f}",
                )
                return False
            print(
                f"created_order_{order_type}_rate={rate:.0f}",
                f"created_order_{order_type}_amount={amount_in_btc:.8f}",
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
            except json.decoder.JSONDecodeError:
                print(response.text)
                raise CannotParseResponse()
            if response_json["success"] == True:
                return response_json
            else:
                print(response_json)
                return False
        else:
            print("order type must be buy or sell")

    def create_order_sell(self, amount_in_btc, rate, dry_run=False, hidden=True):
        return self.create_order(
            amount_in_btc, rate, "sell", dry_run=dry_run, hidden=hidden
        )

    def create_order_buy(self, amount_in_btc, rate, dry_run=False, hidden=True):
        return self.create_order(
            amount_in_btc, rate, "buy", dry_run=dry_run, hidden=hidden
        )

    def create_market_order_buy(
        self, amount_in_btc: float, ticker_btc_pln: Ticker, dry_run=False
    ):
        rate = ticker_btc_pln.bid + ticker_btc_pln.bid * 0.0001
        return self.create_order(amount_in_btc, rate, "buy", dry_run=dry_run)

    def create_market_order_sell(
        self, amount_in_btc: float, ticker_btc_pln: Ticker, dry_run=False
    ):
        rate = ticker_btc_pln.ask - ticker_btc_pln.ask * 0.0001
        return self.create_order(amount_in_btc, rate, "sell", dry_run=dry_run)

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
        except json.decoder.JSONDecodeError:
            print(response.text)
            raise CannotParseResponse()
        if "success" in response_json and response_json["success"] == True:
            return [Offer(**offer) for offer in response_json["offers"]]
        else:
            raise BitcludeClientException(response_json)

    def cancel_offer(self, offer: Offer, dry_run=False):
        if dry_run:
            print("DRY RUN: ", end="")
        print(
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
        except json.decoder.JSONDecodeError:
            print(response.text)
            raise CannotParseResponse()
        if response_json["success"] == True:
            return response_json
        else:
            print(response_json)
            return False

    def wait_for_offer_cancellation(self, offer: Offer):
        while True:
            offers = self.fetch_active_offers()
            offer_numbers = [o.nr for o in offers]
            print("waiting for offer cancellation")
            print(offers)
            print(offer)
            if offer.nr not in offer_numbers:
                return True
            sleep(1)

    def fetch_account_history(self):
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
        except json.decoder.JSONDecodeError:
            print(response.text)
            raise CannotParseResponse()
        if response_json["success"] == True:
            return [AccountHistoryItem(**item) for item in response_json["history"]]
        else:
            raise BitcludeClientException(response_json)

    @staticmethod
    def get_account_history_increment(
        previous_account_history: List[AccountHistoryItem],
        current_account_history: List[AccountHistoryItem],
    ) -> List[AccountHistoryItem]:
        prev = set(previous_account_history)
        curr = set(current_account_history)
        return list(curr.difference(prev))

    def cancel_ask_offers_that_are_not_on_top(self, ASK: float, dry_run=False):
        for offer in self.active_offers:
            if offer.offertype == "ask" and offer.price > ASK:
                self.cancel_offer(offer, dry_run=dry_run)
                self.wait_for_offer_cancellation(offer)
                self.account_info.balances["BTC"].active += offer.amount
                self.active_offers.remove(offer)

    def cancel_all_ask_offers(self, dry_run=False):
        print("cancel_all_ask_offers")
        print(self.active_offers)
        for offer in self.active_offers:
            if offer.offertype == "ask":
                self.cancel_offer(offer, dry_run=dry_run)
                self.wait_for_offer_cancellation(offer)
                self.active_offers.remove(offer)

    def cancel_bid_offers_that_are_not_on_top(self, BID: float, dry_run=False):
        for offer in self.active_offers:
            if offer.offertype == "bid" and offer.price < BID:
                self.cancel_offer(offer, dry_run=dry_run)
                self.wait_for_offer_cancellation(offer)
                self.account_info.balances["PLN"].active += offer.amount * offer.price
                self.active_offers.remove(offer)

    def cancel_all_bid_offers(self, dry_run=False):
        print("cancel_all_bid_offers")
        print(self.active_offers)
        for offer in self.active_offers:
            if offer.offertype == "bid":
                self.cancel_offer(offer, dry_run=dry_run)
                self.wait_for_offer_cancellation(offer)
                self.active_offers.remove(offer)

    def get_inventory_parameter(
        self, account_info: AccountInfo, btc_mark_price_pln: float
    ):
        total_pln = (
            account_info.balances["PLN"].active + account_info.balances["PLN"].inactive
        )
        total_btc = (
            account_info.balances["BTC"].active + account_info.balances["BTC"].inactive
        )
        total_btc_value_in_pln = total_btc * btc_mark_price_pln
        wallet_sum_in_pln = total_pln + total_btc_value_in_pln
        pln_to_sum_ratio = (
            total_btc_value_in_pln / wallet_sum_in_pln
        )  # values from 0 to 1
        return pln_to_sum_ratio * 2 - 1

    def optimal_ask_spread(self, inventory_param):
        # TODO: Watch out for magic parameters. Refactor later
        """
        -0.018 and 0.01 are a and b respectively in ax + b
        """
        return max(-0.018 * inventory_param + 0.01, 0.002)

    def optimal_bid_spread(self, inventory_param):
        """
        0.018 and 0.01 are a and b respectively in ax + b
        """
        return max(0.018 * inventory_param + 0.01, 0.002)

    def execute_action(self, action: Action):
        # Fetching account info once and passing it to another methods
        # account_info = self.fetch_account_info()
        # amount_btc = self.get_bitclude_btcs_active(account_info)
        dry_run = True
        if dry_run:
            print(f"dry run ececuting on bitclude {action}")
            return
        if action.action_type == ActionTypeEnum.CREATE:
            order_type = "buy" if action.order.side == SideTypeEnum.BID else "sell"
            self.create_order(
                amount_in_btc=1, rate=action.order.price, order_type=order_type
            )
            # TODO: amount should be attribute of action not 1

    def execute_actions_list(self, actions: List[Action]):
        for action in actions:
            self.execute_action(action)
