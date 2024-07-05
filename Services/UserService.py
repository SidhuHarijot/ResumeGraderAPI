from Models.DataModels.User import User
from Models.DataModels.Name import Name
from Models.DataModels.Date import Date
from Models.RequestModels.GetModels import RequestModels as rm
from Processing.Factories.UserFactory import UserFactory
from Database.UserDatabase import UserDatabase
from typing import Dict
import json


class UserService:
    user = None
    in_db = False

    def __init__(self, user: User=None, new_user: rm.User.Create = None,dict: Dict= None, json_str: str=None, db_row: str=None):
        if dict:
            user = UserFactory.from_json(self, dict)
        elif json_str:
            user = UserFactory.from_json(self, json.loads(json_str))
        elif db_row:
            user = UserFactory.from_db_row(self, db_row)
        elif new_user:
            user = new_user.to_user()
        if user:
            self.user = user
            self.in_database()
        else:
            raise ValueError("No valid arguments provided to UserService constructor")
    
    def save_to_db(self):
        if self.validate():
            if not self.in_db:
                UserDatabase.create_user(self.user)
            else:
                self.update()
    
    @staticmethod
    def get_from_db(uid: str):
        return UserService(UserDatabase.get_user(uid))
    
    
    @staticmethod
    def find(params: dict):
        return UserDatabase.find_users(params)
    
    def update(self, request: rm.User.Update = None):
        if request:
            self.user = request.to_user(self.user)
        if self.validate():
            UserDatabase.update_user(self.user)
    
    def to_json(self):
        return UserFactory.to_json(self.user)

    def in_database(self):
        try:
            UserDatabase.get_user(self.user.uid)
        except ValueError:
            self.in_db = False
        self.in_db = True
        return self.in_db

    def delete(self):
        UserDatabase.delete_user(self.user.uid)
        self.in_db = False
    
    @staticmethod
    def get_all():
        return UserDatabase.get_all_users()
    
    @staticmethod
    def print_all():
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
                </tr>
            """

        html_data += """
            </table>
        </body>
        </html>
        """

        return html_data
    
    @staticmethod
    def from_json(json_str: str):
        return UserService(json_str=json_str)
    
    @staticmethod
    def from_dict(dict: Dict):
        return UserService(dict=dict)
    
    @staticmethod
    def from_db_row(db_row: str):
        return UserService(db_row=db_row)
    
    def validate(self):
        return True
    
    def __str__(self):
        return str(self.user)
        