from typing import List
from Models.datamodels import *
from Factories.UserFactory import *
from database import *


class UserDatabase:
    @staticmethod
    def create_user(user: User):
        try:
            log(f"Creating user {user.uid}", "UserDatabase.create_user")
            print(UserFactory.to_db_row(user))
            query = """
                INSERT INTO users (uid, name, dob, is_owner, is_admin, phone_number, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = UserFactory.to_db_row(user)
            Database.execute_query(query, params)
            log(f"User {user.uid} created successfully", "UserDatabase.create_user")
        except Exception as e:
            logError(e, "UserDatabase.create_user")
            raise

    @staticmethod
    def get_user(uid: str) -> User:
        try:
            log(f"Retrieving user {uid}", "UserDatabase.get_user")
            query = "SELECT * FROM users WHERE uid = %s"
            result = Database.execute_query(query, (uid,), fetch=True)
            if result:
                user = UserFactory.from_db_row(result[0])
                log(f"User {uid} retrieved successfully", "UserDatabase.get_user")
                return user
            else:
                raise ValueError(f"User {uid} not found")
        except Exception as e:
            logError(e, "UserDatabase.get_user")
            raise

    @staticmethod
    def update_user(user: User):
        try:
            log(f"Updating user {user.uid}", "UserDatabase.update_user")
            query = """
                UPDATE users SET name = %s, dob = %s, is_owner = %s, is_admin = %s, phone_number = %s, email = %s
                WHERE uid = %s
            """
            params = UserFactory.to_db_row(user, False) + (user.uid,)
            Database.execute_query(query, params)
            log(f"User {user.uid} updated successfully", "UserDatabase.update_user")
        except Exception as e:
            logError(e, "UserDatabase.update_user")
            raise

    @staticmethod
    def delete_user(uid: str):
        try:
            log(f"Deleting user {uid}", "UserDatabase.delete_user")
            query = "DELETE FROM users WHERE uid = %s"
            Database.execute_query(query, (uid,))
            log(f"User {uid} deleted successfully", "UserDatabase.delete_user")
        except Exception as e:
            logError(e, "UserDatabase.delete_user")
            raise

    @staticmethod
    def get_all_users() -> List[User]:
        try:
            log("Retrieving all users", "UserDatabase.get_all_users")
            query = "SELECT * FROM users"
            results = Database.execute_query(query, fetch=True)
            users = UserFactory.from_db_rows(results)
            log("All users retrieved successfully", "UserDatabase.get_all_users")
            return users
        except Exception as e:
            logError(e, "UserDatabase.get_all_users")
            raise
