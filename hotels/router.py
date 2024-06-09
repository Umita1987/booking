from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache

from pydantic import parse_obj_as


from exceptions import DateFromCannotBeAfterDateTo, CannotBookHotelForLongPeriod
from hotels.schemas import SHotelInfo, SHotel
from hotels.service import HotelService

router = APIRouter(
    prefix="/hotels",
    tags=["Hotels"],
)


@router.get("/{location}")
@cache(expire=120)
async def get_hotels_by_location_and_time(
        location: str,
        date_from: date = Query(..., description=f"{datetime.now().date()}"),
        date_to: date = Query(..., description=f"{(datetime.now() + timedelta(days=14)).date()}"),
):
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod
    hotels = await HotelService.find_all(location, date_from, date_to)
    hotels_json = parse_obj_as(List[SHotelInfo], hotels)
    return hotels_json


@router.get("/id/{hotel_id}", include_in_schema=True)
# Этот эндпоинт используется для фронтенда, когда мы хотим отобразить все
# номера в отеле и информацию о самом отеле. Этот эндпоинт как раз отвечает за информацию
# об отеле.
# В нем нарушается правило именования эндпоинтов: конечно же, /id/ здесь избыточен.
# Тем не менее, он используется, так как эндпоинтом ранее мы уже задали получение
# отелей по их локации вместо id.
async def get_hotel_by_id(
    hotel_id: int,
) -> Optional[SHotel]:
    return await HotelService.find_one_or_none(id=hotel_id)
