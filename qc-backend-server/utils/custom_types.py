from enum import Enum

from fastapi import FastAPI
from odmantic import AIOEngine
from polygon import RESTClient
from polygon.rest.models.definitions import Definition
from redis import Redis
from starlette.requests import Request

from .models import SnapshotModel, TickerlistModel


class FastAPIExtended(FastAPI):
    redis: Redis
    db: AIOEngine
    polygon: RESTClient


class RequestExtended(Request):
    app: FastAPIExtended


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class ReferenceTickerDetails(Definition):
    active: str
    bloomberg: str
    ceo: str
    cik: str
    country: str
    description: str
    employees: str
    exchange: str
    exchangeSymbol: str
    figi: str
    hq_address: str
    hq_country: str
    hq_state: str
    industry: str
    lei: str
    listdate: str
    logo: str
    marketcap: str
    name: str
    phone: str
    sector: str
    sic: str
    similar: str
    symbol: str
    tags: str
    type: str
    updated: str
    url: str
