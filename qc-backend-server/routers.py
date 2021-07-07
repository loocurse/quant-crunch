from fastapi import APIRouter
from pyrebase.pyrebase import PyreResponse

from constants import Tickers
from custom_types import RequestExtended, Signal

api_router = APIRouter()


@api_router.get("/")
def get_index(request: RequestExtended):
    # Get data from API/Data store
    # print(request.app.redis.get("hello"))
    return {"hello": "this returns a json object"}


@api_router.get("/predictions/{ticker}")
def get_predictions(request: RequestExtended, ticker: Tickers):
    # https://github.com/ktingyew/Code-Server/blob/2117292bb94df1dd307406a1326f1236dc2d621d/controllers/tickers.py
    # if action_taken: post to firebase in addition to telegram
    signals: list[PyreResponse] = request.app.db.child(ticker).get().each()
    for signal in signals:
        details = Signal(signal.val())
        print(details.price)
        print(details.signal)
        print(details.timestamp)

    return {"ticker": ticker}
