from sqlalchemy import Column, Integer, String, Float
from database.database import Base


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    name = Column(String)
    description = Column(String)
