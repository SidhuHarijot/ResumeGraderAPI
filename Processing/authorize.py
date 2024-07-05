import Database.database as database
from functools import wraps


db = database.Database()

class Authorize:
    @staticmethod
    def checkAuth(uid: str, level: str) -> bool:
        is_admin = False
        is_owner = False
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
            user = cursor.fetchone()
            if not user:
                return False
            is_admin = user[4]
            is_owner = user[3]
        if (level=="ADMIN" and is_admin) or (level=="OWNER" and is_owner) or (level=="ADMIN" and is_owner):
            return True
        return False



def authorizeOwner(func):
    def wrapper(*args, **kwargs):
        auth_uid = args[0]
        if Authorize.checkAuth(auth_uid.auth_uid, "OWNER"):
            return func(*args, **kwargs)
        raise PermissionError("You do not have permission to access this resource.")
    return wrapper


def authorizeAdmin(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        if Authorize.checkAuth(request.auth_uid, "ADMIN"):
            return func(*args, **kwargs)
        raise PermissionError("You do not have permission to access this resource.")
    return wrapper
