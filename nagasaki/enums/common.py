from enum import Enum, auto


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
    BTC_PERPETUAL = auto()

    def __init__(self, market_1=None, market_2=None):
        self.market_1 = market_1
        self.market_2 = market_2


class SideTypeEnum(str, Enum):
    ASK = "ASK"
    BID = "BID"


class OfferCurrencyEnum(str, Enum):
    btc = "btc"
    pln = "pln"


class ActionEnum(str, Enum):
    SELL = "SELL"
    BUY = "BUY"


class MarketEnum(str, Enum):
    BTC = "BTC"
    PLN = "PLN"
