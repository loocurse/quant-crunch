import os
from enum import auto

from .custom_types import AutoName


class Tickers(str, AutoName):
    AAPL = auto()
    AMZN = auto()
    BABA = auto()
    BLK = auto()
    BX = auto()
    C = auto()
    GOOG = auto()
    NOK = auto()
    NVDA = auto()
    SHOP = auto()
    TLT = auto()


API_KEY = os.getenv("POLYGON_API_KEY")
