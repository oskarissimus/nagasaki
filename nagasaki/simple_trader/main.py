from time import sleep
from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.bitclude.dto import CreateRequestDTO, CancelRequestDTO
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.clients.yahoo_finance.core import YahooFinanceClient
from nagasaki.enums.common import ActionEnum, MarketEnum
from nagasaki.simple_trader.settings import Settings
from nagasaki.utils.common import round_decimals_down

settings = Settings()
b = BitcludeClient(
    bitclude_url_base="https://api.bitclude.com",
    bitclude_client_id=settings.bitclude_client_id,
    bitclude_client_key=settings.bitclude_client_key,
)
d = DeribitClient(
    deribit_url_base="https://www.deribit.com/api/v2",
    deribit_client_id=settings.deribit_client_id,
    deribit_client_secret=settings.deribit_client_secret,
)
y = YahooFinanceClient(api_key=settings.yahoo_finance_api_key)


def get_inventory_parameter(btc_mark_price_pln, balances):
    total_pln = float(balances["PLN"].active + balances["PLN"].inactive)
    total_btc = float(balances["BTC"].active + balances["BTC"].inactive)

    total_btc_value_in_pln = float(total_btc) * btc_mark_price_pln
    wallet_sum_in_pln = total_pln + total_btc_value_in_pln
    pln_to_sum_ratio = total_btc_value_in_pln / wallet_sum_in_pln  # values from 0 to 1
    return pln_to_sum_ratio * 2 - 1


def get_delta_adjusted_for_inventory_ask(inventory_parameter):
    A = -0.0035
    B = 0.0055
    res = A * inventory_parameter + B
    if res <= 0:
        raise Exception(f"Delta is too small for inventory parameter: {res}")
    return res


def get_delta_adjusted_for_inventory_bid(inventory_parameter):
    A = 0.0035
    B = 0.0055
    res = A * inventory_parameter + B
    if res <= 0:
        raise Exception(f"Delta is too small for inventory parameter: {res}")
    return res


def get_quoting(balances):
    USD_PLN = float(y.fetch_usd_pln_quote())
    BTC_USD = float(d.fetch_index_price_btc_usd())
    BTC_PLN = BTC_USD * USD_PLN
    INVENTORY = float(get_inventory_parameter(BTC_PLN, balances))

    BID = BTC_PLN * (1 - get_delta_adjusted_for_inventory_bid(INVENTORY))
    ASK = BTC_PLN * (1 + get_delta_adjusted_for_inventory_ask(INVENTORY))

    return BID, ASK


while True:
    sleep(10)

    # Cancel all open orders
    # If delta is unhedged then hedge
    # Create orders

    open_offers = b.fetch_active_offers()
    for offer in open_offers:
        b.cancel_order(CancelRequestDTO.from_bitclude_order(offer.to_bitclude_order()))
    sleep(3)
    balances = b.fetch_account_info().balances
    BID, ASK = get_quoting(balances)

    amount_ask = balances["BTC"].active
    rounded_v = round_decimals_down(amount_ask, 4)
    if rounded_v > 0.001:
        ask_order_to_create = CreateRequestDTO(
            action=ActionEnum.SELL,
            amount=amount_ask,
            rate=ASK,
            market1=MarketEnum.BTC,
            market2=MarketEnum.PLN,
            hidden=False,
        )
        b.create_order(ask_order_to_create)
    else:
        print("No bitcoins to sell")

    amount_bid = float(balances["PLN"].active) / BID
    rounded_v = round_decimals_down(amount_bid, 4)
    if rounded_v > 0:
        bid_order_to_create = CreateRequestDTO(
            action=ActionEnum.BUY,
            amount=amount_bid,
            rate=BID,
            market1=MarketEnum.BTC,
            market2=MarketEnum.PLN,
            hidden=False,
        )
        b.create_order(bid_order_to_create)
    else:
        print("No PLNS")
    sleep(50)
