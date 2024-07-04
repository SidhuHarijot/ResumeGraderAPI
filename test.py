from Database.UserDatabase import UserDatabase
from Database.database import Database
from Services.UserService import UserService


Database.initialize()
print(UserDatabase.get_all_users())
while True:
    query = input("[SQL]:")
    if query == "exit":
        break
    try:
        result = Database.execute_query(query, fetch=True)
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")
