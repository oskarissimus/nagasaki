from unittest import mock

import pytest

from nagasaki.state import State


@pytest.fixture(name="client")
def fixture_client():
    return mock.Mock()


@pytest.fixture(name="state")
def fixture_state(bitclude_state, deribit_state, yahoo_finance_state):
    return State(
        exchange_states={
            "bitclude": bitclude_state,
            "deribit": deribit_state,
            "yahoo_finance": yahoo_finance_state,
        }
    )
