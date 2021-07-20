from typing import Optional

from pydantic import Field, BaseModel

from .pyobjectid import PyObjectId
from .recommendations_mongo import ClosedPosition


class PerformanceMongo(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    month: float
    realized_pnl: float
    positions: list[ClosedPosition]


class PerformanceResponse(BaseModel):
    performance: list[PerformanceMongo]
