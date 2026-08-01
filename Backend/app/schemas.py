from pydantic import BaseModel, Field
from pydantic import EmailStr
from typing import List, Optional
from datetime import datetime


class Register(BaseModel):
    name: str
    email: EmailStr
    password: str


class Login(BaseModel):
    email: EmailStr
    password: str


class ProfileCreate(BaseModel):
    phone: str
    state: str
    district: str
    village: str
    language: str
    farmerType: str
    experience: int
    crop: str
    irrigation: str
    soilType: str


# --- Plot Schemas ---

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


class ActivityLogCreate(BaseModel):
    plot_id: Optional[str] = None
    entry_text: str
    entry_language: str = Field(..., description="Language: 'ta' or 'en'")
    input_mode: str = Field(..., description="Input Mode: 'voice' or 'text'")
    created_at: Optional[datetime] = None


class ActivityLogResponse(BaseModel):
    id: int
    farmer_id: int
    plot_id: Optional[str]
    entry_text: str
    entry_language: str
    input_mode: str
    created_at: datetime

    class Config:
        from_attributes = True


class AIChatMessageResponse(BaseModel):
    id: int
    farmer_id: int
    plot_id: Optional[str]
    sender: str
    message_text: str
    created_at: datetime

    class Config:
        from_attributes = True