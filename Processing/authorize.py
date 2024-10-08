import Database.database as database
from functools import wraps
from ServerLogging.serverLogger import Logger
from Errors.GetErrors import Errors as e


def log(msg, func):
    Logger.logService(msg, func)

def logError(*args):
    try:
        message = args[0]
        if len(args) == 2:
            e = ValueError(args[0])
            func = args[1]
        else:    
            e = args[1]
            func = args[2]
        message = f"{message}\n{traceback.format_exception(None, e, e.__traceback__)}"
        Logger.logMain(message, func, "ERROR")
    except Exception as e:
        Logger.logMain(f"Error in logError: {e}", "main.logError", "ERROR")
        Logger.logMain(f"Original error: {message}", "main.logError", "ERROR")


db = database.Database()

class Authorize:
    @staticmethod
    def checkAuth(uid: str, level: str) -> bool:
        is_admin = False
        is_owner = False
        user = database.Database.execute_query("SELECT * FROM users WHERE uid = %s", (uid,), True)[0]
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
    for arg in args:
        if isinstance(arg, str) and len(arg) != 0:
            return arg
    raise e.PermissionErrors.NoTokenError()

def authorizeOwner(func):
    def wrapper(*args, **kwargs):
        auth_uid = find_auth_id(*args, **kwargs)
        if Authorize.checkAuth(auth_uid, "OWNER"):
            log(f"authorized", "authorizeOwner")
            return func(*args, **kwargs)
        raise e.PermissionErrors.InvalidTokenError()
    return wrapper


def authorizeAdmin(func):
    def wrapper(*args, **kwargs):
        auth_uid = find_auth_id(*args, **kwargs)
        if Authorize.checkAuth(auth_uid, "ADMIN"):
            log(f"authorized", "authorizeAdmin")
            return func(*args, **kwargs)
        raise e.PermissionErrors.InvalidTokenError()
    return wrapper
