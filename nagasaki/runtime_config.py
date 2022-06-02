from decimal import Decimal
from pathlib import Path

from pydantic_yaml import YamlModel


class RuntimeConfig:
    class Data(YamlModel):
        delta_when_btc_only: float
        delta_when_pln_only: float

    def __init__(self):
        self.path = Path("runtime_config.yml")

    @property
    def data(self):
        return self.Data.parse_raw(self.path.read_text(encoding="utf-8"))

    @property
    def delta_when_btc_only(self):
        return self.data.delta_when_btc_only

    @property
    def delta_when_pln_only(self):
        return self.data.delta_when_pln_only