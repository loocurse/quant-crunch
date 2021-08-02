import asyncio
import json
import os
import threading
from datetime import datetime, timezone

import alpaca_trade_api
from alpaca_trade_api.entity import Entity
from polygon import STOCKS_CLUSTER, RESTClient, WebSocketClient
from pymongo import MongoClient
from pymongo.database import Database
from redis import Redis

from utils.constants import API_KEY, Tickers
from utils.custom_types import (
    AggregateMinuteModel,
    ClosedPositionModel,
    FastAPIExtended,
    OpenPositionModel,
    OpenPositionMongoModel,
    RecommendationsMongoModel,
    TickersMongoModel,
)


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


def init_redis():
    if (redis_url := os.getenv("REDIS_URL")) is None:
        redis = Redis(host=os.getenv("REDIS_HOST") or "redis", port=6379)
    else:  # for heroku
        redis = Redis.from_url(redis_url)
    return redis


def init_redis_data(app: FastAPIExtended):
    get_tickers_metadata(app)
    db_open_positions = app.db.open_positions.count_documents({})
    redis_open_positions = app.redis.llen("open_positions")
    if db_open_positions != redis_open_positions:
        open_positions = [
            OpenPositionMongoModel(**i) for i in app.db.open_positions.find()
        ]
        app.redis.delete("open_positions")
        if open_positions:
            app.redis.rpush(
                "open_positions",
                *[json.dumps(i.dict(exclude={"id"})) for i in open_positions],
            )


def init_db():
    mongodb_uri = os.getenv("MONGO_ATLAS_URI")
    client = MongoClient(mongodb_uri)
    db = client.quantcrunch
    return db


class Alpaca:
    def __init__(self, db: Database, redis: Redis) -> None:
        self.rest = alpaca_trade_api.REST()
        self.stream = alpaca_trade_api.Stream()
        self.db = db
        self.redis = redis

    async def __trade_updates_callback(self, update: Entity):
        if update.event == "fill":
            order: dict = update.order
            side = order["side"]
            symbol = order["symbol"]
            capital = float(self.redis.hget(symbol, "capital"))
            total_cost = float(order["filled_qty"]) * float(order["filled_avg_price"])

            if side == "buy":
                new_capital = capital - total_cost
                self.redis.hmset(
                    symbol,
                    {
                        "buy_order": json.dumps(order),
                        "capital": new_capital,
                        "state": "sell",
                    },
                )
                pass
            elif side == "sell":
                new_capital = capital + total_cost
                buy_order = json.loads(self.redis.hget(symbol, "buy_order"))
                buy_price = buy_order["filled_avg_price"]
                pnl = (float(order["filled_avg_price"]) - buy_price) / buy_price * 100
                self.db.alpaca.find_one_and_update(
                    {"month": order["filled_at"][:7]},
                    {
                        "$push": {
                            "positions": {
                                "buy_order": buy_order,
                                "sell_order": order,
                                "pnl": pnl,
                            }
                        }
                    },
                    upsert=True,
                )
                self.redis.hmset(symbol, {"capital": new_capital, "state": "buy"})

        pass

    def buy_stock(self, recommendation: OpenPositionModel, capital: float):
        self.rest.submit_order(
            symbol=recommendation.symbol,
            side="buy",
            type="market",
            time_in_force="gtc",
            qty=capital // recommendation.entry_price,
            order_class="bracket",
            take_profit={"limit_price": recommendation.target_price},
            stop_loss={"stop_price": recommendation.stop_loss},
        )

    def run(self):
        self.stream.subscribe_trade_updates(self.__trade_updates_callback)
        asyncio.create_task(self.stream._run_forever())


class RecommendationWatcher(threading.Thread):
    def __init__(self, db: Database, redis: Redis, alpaca: Alpaca):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.db = db
        self.redis = redis
        self.alpaca = alpaca

    def run(self):
        with self.db.recommendations.watch() as stream:
            while stream.alive:
                if new_change := stream.try_next():
                    if new_change.get("operationType") == "insert":
                        document = RecommendationsMongoModel(
                            **new_change.get("fullDocument")
                        )
                        document.set_fields()
                        open_positions = [i.dict() for i in document.recommendations]
                        self.redis.rpush(
                            "open_positions",
                            *[json.dumps(i) for i in open_positions],
                        )
                        # self.db.open_positions.insert_many(open_positions)

                        for recommendation in document.recommendations:
                            if (
                                self.redis.hget(recommendation.symbol, "state").decode()
                                == "buy"
                            ):
                                capital = float(
                                    self.redis.hget(recommendation.symbol, "capital")
                                )
                                self.alpaca.buy_stock(recommendation, capital)
                    continue
                self.event.wait(10)
                if self.event.is_set():
                    break


def init_alpaca(app: FastAPIExtended):
    return Alpaca(app.db, app.redis)


def init_watcher(app: FastAPIExtended):
    watcher = RecommendationWatcher(app.db, app.redis, app.alpaca)
    watcher.start()
    return watcher


def init_polygon():
    client = RESTClient(API_KEY)
    return client


def init_socket(app: FastAPIExtended):
    # TODO
    # test implementation

    # AM for aggregate minute
    # A for aggregate second
    AGGREGATE_MINUTE_PARAMS = [f"AM.{i}" for i in Tickers]

    def parse_am_response(response: AggregateMinuteModel):
        # check if there are any open positions from recommendations
        # if there are open positions:
        #    check if either of the target price/stop loss price has been reached
        #    if reached:
        #        record the price and marked the position as closed
        #        remove the open entry from redis and db
        #        add the marked entry into the database
        open_positions_redis = app.redis.lrange("open_positions", 0, -1)
        open_positions = [
            OpenPositionModel(**json.loads(i)) for i in open_positions_redis
        ]
        for i, position in enumerate(open_positions):
            if position.symbol == response.sym:
                pnl, notes = None, None
                if response.l <= position.target_price <= response.h:
                    pnl = position.expected_profit
                    notes = "Reached target price"
                elif response.l <= position.stop_loss <= response.h:
                    pnl = (
                        (position.stop_loss - position.entry_price)
                        / position.entry_price
                        * 100
                    )
                    notes = "Reached stop loss"
                else:
                    continue

                close_timestamp = response.e / 1000
                closed_position = ClosedPositionModel(
                    **position.dict(),
                    pnl=pnl,
                    notes=notes,
                    close_timestamp=close_timestamp,
                )
                app.redis.lrem("open_positions", 1, open_positions_redis[i])
                app.db.open_positions.delete_one(
                    position.dict(include={"symbol", "open_timestamp"})
                )
                month_timestamp = (
                    datetime.fromtimestamp(close_timestamp, tz=timezone.utc)
                    .replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    .timestamp()
                )
                app.db.performance.find_one_and_update(
                    {"month": month_timestamp},
                    {
                        "$push": {"positions": closed_position.dict()},
                        "$inc": {"realized_pnl": pnl},
                    },
                    upsert=True,
                )

    def process_message_callback(response: str):
        messages: list[dict] = json.loads(response)
        for message in messages:
            if os.getenv("MODE") == "DEV":
                print(message, flush=True)  # requires flush when working in docker
            if message.get("ev") == "AM":
                parse_am_response(AggregateMinuteModel(**message))

    client = WebSocketClient(STOCKS_CLUSTER, API_KEY, process_message_callback)
    client.run_async()
    client.subscribe(*AGGREGATE_MINUTE_PARAMS)
    return client
