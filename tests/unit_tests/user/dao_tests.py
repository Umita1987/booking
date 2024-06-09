import pytest

from users.service import UserService

@pytest.mark.parametrize("user_id, email, is_exisist", [
    (1, "test@test.com", True),
    (2,  "artem@example.com", True),
    (5, "sailor101187@gmail.com", False)
])
async def test_find_user_by_id(user_id, email, is_exisist):
    user = await UserService.find_by_id(user_id)
    if is_exisist:
       assert user
       assert user.id == user_id
       assert user.email == email
       print(user.id)
    else:
        assert not user, "user not exist"
