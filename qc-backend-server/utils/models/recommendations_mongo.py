from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field
from pytz import timezone

from .pyobjectid import PyObjectId

ny_tz = timezone("America/New_York")


class PositionFromRecommendation(BaseModel):
    symbol: str
    target_price: float = Field(alias="targetPrice")
    entry_price: float = Field(alias="currentPrice")


class Position(BaseModel):
    symbol: str
    target_price: float
    entry_price: float
    open_timestamp: Optional[float]
    stop_loss: Optional[float]


class OpenPosition(Position):
    expected_profit: Optional[float]


class RecommendationsMongo(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    us_date: str = Field(alias="us-date")
    sg_date: str = Field(alias="sg-date")
    recommendations: Optional[list[Union[PositionFromRecommendation, OpenPosition]]]

    @property
    def timestamp(self) -> float:
        return ny_tz.localize(datetime.fromisoformat(self.us_date)).timestamp()

    def set_fields(self):
        if self.recommendations:
            new_recommendations = [
                OpenPosition(**i.dict()) for i in self.recommendations
            ]  # basically convert PositionFromRecommendation to OpenPosition cause 'entryPrice' is shown as 'currentPrice'
            for recommendation in new_recommendations:
                recommendation.open_timestamp = self.timestamp
                recommendation.stop_loss = recommendation.entry_price * 0.9
                recommendation.expected_profit = (
                    (recommendation.target_price - recommendation.entry_price)
                    / recommendation.entry_price
                    * 100
                )
            self.recommendations = new_recommendations


class RecommendationsResponse(BaseModel):
    results: list[OpenPosition]


class OpenPositionMongo(OpenPosition):
    id: Optional[PyObjectId] = Field(alias="_id")


class ClosedPosition(OpenPosition):
    pnl: float
    notes: str
    close_timestamp: float
