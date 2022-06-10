from dependency_injector import containers, providers

from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.clients.yahoo_finance.core import YahooFinanceClient
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.settings import Settings
from nagasaki.settings.factory import create_strategies
from nagasaki.state import BitcludeState, DeribitState, YahooFinanceState


class Clients(
    containers.DeclarativeContainer
):  # pylint: disable=(too-few-public-methods, c-extension-no-member)
    config = providers.Configuration()
    bitclude_client_provider = providers.Singleton(
        BitcludeClient,
        client_id=config.bitclude_id,
        client_key=config.bitclude_key,
        url_base=config.bitclude_url_base,
    )
    deribit_client_provider = providers.Singleton(
        DeribitClient,
        client_id=config.deribit_client_id,
        client_secret=config.deribit_client_secret,
        url_base=config.deribit_url_base,
    )
    yahoo_finance_client_provider = providers.Singleton(
        YahooFinanceClient,
        api_key=config.yahoo_finance_api_key,
        email=config.yahoo_finance_api_email,
        password=config.yahoo_finance_api_password,
        url_base=config.yahoo_finance_api_url_base,
    )


class States(containers.DeclarativeContainer):
    bitclude_state_provider = providers.Singleton(BitcludeState)
    deribit_state_provider = providers.Singleton(DeribitState)
    yahoo_finance_state_provider = providers.Singleton(YahooFinanceState)


class Strategies(containers.DeclarativeContainer):
    clients = providers.DependenciesContainer()
    states = providers.DependenciesContainer()

    runtime_settings = RuntimeConfig().data
    strategies_config = runtime_settings.strategies

    strategies_provider = providers.Singleton(
        create_strategies,
        settings=strategies_config,
        bitclude_client=clients.bitclude_client_provider,
        deribit_client=clients.deribit_client_provider,
        bitclude_state=states.bitclude_state_provider,
        deribit_state=states.deribit_state_provider,
        yahoo_finance_state=states.yahoo_finance_state_provider,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[Settings()])

    clients = providers.Container(Clients, config=config)
    states = providers.Container(States)
    strategies = providers.Container(Strategies, clients=clients, states=states)
