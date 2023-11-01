import psycopg2
db_name = "irctcdb"
user = "postgres"
password = "pg23"
host = "localhost"
port = "5432"

try:
    conn = psycopg2.connect(database=db_name, user=user, password=password, host=host, port=port)
    # print("Connected successfully")
except Exception as e:
    print(f"Database not connected: {e}")
    exit()
# Set isolation level to AUTOCOMMIT
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()
# Read the SQL commands from the file
with open("populate-db.sql", "r") as file:
    sql_commands = file.read()
# Execute the SQL commands
cursor.execute(sql_commands)
conn.commit()
cursor.close()
conn.close()
print("Data populated into tables")