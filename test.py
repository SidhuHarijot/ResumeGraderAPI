import asyncio
import random
import time
from Database.database import Database

# Dummy data to insert
dummy_users = [
    ("user1", "Name1", "19900101", False, False, "12-1234567890", "user1@example.com"),
    ("user2", "Name2", "19900202", False, False, "12-2234567890", "user2@example.com"),
    ("user3", "Name3", "19900303", False, False, "12-3234567890", "user3@example.com"),
    # Add more dummy data as needed
]

async def execute_queries(query, params=None):
    start_time = time.time()
    try:
        Database.execute_query(query, params)
        duration = time.time() - start_time
        return duration, True
    except Exception as e:
        duration = time.time() - start_time
        return duration, False

async def run_query():
    query = "INSERT INTO users (uid, name, dob, is_owner, is_admin, phone_number, email) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    delete_query = "DELETE FROM users WHERE uid = %s;"
    uid = f"user{random.randint(1000, 9999)}"
    params = (uid, f"Name{uid}", "19900101", False, False, f"12-{random.randint(1000000000, 9999999999)}", f"{uid}@example.com")
    duration, success = await execute_queries(query, params)
    await execute_queries(delete_query, (uid,))
    return duration, success

async def stress_test():
    Database.initialize()

    total_queries = 0
    total_time = 0
    successful_queries = 0
    failed_queries = 0
    durations = []

    tasks = [run_query() for _ in range(1000)]  # Number of queries to run
    results = await asyncio.gather(*tasks)

    for duration, success in results:
        durations.append(duration)
        total_queries += 1
        total_time += duration
        if success:
            successful_queries += 1
        else:
            failed_queries += 1

    print(f"Total queries run: {total_queries}")
    print(f"Successful queries: {successful_queries}")
    print(f"Failed queries: {failed_queries}")
    print(f"Total time taken: {total_time} seconds")
    print(f"Average time per query: {total_time / total_queries if total_queries > 0 else 0} seconds")
    print(f"Min time per query: {min(durations) if durations else 0} seconds")
    print(f"Max time per query: {max(durations) if durations else 0} seconds")

if __name__ == "__main__":
    Database.initialize()
    print(Database.has("job", "job_id", 1))
