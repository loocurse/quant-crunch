import json
import os

from utils.constants import Tickers
from utils.custom_types import FastAPIExtended


def get_tickers_metadata(app: FastAPIExtended) -> dict[str, dict[str, str]]:
    tickers_metadata = app.redis.get("tickers_metadata")
    if tickers_metadata is None:
        TICKER_DETAILS_ENDPOINT = "https://api.polygon.io/v1/meta/symbols/{}/company"
        params = {"apiKey": os.getenv("POLYGON_API_KEY")}
        tickers_metadata = {}
        for ticker in Tickers:
            res: dict = app.session.get(
                TICKER_DETAILS_ENDPOINT.format(ticker), params=params
            ).json()
            name, exchange = res.get("name"), res.get("exchangeSymbol")
            tickers_metadata[ticker] = {
                "name": name,
                "exchange": exchange,
                "symbol": ticker,
            }
        app.redis.set("tickers_metadata", json.dumps(tickers_metadata))
        return tickers_metadata
    else:
        return json.loads(tickers_metadata)
