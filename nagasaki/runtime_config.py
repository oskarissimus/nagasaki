from decimal import Decimal
from pathlib import Path

from pydantic_yaml import YamlModel

from nagasaki.enums.common import InstrumentTypeEnum


class RuntimeConfig:
    class Data(YamlModel):
        delta_when_btc_only: str
        delta_when_pln_only: str
        market_making_instrument: str
        hedging_instrument: str

    def __init__(self, path: Path = None):
        self.path = path or Path(__file__).parent.parent / "runtime_config.yml"

    @property
    def data(self):
        return self.Data.parse_raw(self.path.read_text(encoding="utf-8"))

    @property
    def delta_when_btc_only(self):
        return Decimal(self.data.delta_when_btc_only)

    @property
    def delta_when_pln_only(self):
        return Decimal(self.data.delta_when_pln_only)

    @property
    def market_making_instrument(self):
        return InstrumentTypeEnum(self.data.market_making_instrument)

    @property
    def hedging_instrument(self):
        return InstrumentTypeEnum(self.data.hedging_instrument)
