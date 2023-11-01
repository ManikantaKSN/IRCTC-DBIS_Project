import psycopg2
from datetime import datetime
import time
import re
# Make a regular expression for validating an Email
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
def check(emailid):
    # pass the regular expression and the string into the fullmatch() method
    if(re.fullmatch(regex, emailid)):
        return True
    else:
        return False
def is_valid_date(dob):
    date2 = datetime.strptime(dob, '%Y-%m-%d').date()
    date1 = datetime.today().date()
    difference = (date1 - date2).days
    return difference
def check_mb(mobile_number):
    Pattern = re.compile("[6-9][0-9]{9}")
    if Pattern.match(mobile_number):
        return True
    return False

db_name="irctcdb"
user="postgres"
password="pg23"
host="localhost"
port="5432"
# forming connection
try:
    conn = psycopg2.connect(database=db_name,user=user,password=password,host=host,port=port)
    # print("connected successfully")
except:
    print("Database not connected")
    exit()
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur=conn.cursor()
try:
    cur.execute("BEGIN")
    print("\n CREATING A USER")
    print("-----------------")
    fname = input("Enter first name: ")
    lname = input("Enter last name: ")
    emailid = input("Enter (valid) email address: ")
    password = input("Enter password(minimum length = 4): ")
    mobile_number = input("Enter (10-digit) mobile number: ")
    gender = input("Enter gender (M/F): ")
    dob = input("Enter date of birth (YYYY-MM-DD): ")
    status="verified"

    if check_mb(mobile_number):
        mb = 1
    else:
        mb = 0

    if len(password)>=4:
        pd = 1
    else:
        pd = 0

    if gender=='F' or gender=='M':
        gd = 1
    else:
        gd = 0

    if is_valid_date(dob)>(18*365):
        dd = 1
    else:
        dd = 0

    if check(emailid):
        ed = 1
    else:
        ed = 0

    if(mb == 1 and pd == 1 and gd == 1 and dd == 1 and ed == 1):    
        cur.execute("INSERT INTO user_details(fname, lname, emailid, password, mobile_number, gender, dob,status) VALUES(%s, %s, %s, %s,%s,%s,%s,%s)",(fname, lname, emailid, password, mobile_number, gender, dob,status))
        cur.execute("COMMIT")
        cur.execute("select user_id from user_details where fname = (%s) and lname = (%s) and emailid = (%s) and password = (%s) and mobile_number =(%s) and gender = (%s) and dob = (%s) and status = (%s)",(fname,lname,emailid,password,mobile_number,gender,dob,status))
        ud = cur.fetchone()
        time.sleep(1)
        print("USER ADDED SUCCESSFULLY!")
        print("User ID =",ud[0]) 

    else:
        conn.rollback()
        print("ROLLBACK: Invalid input. Please check your details.")
        if(mb == 0):
            print("Invalid mobile number")
        if(pd == 0):
            print("Invalid password")
        if(gd == 0):
            print("Invalid gender")
        if(dd == 0):
            print("Invalid date of birth")
        if(ed == 0):
            print("Invalid email id")
except Exception as e:
    print(f"ROLLBACK: Error: {e}")
    conn.rollback()  
finally:    
    conn.commit()         
    cur.close()
    conn.close()