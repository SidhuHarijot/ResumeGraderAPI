from Processing.authorize import authorizeAdmin, authorizeOwner
from Database.UserDatabase import UserDatabase
from .UserService import UserService


class AuthService:
    @staticmethod
    @authorizeOwner
    def update_privileges(request):
        us = UserService.get_from_db(request.target_uid)
        us = UserService(request.to_user(us.user))
        us.update()

