from Database.UserDatabase import UserDatabase
from Database.database import Database


Database.initialize()
while True:
    query = input("[SQL]:")
    fetch = input("Fetch results? (y/n):")
    fetch = True if fetch == "y" else False
    if query == "exit":
        break
    try:
        result = Database.execute_query(query, fetch=fetch)
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")