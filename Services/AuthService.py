from Processing.authorize import authorizeOwner
from .UserService import UserService
from Models.RequestModels.GetModels import RequestModels as rm


class AuthService:
    @staticmethod
    @authorizeOwner
    def update_privileges(request: rm.User.Privileges.Update):
        us = UserService.get_from_db(request.target_uid)
        us = UserService(request.to_user(us.user))
        us.update()

