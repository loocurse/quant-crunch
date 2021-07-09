import json
import os

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from polygon.rest.client import RESTClient

from utils.constants import API_KEY, Tickers
from utils.custom_types import FastAPIExtended, ReferenceTickerDetails


def get_tickers_metadata(app: FastAPIExtended) -> dict[str, dict[str, str]]:
    # tickers_metadata = app.redis.get("tickers_metadata")
    tickers_metadata = None
    if tickers_metadata is None:
        tickers_metadata = {}
        for ticker in Tickers:
            res: ReferenceTickerDetails = app.polygon.reference_ticker_details(ticker)
            tickers_metadata[ticker] = {
                "name": res.name,
                "exchange": res.exchangeSymbol,
                "symbol": ticker,
            }
        app.redis.set("tickers_metadata", json.dumps(tickers_metadata))
        return tickers_metadata
    else:
        return json.loads(tickers_metadata)


def init_db():
    mongodb_uri = os.getenv("MONGO_ATLAS_URI")
    client = AsyncIOMotorClient(mongodb_uri)
    db = AIOEngine(motor_client=client, database="databasename")
    return db


def init_polygon():
    client = RESTClient(API_KEY)
    return client
