from fastapi import APIRouter

from services import get_tickers_metadata
from utils.constants import Tickers
from utils.custom_types import RequestExtended, SnapshotModel, TickerlistModel

api_router = APIRouter()


@api_router.get("/")
def get_index(request: RequestExtended):
    # Get data from API/Data store
    # print(request.app.redis.get("hello"))
    return {"hello": "this returns a json object"}


@api_router.get("/tickerlist", response_model=TickerlistModel)
def get_ticker_list(request: RequestExtended):
    """
    return list of tickers
    """
    tickers_metadata = get_tickers_metadata(request.app)
    params = {"tickers": ",".join(Tickers)}
    res = request.app.polygon.stocks_equities_snapshot_all_tickers(**params)
    for snapshot in res.tickers:
        s = SnapshotModel(**snapshot)
        tickers_metadata[s.ticker].update(
            {
                "change": s.todaysChange,
                "changePerc": s.todaysChangePerc,
            }
        )
    return {"tickerlist": list(tickers_metadata.values())}


@api_router.get("/predictions")
def get_predictions(request: RequestExtended):
    """
    {
        date: [
            {
                ticker: ,
                targetPrice: ,
                currentPrice: ,
            }
        ],
    }
    """
    pass
