from dependency_injector import containers, providers

from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.clients.yahoo_finance.core import YahooFinanceClient


class Clients(
    containers.DeclarativeContainer
):  # pylint: disable=(too-few-public-methods, c-extension-no-member)
    config = providers.Configuration()
    bitclude_client = providers.Singleton(
        BitcludeClient,
        client_id=config.bitclude_id,
        client_key=config.bitclude_key,
        url_base=config.bitclude_url_base,
    )
    deribit_client = providers.Singleton(
        DeribitClient,
        client_id=config.deribit_client_id,
        client_secret=config.deribit_client_secret,
        url_base=config.deribit_url_base,
    )
    yahoo_finance_client = providers.Singleton(
        YahooFinanceClient,
        api_key=config.yahoo_finance_api_key,
        email=config.yahoo_finance_api_email,
        password=config.yahoo_finance_api_password,
        url_base=config.yahoo_finance_api_url_base,
    )
