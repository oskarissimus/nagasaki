from enum import Enum, auto


class OrderActionEnum(str, Enum):
    CREATED = "CREATED"
    CANCELLED = "CANCELLED"


class ActionTypeEnum(str, Enum):
    CREATE = "CREATE"
    CANCEL = "CANCEL"
    NOOP = "NOOP"
    CANCEL_AND_WAIT = "CANCEL_AND_WAIT"


class InstrumentTypeEnum(int, Enum):
    BTC_PLN = auto()
    BTC_PERPETUAL = auto()


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
