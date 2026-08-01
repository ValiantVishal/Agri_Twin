from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(255))


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    phone = Column(String(20))
    state = Column(String(100))
    district = Column(String(100))
    village = Column(String(100))
    language = Column(String(50))
    farmer_type = Column(String(100))
    experience = Column(Integer)
    crop = Column(String(100))
    irrigation = Column(String(100))
    soil_type = Column(String(100))

    user = relationship("User")


class Plot(Base):
    __tablename__ = "plots"

    id = Column(String(36), primary_key=True, index=True)  # Accept UUID string
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plot_name = Column(String(100), nullable=False)
    points = Column(JSON, nullable=False)  # List of {lat, lng, timestamp}
    area_sqm = Column(Float, nullable=False)
    area_acres = Column(Float, nullable=False)
    area_cents = Column(Float, nullable=False)
    perimeter_m = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)

    farmer = relationship("User")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plot_id = Column(String(36), ForeignKey("plots.id"), nullable=True)
    entry_text = Column(String, nullable=False)
    entry_language = Column(String(10), nullable=False)  # 'ta' or 'en'
    input_mode = Column(String(20), nullable=False)  # 'voice' or 'text'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    farmer = relationship("User")
    plot = relationship("Plot")