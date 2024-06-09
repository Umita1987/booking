from datetime import date, timedelta

from fastapi.logger import logger
from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from booking.models import Bookings
from database import async_session_maker, async_session_maker_nullpool
from exceptions import RoomFullyBooked
from hotels.rooms.models import Room
from service.base import BaseService



class BookingService(BaseService):
    model = Bookings

    @classmethod
    async def add(
            cls,
            user_id: int,
            room_id: int,
            date_from: date,
            date_to: date,
    ):

        try:
            async with async_session_maker() as session:
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
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
                    )
                    .cte("booked_rooms")
                )

                get_rooms_left = (
                    select(
                        (
                                Room.quantity
                                - func.count(booked_rooms.c.room_id).filter(
                            booked_rooms.c.room_id.is_not(None)
                        )
                        ).label("rooms_left")
                    )
                    .select_from(Room)
                    .join(booked_rooms, booked_rooms.c.room_id == Room.id, isouter=True)
                    .where(Room.id == room_id)
                    .group_by(Room.quantity, booked_rooms.c.room_id)
                )

                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                if rooms_left > 0:
                    get_price = select(Room.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Bookings)
                        .values(

                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(
                            Bookings.id,
                            Bookings.user_id,
                            Bookings.room_id,
                            Bookings.date_from,
                            Bookings.date_to,
                        )
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.mappings().one()
                else:
                    raise RoomFullyBooked
        except RoomFullyBooked:
            raise RoomFullyBooked
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot add booking"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def find_need_to_remind(days):
        async def find_need_to_remind(cls, days: int):
            """Список броней и пользователей, которым необходимо
            направить напоминание за `days` дней"""
            async with async_session_maker_nullpool() as session:
                query = (
                    select(Bookings).options(joinedload(Bookings.user))
                    # Фильтр ниже выдаст брони, до начала которых остается `days` дней
                    # В нашем пет-проекте можно брать все брони, чтобы протестировать функционал
                    .filter(date.today() == Bookings.date_from - timedelta(days=days))
                )
                result = await session.execute(query)
                return result.scalars().all()
