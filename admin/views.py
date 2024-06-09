from sqladmin import ModelView

from booking.models import Bookings
from users.models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email]
    column_details_exclude_list = [User.hashed_password]

    can_delete = False
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

class BookingsAdmin(ModelView,model=Bookings):
    column_list = [c.name for c in Bookings.__table__.c] + [Bookings.user]
    name = "Booking"
    name_plural = "Bookings"
