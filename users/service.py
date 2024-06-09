from service.base import BaseService
from users.models import User


class UserService(BaseService):
    model = User
