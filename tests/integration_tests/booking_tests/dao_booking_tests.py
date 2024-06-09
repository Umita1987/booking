from datetime import datetime

from booking.service import BookingService


async def test_add_get_booking():
    new_booking = await BookingService.add(
        user_id=2,
        room_id=2,
        date_from=datetime.strptime("2024-07-07", "%Y-%m-%d"),
        date_to=datetime.strptime("2024-07-20", "%Y-%m-%d"),
    )
    assert new_booking.user_id == 2
    assert new_booking.room_id == 2

    # Проверка добавления брони
    new_booking = await BookingService.find_by_id(new_booking.id)
    assert new_booking is not None

async def test_crude_booking():
    new_booking = await BookingService.add(
        user_id=2,
        room_id=2,
        date_from=datetime.strptime("2024-07-07", "%Y-%m-%d"),
        date_to=datetime.strptime("2024-07-20", "%Y-%m-%d"),
    )
    assert new_booking.user_id == 2
    assert new_booking.room_id == 2

    # Проверка добавления брони
    new_booking = await BookingService.find_by_id(new_booking.id)
    assert new_booking is not None

    # Удаление брони
    await BookingService.delete_by_id(id=new_booking.id, user_id =new_booking.user_id)
    find_deleted_booking = await BookingService.find_one_or_none(id=new_booking.id)
    assert find_deleted_booking is None
