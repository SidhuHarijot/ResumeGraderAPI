from Database.UserDatabase import UserDatabase
from Database.database import Database
from Services.UserService import UserService



Database.initialize()
Database.migrate_data()
tables = Database.list_tables()
for table in tables:
    print(table[0])
    result = Database.view_table_data(table[0], 0)
    for row in result:
        print(row)
        print("\n")
    print("\n\n")

