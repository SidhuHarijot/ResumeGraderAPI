from Database.UserDatabase import UserDatabase
from Database.database import Database


Database.initialize()
print(UserDatabase.find_user({"email": "bug@slayerz.com"}))
