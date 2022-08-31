from typing import List

from dependency_injector.wiring import Provide, inject

from nagasaki.containers import Application
from nagasaki.database import Database
from nagasaki.exceptions import SkippableStrategyException
from nagasaki.logger import logger
from nagasaki.strategy.abstract_strategy import AbstractStrategy
from nagasaki.strategy.market_making_strategy import MarketMakingStrategy


@inject
def execute_all_strategies(
    strategies: List[AbstractStrategy] = Provide[
        Application.strategies.strategies_provider
    ],
    database: Database = Provide[Application.databases.database_provider],
):
    logger.debug("strategy execution requested")
    for strategy in strategies:
        try:
            order = strategy.execute()
            if order:
                database.save_order(order)
        except SkippableStrategyException:
            if isinstance(strategy, MarketMakingStrategy):
                logger.info(f"skipping MarketMakingStrategy: {strategy.side}")
            else:
                logger.info(f"skipping strategy: {strategy.__class__.__name__}")
