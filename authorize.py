import database


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
            is_owner = user[5]
        if level=="ADMIN" and is_admin:
            return True
        if level=="OWNER" and is_owner:
            return True
        return False
