import os
from enum import auto

from .custom_types import AutoName


class Tickers(str, AutoName):
    AAPL = auto()
    BABA = auto()
    GOOG = auto()
    DIS = auto()
    SHOP = auto()
    C = auto()
    BX = auto()
    TSLA = auto()


API_KEY = os.getenv("POLYGON_API_KEY")