import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("name,email,password,status_code", [
    ("Kot1", "kot@pes.com", "kotopes", 201),
    ("Pes1", "pes@kot.com", "pesokot", 201),
    ("Pesokot1", "abcde", "pesokot", 422),
])
async def test_register_user(name, email, password, status_code, ac: AsyncClient):
    response = await ac.post("/auth/register", json={
        "name": name,
        "email": email,
        "password": password,
        "status_code": status_code
    })

    assert response.status_code == status_code, response.text


@pytest.mark.parametrize("name,email,password,status_code", [
    ("test", "test@test.com", "test", 200),
    ("artem", "artem@example.com", "artem", 200),
    ("wrong", "wrong@person.com", "artem", 401),
])
async def test_login_user(name,email, password, status_code, ac: AsyncClient):
    response = await ac.post("/auth/login", json={
        "name": name,
        "email": email,
        "password": password,
    })

    assert response.status_code == status_code, response.text