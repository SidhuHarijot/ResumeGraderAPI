from typing import List
import json
from Models.DataModels.GetModels import *
from .factories import log, logError


class UserFactory:
    @staticmethod
    def from_db_row(row) -> User:
        try:
            log(f"Creating User object from row: {row[1]}", "UserFactory.from_db_row")
            return User(
                uid=row[0],
                name=Name.create(row[1]),
                dob=Date.create(row[2]),
                is_owner=row[3],
                is_admin=row[4],
                phone_number=row[5],
                email=row[6]
            )
        except Exception as e:
            logError(f"Error creating User object from row: {row}. \n", e, "UserFactory.from_db_row")
            return User(uid=row[0], name=Name(first_name="Error", last_name="Error"), dob=Date(day=1, month=1, year=1), is_owner=False, is_admin=False, phone_number="00-0000000000", email="error@database.com")
            

    @staticmethod
    def to_db_row(user: User, with_uid=True):
        try:
            log(f"Converting User object to db row: {str(user.name)}", "UserFactory.to_db_row")
            dob_str = str(user.dob)
            if with_uid:
                return (
                    user.uid,
                    str(user.name),
                    dob_str,
                    user.is_owner,
                    user.is_admin,
                    user.phone_number,
                    user.email
                )
            return (
                str(user.name),
                dob_str,
                user.is_owner,
                user.is_admin,
                user.phone_number,
                user.email
            )
        except Exception as e:
            logError(f"Error converting User object to db row: {user}. \n", e, "UserFactory.to_db_row")
            raise

    @staticmethod
    def from_json(data: dict) -> User:
        try:
            log(f"Creating User object from JSON: {data['name']}", "UserFactory.from_json")
            try:
                name = Name.create(data['name'])
            except TypeError:
                data = json.loads(data)
                name = Name.create(data['name'])
            return User(
                uid=data['uid'],
                name=name,
                dob=Date.create(data['dob']),
                is_owner=data.get('is_owner', False),
                is_admin=data.get('is_admin', False),
                phone_number=data['phone_number'],
                email=data['email']
            )
        except Exception as e:
            logError(f"Error creating User object from JSON: {data}. \n", e, "UserFactory.from_json")
            raise

    @staticmethod
    def to_json(user: User) -> dict:
        try:
            log(f"Converting User object to JSON: {str(user.name)}", "UserFactory.to_json")
            return {
                'uid': user.uid,
                'name': str(user.name),
                'dob': str(user.dob),
                'is_owner': user.is_owner,
                'is_admin': user.is_admin,
                'phone_number': user.phone_number,
                'email': user.email
            }
        except Exception as e:
            logError(f"Error converting User object to JSON: {user}. \n", e, "UserFactory.to_json")
            raise

    @staticmethod
    def from_db_rows(rows: List[tuple]) -> List[User]:
        try:
            log(f"Creating list of User objects from multiple rows: ", "UserFactory.from_db_rows")
            result = []
            return [UserFactory.from_db_row(row) for row in rows]
        except Exception as e:
            logError(f"Error creating list of User objects from rows. \n", e, "UserFactory.from_db_rows")
            raise

    @staticmethod
    def to_db_rows(users: List[User]) -> List[tuple]:
        try:
            log(f"Converting list of User objects to db rows: ", "UserFactory.to_db_rows")
            return [UserFactory.to_db_row(user) for user in users]
        except Exception as e:
            logError(f"Error converting list of User objects to db rows. \n", e, "UserFactory.to_db_rows")
            raise

