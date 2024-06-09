from sqlalchemy import Column, Integer, ForeignKey, String, JSON

from database import Base


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    hotel_id = Column(ForeignKey("hotel.id"))
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    services = Column(JSON)
    quantity = Column(Integer)
    image_id = Column(Integer)



    def __str__(self):
        return f"Номер {self.name}"