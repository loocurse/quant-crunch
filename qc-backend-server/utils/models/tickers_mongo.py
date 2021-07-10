from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .pyobjectid import PyObjectId


class TickersMongo(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    exchange: str
    symbol: str
