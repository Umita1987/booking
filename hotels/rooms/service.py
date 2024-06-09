from datetime import date

from sqlalchemy import select, func, or_, and_

from booking.models import Bookings
from database import async_session_maker
from hotels.rooms.models import Room
from service.base import BaseService


class RoomService(BaseService):
    model = Room

    @classmethod
    async def get_all(cls, hotel_id: str, date_from: date, date_to: date):
        booked_rooms = (
            select(Bookings.room_id, func.count(Bookings.room_id).label("rooms_booked"))
            .select_from(Bookings)
            .where(
                or_(
                    and_(
                        Bookings.date_from >= date_from,
                        Bookings.date_from <= date_to,
                    ),
                    and_(
                        Bookings.date_from <= date_from,
                        Bookings.date_to > date_from,
                    ),
                ),
            )
            .group_by(Bookings.room_id)
            .cte("booked_rooms")
        )

        get_rooms = (
            select(
                Room.__table__.columns,
                (Room.price * (date_to - date_from).days).label("total_cost"),
                (Room.quantity - func.coalesce(booked_rooms.c.rooms_booked, 0)).label("rooms_left"),
            )
            .join(booked_rooms, booked_rooms.c.room_id == Room.id, isouter=True)
            .where(
                Room.hotel_id == hotel_id
            )
        )
        async with async_session_maker() as session:
            # logger.debug(get_rooms.compile(engine, compile_kwargs={"literal_binds": True}))
            rooms = await session.execute(get_rooms)
            return rooms.mappings().all()