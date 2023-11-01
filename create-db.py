import psycopg2
import sys
db_name = "postgres"
user = "postgres"
password = "pg23"
host = "localhost"
port = "5432"

try:
    conn = psycopg2.connect(database=db_name, user=user, password=password, host=host, port=port)
    print("Connected successfully")
    print()
except Exception as e:
    print(f"Database not connected: {e}")
    exit()
arg1 = 0
if len(sys.argv) > 1:
    arg1 = sys.argv[1]
# Set isolation level to AUTOCOMMIT
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

cursor = conn.cursor()
if(arg1 != "drop"):
    cursor.execute("CREATE DATABASE irctcdb")
    print("Database 'irctcdb' created")
if(arg1 == "drop"):
    cursor.execute("DROP DATABASE irctcdb")
conn.commit()
cursor.close()
conn.close()
