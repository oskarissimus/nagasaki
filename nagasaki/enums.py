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
