from typing import List

from dependency_injector.wiring import Provide, inject

from nagasaki.clients import YahooFinanceClient
from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.containers import Application
from nagasaki.database.database import Database
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.state import BitcludeState, DeribitState, State, YahooFinanceState
from nagasaki.strategy.abstract_strategy import AbstractStrategy
from nagasaki.strategy.market_making_strategy import MarketMakingStrategy


def initialize_states():
    logger.info("Initializing States")
    synchronize_bitclude_state()
    synchronize_deribit_state()
    synchronize_yahoo_finance_state()
    log_states()


@inject
def synchronize_bitclude_state(
    state: State = Provide[Application.states.state_provider],
    bitclude_state: BitcludeState = Provide[Application.states.bitclude_state_provider],
    bitclude_client: BitcludeClient = Provide[
        Application.clients.bitclude_client_provider
    ],
    strategies: List[AbstractStrategy] = Provide[
        Application.strategies.strategies_provider
    ],
    database: Database = Provide[Application.databases.database_provider],
):
    bitclude_state.account_info = bitclude_client.fetch_account_info()
    bitclude_state.exchange_balance = bitclude_client.fetch_exchange_balance()
    database.write_account_info_to_db(account_info=bitclude_state.account_info)
    bitclude_state.active_offers = bitclude_client.fetch_active_offers()

    orderbook_symbols = [
        strategy.symbol
        for strategy in strategies
        if isinstance(strategy, MarketMakingStrategy)
    ]
    for symbol in set(orderbook_symbols):
        bitclude_state.orderbooks[symbol] = bitclude_client.fetch_orderbook(
            symbol
        ).to_orderbook_rest()

    state.exchange_states["bitclude"] = bitclude_state


@inject
def synchronize_deribit_state(
    state: State = Provide[Application.states.state_provider],
    deribit_state: DeribitState = Provide[Application.states.deribit_state_provider],
    deribit_client: DeribitClient = Provide[
        Application.clients.deribit_client_provider
    ],
):
    runtime_config = RuntimeConfig()
    currency = runtime_config.hedging_instrument.market_1
    deribit_state.account_summary = deribit_client.fetch_account_summary(currency)
    deribit_state.exchange_balance = deribit_client.fetch_exchange_balance()
    deribit_state.mark_price[currency] = deribit_client.fetch_index_price_in_usd(
        runtime_config.market_making_instrument
    )

    state.exchange_states["deribit"] = deribit_state


@inject
def synchronize_yahoo_finance_state(
    state: State = Provide[Application.states.state_provider],
    yahoo_finance_state: YahooFinanceState = Provide[
        Application.states.yahoo_finance_state_provider
    ],
    yahoo_finance_client: YahooFinanceClient = Provide[
        Application.clients.yahoo_finance_client_provider
    ],
):
    yahoo_finance_state.mark_price[
        "USD/PLN"
    ] = yahoo_finance_client.fetch_usd_pln_quote()

    state.exchange_states["yahoo_finance"] = yahoo_finance_state


@inject
def log_states(
    state: State = Provide[Application.states.state_provider],
):
    runtime_config = RuntimeConfig()

    bitclude_state = state.exchange_states["bitclude"]
    logger.info(bitclude_state.account_info)
    for orderbook in bitclude_state.orderbooks.values():
        logger.info(orderbook)
    logger.info(f"{bitclude_state.active_offers=}")

    deribit_state = state.exchange_states["deribit"]
    currency = runtime_config.market_making_instrument.market_1
    logger.info(f"{currency}/USD: {deribit_state.mark_price[currency]}")

    yahoo_finance_state = state.exchange_states["yahoo_finance"]
    logger.info(f"USD/PLN: {yahoo_finance_state.mark_price['USD/PLN']:.2f}")
