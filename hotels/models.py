from sqlalchemy import Column, Integer, String, JSON

from database import Base


class Hotel(Base):
    __tablename__ = "hotel"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    services = Column(JSON)
    rooms_quantity = Column(Integer, nullable=False)
    image_id = Column(Integer, nullable=False)









