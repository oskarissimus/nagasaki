from typing import List

from dependency_injector.wiring import Provide, inject

from nagasaki.containers import Application
from nagasaki.database import Database
from nagasaki.logger import logger
from nagasaki.strategy.abstract_strategy import AbstractStrategy


@inject
def execute_all_strategies(
    strategies: List[AbstractStrategy] = Provide[
        Application.strategies.strategies_provider
    ],
    database: Database = Provide[Application.databases.database_provider],
):
    logger.debug("strategy execution requested")
    for strategy in strategies:
        order = strategy.execute()
        if order:
            database.save_order(order)
