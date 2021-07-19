import os
from enum import auto

from .custom_types import AutoName


class Tickers(str, AutoName):
    AAPL = auto()
    AMZN = auto()
    BABA = auto()
    GOOG = auto()
    DIS = auto()
    SHOP = auto()
    BX = auto()
    C = auto()
    TSLA = auto()
    TLT = auto()
    NVDA = auto()


API_KEY = os.getenv("POLYGON_API_KEY")
