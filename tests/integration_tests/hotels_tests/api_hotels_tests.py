from httpx import AsyncClient
import pytest


@pytest.mark.parametrize("location,date_from,date_to,status_code,detail", [
    ("Altaj", "2025-01-10", "2025-01-01", 400, "The check-in date cannot be later than the check-out date"),
    ("Altaj", "2025-01-01", "2025-02-10", 400, "It is not possible to book a hotel for more than a month"),
    ("Altaj", "2025-01-01", "2025-01-10", 200, None),
])
async def test_get_hotels_by_location_and_time(
        location,
        date_from,
        date_to,
        status_code,
        detail,
        ac: AsyncClient,
):
    response = await ac.get(
        f"/hotels/{location}",
        params={
            "date_from": date_from,
            "date_to": date_to,
        })
    assert response.status_code == status_code, response.text
    if str(status_code).startswith("4"):
        assert response.json()["detail"] == detail