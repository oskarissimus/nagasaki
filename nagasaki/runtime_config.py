from pathlib import Path

from nagasaki.enums.common import InstrumentTypeEnum
from nagasaki.settings.runtime import RuntimeSettings


class RuntimeConfig:
    def __init__(self, path: Path = None):
        self.path = path or Path(__file__).parent.parent / "runtime_config.yml"

    @property
    def data(self):
        return RuntimeSettings.parse_raw(self.path.read_text(encoding="utf-8"))

    @property
    def market_making_instrument(self):
        return InstrumentTypeEnum.from_str(self.data.market_making_instrument)

    @property
    def hedging_instrument(self):
        return InstrumentTypeEnum.from_str(self.data.hedging_instrument)
