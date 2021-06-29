import json
import os
from functools import wraps
from pathlib import Path
from typing import Dict

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from polygon import STOCKS_CLUSTER, RESTClient, WebSocketClient
from polygon.rest.models.definitions import AggResponse

load_dotenv()


def init_polygon_websocket():
    TICKERS = ["MSFT", "AAPL", "AMD"]
    AGGREGATE_MINUTE_PARAMS = [f"AM.{i}" for i in TICKERS]

    def process_message_callback(response: str):
        messages: list[Dict] = json.loads(response)
        for message in messages:
            if os.getenv("MODE") == "DEV":
                print(message)
            elif not message.get("status"):
                print(message)

    key = os.getenv("POLYGON_API_KEY")
    polygon_client = WebSocketClient(STOCKS_CLUSTER, key, process_message_callback)
    polygon_client.run_async()
    polygon_client.subscribe(*AGGREGATE_MINUTE_PARAMS)
    return polygon_client


def PolygonREST(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = os.getenv("POLYGON_API_KEY")
        with RESTClient(key) as client:
            return fn(client, *args, **kwargs)

    return wrapper


@PolygonREST
def get_aggregates(client: RESTClient):
    ticker = "AAPL"
    start = "2021-01-01"
    end = "2021-01-05"
    timespan = "hour"  # minute,hour,day,week,month,quarter,year
    multiplier = 1
    # Inaccurate typing from library
    res: AggResponse = client.stocks_equities_aggregates(
        ticker, multiplier, timespan, start, end
    )
    if res.status == "OK" and res.results_count > 0:
        print(res.results)


@PolygonREST
def get_snapshot(client: RESTClient):
    TICKERS = ["MSFT", "AAPL", "AMD"]
    res = client.stocks_equities_snapshot_all_tickers(tickers=",".join(TICKERS))
    if res.status == "OK" and res.count > 0:
        results = [
            dict((k, ticker[k]) for k in ("ticker", "min", "updated"))
            for ticker in res.tickers
        ]
        print(results)


def create_app():
    app = FastAPI()
    polygon_client: WebSocketClient or None = None

    @app.get("/")
    def get_index():
        # Get data from API/Data store
        return {"hello": "this returns a json object"}

    @app.on_event("startup")
    def startup_event():
        # polygon_client = init_polygon_websocket()
        get_snapshot()

    @app.on_event("shutdown")
    def shutdown_event():
        if polygon_client:
            polygon_client.close_connection()

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        f"{Path(__file__).stem}:app",
        host="0.0.0.0",
        port=5050,
        reload=os.getenv("MODE") == "DEV" and os.getenv("RELOAD"),
    )
