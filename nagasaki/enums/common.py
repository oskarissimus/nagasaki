from aenum import Enum


class OrderActionEnum(str, Enum):
    CREATED = "CREATED"
    CANCELLED = "CANCELLED"


class ActionTypeEnum(str, Enum):
    CREATE = "CREATE"
    CANCEL = "CANCEL"
    NOOP = "NOOP"
    CANCEL_AND_WAIT = "CANCEL_AND_WAIT"


class InstrumentTypeEnum(Enum):
    BTC_PLN = ("BTC", "PLN")
    ETH_PLN = ("ETH", "PLN")
    BTC_PERPETUAL = ("BTC", "PERPETUAL")
    ETH_PERPETUAL = ("ETH", "PERPETUAL")

    def __init__(self, market_1=None, market_2=None):
        self.market_1 = market_1
        self.market_2 = market_2

    @classmethod
    def from_str(cls, value):
        return cls(tuple(value.upper().split("_")))


class SideTypeEnum(str, Enum):
    ASK = "ASK"
    BID = "BID"


class Currency(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    PLN = "PLN"
    USD = "USD"

    @classmethod
    def _missing_(cls, name):
        """https://stackoverflow.com/a/42659222/"""
        for member in cls:
            if member.name.lower() == name.lower():
                return member


class Symbol(str, Enum):
    BTC_PLN = "BTC/PLN"
    ETH_PLN = "ETH/PLN"


class Side(str, Enum):
    SELL = "SELL"
    BUY = "BUY"


class MarketEnum(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    PLN = "PLN"


class Type(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
