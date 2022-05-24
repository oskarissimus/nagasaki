from unittest import mock

import pytest


@pytest.fixture(name="client")
def fixture_client():
    return mock.Mock()
