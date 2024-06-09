from datetime import date, datetime, timedelta
from typing import List

from hotels.rooms.schmas import SRoomInfo
from hotels.rooms.service import RoomService
from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/hotels/rooms",
    tags=["Rooms"],
)

@router.get("/{hotel_id}/room")
async def get_rooms_by_time(
    hotel_id: int,
    date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(..., description=f"Например, {(datetime.now() + timedelta(days=14)).date()}"),
) -> List[SRoomInfo]:
    rooms = await RoomService.find_all(hotel_id, date_from, date_to)
    return rooms