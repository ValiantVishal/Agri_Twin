from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

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