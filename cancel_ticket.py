from prettytable import PrettyTable
from datetime import datetime
import time
import psycopg2
db_name = "irctcdb"
user = "postgres"
password = "pg23"
host = "localhost"
port = "5432"

try:
    conn = psycopg2.connect(database=db_name, user=user,
                            password=password, host=host, port=port)
    print("Connected successfully\n")
except Exception as e:
    print(f"Database not connected: {e}")
    exit()

# Set isolation level to AUTOCOMMIT
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
mycursor = conn.cursor()
user_id = int(input("Enter user_id: "))
# user_id = 1
temp = 0

try:
# start fetching details for the user
    mycursor.execute("BEGIN")
    mycursor.execute("SELECT * FROM user_details WHERE user_id = %s", (user_id,))
    exists = mycursor.fetchone()

    if exists:
        password = input("Enter password: ")
        # password = "1973"
        mycursor.execute(
            "SELECT * FROM user_details WHERE user_id = %s AND password = %s", (user_id, password))
        found = mycursor.fetchone()
        if found:
            print()
            print("WELCOME")
            time.sleep(1)
            temp = 1
        else:
            print("Incorrect password")
            exit()
    else:
        print("User does not exist")
        exit()

    mycursor.execute(
        "select * from reservation where user_id = (%s) order by pnr_number desc", (user_id,))
    resval1 = mycursor.fetchall()
    print("Here are your previous transactions:")
    all_transactions = PrettyTable(['PNR', 'User_id', 'Train_number', 'From', 'To',
                                       'Journey_date', 'Ticket_fare', 'Class_name', 'No.of tickets', 'Ticket_status', 'Quota'])
    for t2 in resval1:
        all_transactions.add_row([t2[0], t2[1], t2[2], t2[3], t2[4], t2[5], t2[6], t2[7], t2[8], t2[9], t2[10]])   
    print(all_transactions)
    print()
    time.sleep(0.75)
    pnr=int(input("Enter the PNR number of the ticket you want to cancel: "))
    mycursor.execute("select * from passenger_details where pnr_number = (%s)", (pnr,))
    pass_det = mycursor.fetchall()
    print("Passenger Details : ")
    passenger_details = PrettyTable(['PNR', 'Name', 'Age', 'Gender', 'Seat_Number', 'Berth'])
    for t1 in pass_det:
        passenger_details.add_row([t1[0], t1[1], t1[2], t1[3], t1[4], t1[5]])
    print(passenger_details)
    print()
    mycursor.execute("SELECT * FROM reservation WHERE pnr_number = %s", (pnr,))
    rows=mycursor.fetchall()
    print(rows)
    mycursor.execute("SELECT pnr_number,seat_number FROM passenger_details WHERE pnr_number = %s", (pnr,))
    rowss=mycursor.fetchall()
    print(rowss)
    if (len(rows)):
        st="insert into cancel_ticket(pnr_number,ticket_fare) values(%s,%s)"
        v=(pnr,0.8*rows[0][6])
        mycursor.execute(st,v)
        tno = rows[0][2]
        stp = rows[0][3]
        dtp = rows[0][4]
        jnyd = rows[0][5]
        clsn = rows[0][7]
        print("-------------------")
        print(tno,stp,dtp,jnyd,clsn)
        mycursor.execute("select mapval from mapping where start_point = (%s) and destination_point = (%s)",
                         (stp, dtp))
        mpv = mycursor.fetchone()[0]
        seatno = []
        for x in range(len(rowss)):
                seatno.append(rowss[x][1])
                statement = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                varb = ('AVAILABLE', tno, jnyd, clsn, mpv, 'BOOKED', seatno[x])
                mycursor.execute(statement, varb)
                # code for removing ab and abc for a booked and so on
        if mpv == 'A':
            mpl = ['A', 'AB', 'ABC']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'B':
            mpl = ['B', 'AB', 'BC', 'ABC']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'C':
            mpl = ['C', 'BC', 'ABC']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'AB':
            mpl = ['A', 'B', 'AB', 'BC', 'ABC']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'BC':
            mpl = ['AB', 'B', 'C', 'BC', 'ABC']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'ABC':
            mpl = ['A', 'B', 'C', 'AB', 'BC', 'ABC']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'A1':
            mpl = ['A1', 'AB1', 'ABC1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'B1':
            mpl = ['B1', 'AB1', 'BC1', 'ABC1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'C1':
            mpl = ['C1', 'BC1', 'ABC1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'AB1':
            mpl = ['A1', 'B1', 'AB1', 'BC1', 'ABC1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'BC1':
            mpl = ['AB1', 'B1', 'C1', 'BC1', 'ABC1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'ABC1':
            mpl = ['A1', 'B1', 'C1', 'AB1', 'BC1', 'ABC1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'D':
            mpl = ['D', 'DE', 'DEF']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'E':
            mpl = ['E', 'DE', 'EF', 'DEF']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'F':
            mpl = ['F', 'EF', 'DEF']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'DE':
            mpl = ['D', 'E', 'DE', 'EF', 'DEF']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'EF':
            mpl = ['DE', 'E', 'F', 'EF', 'DEF']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'DEF':
            mpl = ['D', 'E', 'F', 'DE', 'EF', 'DEF']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'D1':
            mpl = ['D1', 'DE1', 'DEF1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'E1':
            mpl = ['E1', 'DE1', 'EF1', 'DEF1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'F1':
            mpl = ['F1', 'EF1', 'DEF1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'DE1':
            mpl = ['D1', 'E1', 'DE1', 'EF1', 'DEF1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'EF1':
            mpl = ['DE1', 'E1', 'F1', 'EF1', 'DEF1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        if mpv == 'DEF1':
            mpl = ['D1', 'E1', 'F1', 'DE1', 'EF1', 'DEF1']
            for y in mpl:
                for xy in seatno:
                    stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                    vrq = ('AVAILABLE', tno, jnyd,
                           clsn, y, 'BOOKED', xy)
                    mycursor.execute(stmt, vrq)
        st1=("DELETE FROM passenger_details WHERE pnr_number =(%s)")   
        mycursor.execute(st1,(pnr,))
        st2=("DELETE FROM passenger_details WHERE pnr_number =(%s)")
        mycursor.execute(st2,(pnr,))
        mycursor.execute("commit")
    else:
        print("You haven't booked any tickets on this pnr_number:",pnr)
except Exception as e:
    conn.rollback()
    print(f"ROLLBACK: Error: {e}")
finally:
    conn.commit()
    mycursor.close()
    conn.close()