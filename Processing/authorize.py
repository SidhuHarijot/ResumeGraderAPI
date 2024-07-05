import Database.database as database
from functools import wraps
from ServerLogging.serverLogger import Logger


def log(msg, func):
    Logger.logService(msg, func)

def logError(msg, exception, func):
    msg = f"{msg}. Exception: {exception}"
    Logger.logService(msg, func, "ERROR")


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

def find_auth_id(*args, **kwargs):
    for arg in args:
        if hasattr(arg, "auth_uid"):
            return arg.auth_uid
    for key, value in kwargs.items():
        if key == "auth_uid":
            return value
        if hasattr(value, "auth_uid"):
            return value.auth_uid
    return None

def authorizeOwner(func):
    def wrapper(*args, **kwargs):
        auth_uid = find_auth_id(*args, **kwargs)
        if not auth_uid:
            raise PermissionError("You do not have permission to access this resource.")
        if Authorize.checkAuth(auth_uid, "OWNER"):
            log(f"authorized", "authorizeOwner")
            return func(*args, **kwargs)
        raise PermissionError("You do not have permission to access this resource.")
    return wrapper


def authorizeAdmin(func):
    def wrapper(*args, **kwargs):
        auth_uid = find_auth_id(*args, **kwargs)
        if not auth_uid:
            raise PermissionError("You do not have permission to access this resource.")
        if Authorize.checkAuth(auth_uid, "ADMIN"):
            log(f"authorized", "authorizeAdmin")
            return func(*args, **kwargs)
        raise PermissionError("You do not have permission to access this resource.")
    return wrapper
