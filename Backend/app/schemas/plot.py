from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PlotPoint(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude must be between -90 and 90")
    lng: float = Field(..., ge=-180.0, le=180.0, description="Longitude must be between -180 and 180")
    timestamp: Optional[str] = None


class PlotCreate(BaseModel):
    id: str = Field(..., description="Client generated UUID for idempotent sync")
    plot_name: str = Field(..., min_length=1, max_length=100)
    points: List[PlotPoint] = Field(..., min_items=3)
    area_sqm: float
    area_acres: float
    area_cents: float
    perimeter_m: float


class PlotUpdate(BaseModel):
    plot_name: Optional[str] = Field(None, min_length=1, max_length=100)
    points: Optional[List[PlotPoint]] = Field(None, min_items=3)
    area_sqm: Optional[float] = None
    area_acres: Optional[float] = None
    area_cents: Optional[float] = None
    perimeter_m: Optional[float] = None


class PlotResponse(BaseModel):
    id: str
    farmer_id: int
    plot_name: str
    points: List[PlotPoint]
    area_sqm: float
    area_acres: float
    area_cents: float
    perimeter_m: float
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
