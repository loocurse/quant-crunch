import json
import os
import threading

from pymongo import MongoClient
from polygon import STOCKS_CLUSTER, RESTClient, WebSocketClient
from pymongo.database import Database

from utils.constants import API_KEY, Tickers
from utils.custom_types import FastAPIExtended, TickersMongoModel, AggregateMinuteModel


def get_tickers_metadata(app: FastAPIExtended) -> dict[str, dict[str, str]]:
    tickers_metadata = app.redis.get("tickers_metadata")

    if tickers_metadata is None:
        tickers_metadata = [TickersMongoModel(**i) for i in app.db.tickers.find()]
        tickers_metadata = dict(
            (i.symbol, i.dict(exclude={"id"})) for i in tickers_metadata
        )
        app.redis.set("tickers_metadata", json.dumps(tickers_metadata))
        return tickers_metadata
    else:
        return json.loads(tickers_metadata)


def init_db():
    mongodb_uri = os.getenv("MONGO_ATLAS_URI")
    client = MongoClient(mongodb_uri)
    db = client.quantcrunch
    return db


def init_watcher(db: Database):
    class RecommendationWatcher(threading.Thread):
        def __init__(self, db: Database):
            threading.Thread.__init__(self)
            self.event = threading.Event()
            self.db = db

        def run(self):
            with self.db.recommendations.watch() as stream:
                while stream.alive:
                    if document := stream.try_next():
                        print(
                            document
                        )  # dict -> keys to get: 'fullDocument', operationType == 'insert'
                        continue
                    # TODO add new recommendations as open positions
                    self.event.wait(10)
                    if self.event.is_set():
                        break

    watcher = RecommendationWatcher(db)
    watcher.start()
    return watcher


def init_polygon():
    client = RESTClient(API_KEY)
    return client


def init_socket():
    # TODO
    # receive minute based price update from socket
    # check if there are any open positions from recommendations
    # if there are open positions:
    #    check if either of the target price/stop loss price has been reached
    #    if reached:
    #        record the price and marked the position as closed
    #        add the entry into the database

    AGGREGATE_MINUTE_PARAMS = [f"AM.{i}" for i in Tickers]

    def parse_am_response(response: AggregateMinuteModel):
        # check for open positions in db/redis
        print(response)

    def process_message_callback(response: str):
        messages: list[dict] = json.loads(response)
        for message in messages:
            if os.getenv("MODE") == "DEV":
                print(message)
            if message.get("ev") == "AM":
                parse_am_response(AggregateMinuteModel(**message))

    client = WebSocketClient(STOCKS_CLUSTER, API_KEY, process_message_callback)
    client.run_async()
    client.subscribe(*AGGREGATE_MINUTE_PARAMS)
    return client
