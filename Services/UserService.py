from Models.DataModels.User import User
from .services import log, logError
from Models.RequestModels.GetModels import RequestModels as rm
from Processing.Factories.UserFactory import UserFactory
from Database.UserDatabase import UserDatabase
from typing import Dict
from Processing.authorize import authorizeAdmin, authorizeOwner


class UserService:
    user = None
    in_db = False

    def __init__(self, user: User=None, new_user: rm.User.Create = None, dict: Dict= None, json_str: str=None, db_row: str=None):
        log("Initializing UserService", "__init__")
        try:
            if dict or json_str:
                user = UserFactory.from_json(self, json_str)
            elif db_row:
                user = UserFactory.from_db_row(self, db_row)
            elif new_user:
                user = new_user.to_user()
            if user:
                self.user = user
                self.in_database()
            else:
                raise ValueError("No valid arguments provided to UserService constructor")
        except Exception as e:
            logError("Error in UserService __init__", e, "__init__")
            raise

    def save_to_db(self):
        log("Saving user to database", "save_to_db")
        try:
            if self.validate():
                if not self.in_db:
                    UserDatabase.create_user(self.user)
                else:
                    self.update()
        except Exception as e:
            logError("Error in UserService save_to_db", e, "save_to_db")
            raise

    @staticmethod
    def get_from_db(uid: str):
        log(f"Getting user from database with uid: {uid}", "get_from_db")
        try:
            return UserService(UserDatabase.get_user(uid))
        except Exception as e:
            logError("Error in UserService get_from_db", e, "get_from_db")
            raise

    @staticmethod
    def find(params: dict):
        log(f"Finding users with params: {params}", "find")
        try:
            return UserDatabase.find_users(params)
        except Exception as e:
            logError("Error in UserService find", e, "find")
            raise

    def update(self, request: rm.User.Update = None):
        log(f"Updating user: {self.user.uid}", "update")
        try:
            if request:
                self.user = request.to_user(self.user)
            if self.validate():
                UserDatabase.update_user(self.user)
        except Exception as e:
            logError("Error in UserService update", e, "update")
            raise

    def to_json(self):
        log(f"Converting user to JSON: {self.user.uid}", "to_json")
        try:
            return UserFactory.to_json(self.user)
        except Exception as e:
            logError("Error in UserService to_json", e, "to_json")
            raise

    def in_database(self):
        log(f"Checking if user is in database: {self.user.uid}", "in_database")
        try:
            UserDatabase.get_user(self.user.uid)
            self.in_db = True
        except ValueError:
            self.in_db = False
        except Exception as e:
            logError("Error in UserService in_database", e, "in_database")
            raise

    def delete(self):
        log(f"Deleting user: {self.user.uid}", "delete")
        try:
            UserDatabase.delete_user(self.user.uid)
            self.in_db = False
        except Exception as e:
            logError("Error in UserService delete", e, "delete")
            raise

    @staticmethod
    def get_all():
        log("Getting all users from database", "get_all")
        try:
            return UserDatabase.get_all_users()
        except Exception as e:
            logError("Error in UserService get_all", e, "get_all")
            raise
    
    @staticmethod
    @authorizeAdmin
    def print_all(request):
        log("Printing all users", "print_all")
        try:
            users = UserDatabase.get_all_users()
            html_data = """
            <html>
            <head>
                <style>
                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    th, td {
                        border: 1px solid black;
                        padding: 8px;
                        text-align: left;
                    }
                    th {
                        background-color: #f2f2f2;
                    }
                </style>
            </head>
            <body>
                <table>
                    <tr>
                        <th>UID</th>
                        <th>Name</th>
                        <th>DOB</th>
                        <th>Owner</th>
                        <th>Admin</th>
                        <th>Phone</th>
                        <th>Email</th>
                        <th>Saved Jobs</th>
                    </tr>
            """

            for user in users:
                html_data += f"""
                    <tr>
                        <td>{user.uid}</td>
                        <td>{str(user.name)}</td>
                        <td>{str(user.dob)}</td>
                        <td>{user.is_owner}</td>
                        <td>{user.is_admin}</td>
                        <td>{user.phone_number}</td>
                        <td>{user.email}</td>
                        <td>{user.saved_jobs}</td>
                    </tr>
                """

            html_data += """
                </table>
            </body>
            </html>
            """

            return html_data
        except Exception as e:
            logError("Error in UserService print_all", e, "print_all")
            raise

    @staticmethod
    def from_json(json_str: str):
        log("Creating UserService from JSON", "from_json")
        try:
            return UserService(json_str=json_str)
        except Exception as e:
            logError("Error in UserService from_json", e, "from_json")
            raise

    @staticmethod
    def from_dict(dict: Dict):
        log("Creating UserService from dictionary", "from_dict")
        try:
            return UserService(dict=dict)
        except Exception as e:
            logError("Error in UserService from_dict", e, "from_dict")
            raise

    @staticmethod
    def from_db_row(db_row: str):
        log("Creating UserService from database row", "from_db_row")
        try:
            return UserService(db_row=db_row)
        except Exception as e:
            logError("Error in UserService from_db_row", e, "from_db_row")
            raise

    def validate(self):
        log(f"Validating user: {self.user.uid}", "validate")
        return True

    def __str__(self):
        return str(self.user)

    @staticmethod
    def save_job_from_request(request: rm.User.SaveJob):
        log(f"Saving job {request.job_id} for user {request.uid}", "save_job")
        try:
            user = UserService.get_from_db(request.uid)
            user.user.saved_jobs.append(request.job_id)
            user.save_to_db()
        except Exception as e:
            logError("Error in UserService save_job", e, "save_job")
            raise
    
    @staticmethod
    def remove_job_from_request(request: rm.User.SaveJob):
        log(f"Removing job {request.job_id} for user {request.uid}", "remove_job")
        try:
            user = UserService.get_from_db(request.uid)
            user.user.saved_jobs.remove(request.job_id)
            user.save_to_db()
        except Exception as e:
            logError("Error in UserService remove_job", e, "remove_job")
            raise

