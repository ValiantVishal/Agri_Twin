from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from .database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100))

    email = Column(String(100), unique=True)

    password = Column(String(255))