from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel
from redis import Redis
from starlette.requests import Request

from database import Database


class FastAPIExtended(FastAPI):
    redis: Redis
    db: Database


class RequestExtended(Request):
    app: FastAPIExtended


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class Signal(BaseModel):
    timestamp: str
    signal: str
    price: int
