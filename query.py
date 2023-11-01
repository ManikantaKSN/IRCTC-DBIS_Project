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
with open("queries.sql", "r") as file:
    sql_commands = file.readlines()
with open("queries.txt",'r')as file1:
    sql_ques = file1.readlines()
print(sql_ques)
for x in sql_ques:
    print(x[0:-1])
for x in range(len(sql_commands)):
    print("\nQuestion:")
    print("--------")
    print(sql_ques[x][0:-1])
    print("\nQuery:")
    print("-----")
    print(sql_commands[x][0:-1])
    cursor.execute(sql_commands[x][0:-1])
    print("\nResults:")
    print("-------")
    val = cursor.fetchall()
    for y in val:
        print(y)
conn.commit()
cursor.close()
conn.close()