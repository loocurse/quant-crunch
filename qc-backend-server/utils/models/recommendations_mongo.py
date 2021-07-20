from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pytz import timezone

from .pyobjectid import PyObjectId

ny_tz = timezone("America/New_York")


class OpenPosition(BaseModel):
    symbol: str
    target_price: float = Field(alias="targetPrice")
    entry_price: float = Field(alias="currentPrice")
    open_timestamp: Optional[int] = Field(alias="openTimestamp")
    stop_loss: Optional[float] = Field(alias="stopLoss")
    expected_profit: Optional[float] = Field(alias="expectedProfit")


class RecommendationsMongo(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    us_date: str = Field(alias="us-date")
    sg_date: str = Field(alias="sg-date")
    recommendations: Optional[list[OpenPosition]]

    @property
    def timestamp(self) -> float:
        return ny_tz.localize(datetime.fromisoformat(self.us_date)).timestamp()

    def set_fields(self):
        if self.recommendations:
            for recommendation in self.recommendations:
                recommendation.open_timestamp = self.timestamp
                recommendation.stop_loss = recommendation.entry_price * 0.9
                recommendation.expected_profit = (
                    (recommendation.target_price - recommendation.entry_price)
                    / recommendation.entry_price
                    * 100
                )


class RecommendationsResponse(BaseModel):
    results: list[OpenPosition]


class OpenPositionMongo(OpenPosition):
    id: Optional[PyObjectId] = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True


class ClosedPosition(OpenPosition):
    pnl: float
    notes: str
    close_timestamp: int = Field(alias="closeTimestamp")
