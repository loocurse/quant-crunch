import json
import os
from functools import wraps
from typing import Dict, TypedDict

from polygon import STOCKS_CLUSTER, RESTClient, WebSocketClient
from polygon.rest.models.definitions import AggResponse


class AMResponse(TypedDict):
    ev: str
    sym: str
    v: int
    av: int
    op: int
    vw: int
    o: int
    c: int
    h: int
    l: int
    a: int
    z: int
    s: int
    e: int


def init_polygon_websocket():
    TICKERS = ["MSFT", "AAPL", "AMD"]
    AGGREGATE_MINUTE_PARAMS = [f"AM.{i}" for i in TICKERS]

    def parse_am_response(response: AMResponse):
        stored_data = dict(
            (k, response[k]) for k in ("v", "o", "c", "h", "l", "s", "e")
        )
        r.rpush(response["sym"], stored_data)

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
def get_aggregates(client: RESTClient, ticker="AAPL"):
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
