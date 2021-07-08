import os
from datetime import date

from fastapi import APIRouter
from pyrebase.pyrebase import PyreResponse

from services import get_tickers_metadata
from utils.constants import Tickers
from utils.custom_types import RequestExtended, Signal

api_router = APIRouter()


@api_router.get("/")
def get_index(request: RequestExtended):
    # Get data from API/Data store
    # print(request.app.redis.get("hello"))
    return {"hello": "this returns a json object"}


@api_router.get("/tickerlist")
def get_ticker_list(request: RequestExtended):
    """
    return list of tickers
    """
    tickers_metadata = get_tickers_metadata(request.app)
    SNAPSHOT_ALL_TICKERS_ENDPOINT = (
        "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers"
    )
    params = {"tickers": ",".join(Tickers), "apiKey": os.getenv("POLYGON_API_KEY")}
    res: dict = request.app.session.get(
        SNAPSHOT_ALL_TICKERS_ENDPOINT, params=params
    ).json()
    for snapshot in res.get("tickers"):
        tickers_metadata[snapshot.get("ticker")].update(
            {
                "todaysChange": snapshot.get("todaysChange"),
                "todaysChangePerc": snapshot.get("todaysChangePerc"),
            }
        )
    return {"tickerlist": list(tickers_metadata.values())}


@api_router.get("/predictions/{ticker}")
def get_predictions(request: RequestExtended, ticker: Tickers):
    # https://github.com/ktingyew/Code-Server/blob/2117292bb94df1dd307406a1326f1236dc2d621d/controllers/tickers.py
    # if action_taken: post to firebase in addition to telegram
    signals: list[PyreResponse] = request.app.db.child(ticker).get().each()
    for signal in signals:
        details = Signal(**signal.val())
        print(details.price)
        print(details.signal)
        print(details.timestamp)

    return {"ticker": ticker}


@api_router.get("/price/{ticker}")
def get_price(request: RequestExtended, ticker: Tickers):
    # If redis does not have the data
    # get the data from polygon
    multiplier = 1
    timespan = "minute"
    start = date(2021, 7, 7).isoformat()
    end = date(2021, 7, 7).isoformat()
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 10,
        "apiKey": os.getenv("POLYGON_API_KEY"),
    }
    data = request.app.session.get(
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start}/{end}",
        params=params,
    ).json()
    print(data)
