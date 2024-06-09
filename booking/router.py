from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import TypeAdapter


from booking.schemas import SBooking, SNewBooking
from booking.service import BookingService
from exceptions import RoomCannotBeBooked
from tasks.tasks import send_booking_confirmation_email
from users.depends import get_current_user
from users.models import User
from fastapi_versioning import version


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.get("/{bookings_id}")
@version(1)
async def get_booking_user(bookings_id):
    return await BookingService.find_by_id(bookings_id)


@router.get("")
@version(1)

async def get_booking(user: User = Depends(get_current_user)):
    print(user, type(user), user.id, user.email)
    return await BookingService.find_all(user_id=1)


@router.get("/{room_id}")
@version(1)

async def get_booking_room(room_id) -> SBooking:
    return await BookingService.find_one_or_none(room_id=int(room_id))


@router.post("", status_code=201)
@version(1)

async def add_booking(
        booking: SNewBooking,
        background_tasks: BackgroundTasks,
        user: User = Depends(get_current_user),
):
    booking = await BookingService.add(
        user.id,
        booking.room_id,
        booking.date_from,
        booking.date_to,
    )
    if not booking:
        raise RoomCannotBeBooked
    # TypeAdapter и model_dump - это новинки версии Pydantic 2.0
    booking = TypeAdapter(SNewBooking).validate_python(booking).model_dump()
    send_booking_confirmation_email.delay(booking, user.email)
    # Celery - отдельная библиотека
    # send_booking_confirmation_email.delay(booking, user.email)
    # Background Tasks - встроено в FastAPI
    # background_tasks.add_task(send_booking_confirmation_email, booking, user.email)
    return booking


@router.delete("/{booking_id}")
@version(1)

async def delete_booking(booking_id: int, current_user: User = Depends(get_current_user)):
    await BookingService.delete_by_id(id=booking_id, user_id=current_user.id)
    return {"message": "Booking deleted successfully"}
