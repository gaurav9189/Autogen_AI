import os
import snowflake.connector
from dotenv import load_dotenv

def connect_to_snowflake():
    print("Connecting to Snowflake using environment variables...")
    load_dotenv()
    try:
        conn = snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            role=os.getenv('SNOWFLAKE_ROLE'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
        )
        print("Connection established.")
        return conn
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        raise

def list_databases(cursor):
    query = "SHOW DATABASES"
    print(f"Executing query: {query}")
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print("\nDatabases found:")
        for row in results:
            print(f"- {row[1]}")
        print(f"\nTotal databases: {len(results)}")
        return [row[1] for row in results]
    except Exception as e:
        print(f"Error executing query: {e}")
        return []

def list_tables_in_database(cursor, database_name):
    query = f"SHOW TABLES IN DATABASE {database_name}"
    print(f"\nExecuting query: {query}")
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            print(f"\nTables in {database_name}:")
            for row in results:
                print(f"- {row[1]}")
            print(f"\nTotal tables: {len(results)}")
        else:
            print(f"No tables found in {database_name}")
    except Exception as e:
        print(f"Error executing query in database {database_name}: {e}")

def main():
    try:
        conn = connect_to_snowflake()
        cursor = conn.cursor()

        print("\nRetrieving all databases...")
        databases = list_databases(cursor)

        for database in databases:
            list_tables_in_database(cursor, database)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
            print("\nCursor closed.")
        if 'conn' in locals() and conn:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    main()
