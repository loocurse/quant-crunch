import json
import os
from typing import Dict, TypedDict

from polygon import STOCKS_CLUSTER, WebSocketClient


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
