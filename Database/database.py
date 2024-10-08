# region imports
import psycopg2
import psycopg2.pool
from ServerLogging.serverLogger import Logger
import traceback
from psycopg2.errors import DuplicateTable, UniqueViolation, OperationalError
import time
# endregion

# region logging
def log(message, func):
    Logger.logDatabase(message, func)

def logError(*args):
    try:
        message = args[0]
        if len(args) == 2:
            e = ValueError(args[0])
            func = args[1]
        else:    
            e = args[1]
            func = args[2]
        message = f"{message}\n{traceback.format_exception(None, e, e.__traceback__)}"
        Logger.logDatabase(message, func, "ERROR")
    except Exception as e:
        Logger.logDatabase(f"Error in logError: {e}", "main.logError", "ERROR")
        Logger.logDatabase(f"Original error: {message}", "main.logError", "ERROR")
# endregion

# Define the old and new schemas as global variables
old_schemas = {
    "users": """
        CREATE TABLE users (
            uid VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100),
            dob VARCHAR(8),
            is_owner BOOLEAN DEFAULT FALSE,
            is_admin BOOLEAN DEFAULT FALSE,
            phone_number CHAR(13),
            jobs_saved INT[] DEFAULT '{}',
            email VARCHAR(100) NOT NULL UNIQUE
        );
    """,
    "resumes": """
        CREATE TABLE resumes (
            uid VARCHAR(50) PRIMARY KEY,
            skills TEXT[],
            experience JSONB,
            education JSONB,
            FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
        );
    """,
    "jobdescriptions": """
        CREATE TABLE jobdescriptions (
            job_id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            company VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            required_skills TEXT[],
            application_deadline VARCHAR(8),
            location VARCHAR(100),
            salary DECIMAL(10, 2),
            job_type VARCHAR(4) CHECK (job_type IN ('FULL', 'PART', 'CONT', 'UNKN')),
            active BOOLEAN DEFAULT TRUE
        );
    """,
    "matches": """
        CREATE TABLE matches (
            match_id SERIAL PRIMARY KEY,
            uid VARCHAR(50) NOT NULL,
            job_id INT NOT NULL,
            status VARCHAR(100)  DEFAULT 'Application received' NOT NULL,
            status_code INT DEFAULT 100 NOT NULL,
            grade DECIMAL(5, 2) DEFAULT 0 NOT NULL,
            selected_skills TEXT[],
            FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobdescriptions(job_id) ON DELETE CASCADE
        );
    """,
    "feedback": """
        CREATE TABLE feedback (
            feedback_id SERIAL PRIMARY KEY,
            match_id INT NOT NULL,
            feedback_text TEXT NOT NULL,
            auth_uid VARCHAR(50) NOT NULL,
            FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
            FOREIGN KEY (auth_uid) REFERENCES users(uid) ON DELETE CASCADE
        );
    """
}

new_schemas = {
    "users": old_schemas["users"],
    "resumes": old_schemas["resumes"],
    "jobdescriptions": old_schemas["jobdescriptions"],
    "matches": old_schemas["matches"],
    "feedback": old_schemas["feedback"]
}

# region Database
class Database:
    connection_pool = None

    @staticmethod
    def initialize():
        try:
            # Attempt to connect using the internal URL
            log("Connecting to internal URL", "Database.initialize")
            Database.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 95,
                database="resume_grader",
                user="bugslayerz",
                password="dZLAsglBKDPxeXaRwgncaoHr9nTKGZXi",
                host="dpg-coi9t65jm4es739kjul0-a"
            )
            if Database.connection_pool:
                log("Connection to internal URL successful", "Database.initialize")
        except OperationalError as internal_error:
            log("Could not connect to internal database trying external", "Database.initialize")
            
            try:
                # Fallback to the external URL if internal fails
                Database.connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 95,
                    database="resume_grader",
                    user="bugslayerz",
                    password="dZLAsglBKDPxeXaRwgncaoHr9nTKGZXi",
                    host="dpg-coi9t65jm4es739kjul0-a.oregon-postgres.render.com"
                )
                if Database.connection_pool:
                    log("Connection to external URL successful", "Database.initialize")
            except (Exception, psycopg2.DatabaseError) as external_error:
                logError(external_error, "Database.initialize")
        except Exception as e:
            logError(e, "Database.initialize")
            raise

    @staticmethod
    def _get_connection():
        con = Database.connection_pool.getconn()
        log(f"Connection acquired{con}", "Database._get_connection")
        return con

    @staticmethod
    def _return_connection(connection):
        Database.connection_pool.putconn(connection)
        log(f"Connection returned{connection}", "Database._return_connection")


    @staticmethod
    def execute_query(query, params=None, fetch=False):
        con = None
        start_time = time.time()
        try:
            con = Database._get_connection()
            with con.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    con.commit()
                    return result
                con.commit()
        except psycopg2.Error as e:
            logError(e, "execute_query")
            if con:
                con.rollback()
            raise
        finally:
            if con:
                Database._return_connection(con)
            log(f"Query {query} executed in {time.time() - start_time} seconds", "Database.execute_query")

    @staticmethod
    def create_tables(table_name=None):
        try:
            log("Creating tables", "Database.create_tables")
            if table_name:
                Database.execute_query(new_schemas[table_name])
                log(f"Table {table_name} created successfully", "Database.create_tables")
                return
            for table_name, table_schema in old_schemas.items().__reversed__():
                Database.execute_query(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            for table_name, table_schema in new_schemas.items():
                Database.execute_query(table_schema)
            indexes = {
                "users": "CREATE INDEX idx_users_email ON users(email)",
                "users": "CREATE INDEX idx_users_uid ON users(uid)",
                "resumes": "CREATE INDEX idx_resumes_uid ON resumes(uid)",
                "jobdescriptions": "CREATE INDEX idx_jobdescriptions_title ON jobdescriptions(title)",
                "jobdescriptions": "CREATE INDEX idx_jobdescriptions_company ON jobdescriptions(company)",
                "jobdescriptions": "CREATE INDEX idx_jobdescriptions_description ON jobdescriptions(description)",
                "matches": "CREATE INDEX idx_matches_uid ON matches(uid)",
                "matches": "CREATE INDEX idx_matches_job_id ON matches(job_id)",
                "matches": "CREATE INDEX idx_matches_grade ON matches(grade)",
                "matches": "CREATE INDEX idx_matches_job_id_grade ON matches(job_id, grade)",
                "feedback": "CREATE INDEX idx_feedback_match_id ON feedback(match_id)"
            }
            log("Creating INDEXES", "Database.create_tables")
            try:
                for table_name, index_schema in indexes.items():
                    Database.execute_query(index_schema)
            except DuplicateTable:
                pass
            log("Tables and INDEXES created successfully", "Database.create_tables")
        except psycopg2.Error as e:
            logError(e, "Database.create_tables")
            raise

    @staticmethod
    def migrate_data():
        try:
            log("Starting data migration", "Database.migrate_data")
            
            tables_to_create = new_schemas.keys()
            # Rename old tables
            for table_name in tables_to_create:
                Database.execute_query(f"ALTER TABLE {table_name} RENAME TO old_{table_name}")
            
            log("Tables renamed", "Database.migrate_data")

            # Create new tables
            for table_name in tables_to_create:
                Database.create_tables(table_name)
            log("Migrating data", "Database.migrate_data")
            # migrate user data
            user_data = Database.execute_query("SELECT * FROM old_users;", fetch=True)
            for user in user_data:
                Database.execute_query("INSERT INTO users (uid, name, dob, is_owner, is_admin, phone_number, email) VALUES (%s, %s, %s, %s, %s, %s, %s);", user)
                
            log("Data migration completed", "Database.migrate_data")
        except psycopg2.Error as e:
            logError(e, "Database.migrate_data")
            raise
    
    @staticmethod
    def list_tables():
        try:
            log("Listing all tables", "Database.list_tables")
            result = Database.execute_query("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public';
            """, fetch=True)
            return result
        except psycopg2.Error as e:
            logError(e, "Database.list_tables")
            raise

    @staticmethod
    def view_table_data(table_name, limit=10):
        try:
            log(f"Viewing data from table {table_name}", "Database.view_table_data")
            result = Database.execute_query(f"SELECT * FROM {table_name} LIMIT %s;", (limit,), fetch=True)
            return result
        except psycopg2.Error as e:
            logError(e, "Database.view_table_data")
            raise
    
    @staticmethod
    def has(table, columns, values):
        try:
            log(f"Checking if {columns} with value {values} exists in table {table}", "Database.has")
            query = f"SELECT * FROM {table} WHERE "
            query += " AND ".join([f"{column} = %s" for column in columns])
            result = Database.execute_query(query, values, fetch=True)
            return len(result) > 0
        except psycopg2.Error as e:
            logError(e, "Database.has")
            raise

# endregion
