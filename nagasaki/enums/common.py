from enum import Enum


class OrderActionEnum(str, Enum):
    CREATED = "CREATED"
    CANCELLED = "CANCELLED"


class ActionTypeEnum(str, Enum):
    CREATE = "CREATE"
    CANCEL = "CANCEL"
    NOOP = "NOOP"


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
