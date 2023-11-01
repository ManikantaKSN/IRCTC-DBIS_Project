from prettytable import PrettyTable
from datetime import datetime
import psycopg2
import time

db_name = "irctcdb"
user = "postgres"
password = "pg23"
host = "localhost"
port = "5432"


def is_valid_date(dob):
    date2 = datetime.strptime(dob, '%Y-%m-%d').date()
    date1 = datetime.today().date()
    difference = (date1 - date2).days
    return difference

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
user_id = int(input("Enter user_id : "))
# user_id = 1
temp = 0

# start fetching details for the user
mycursor.execute("BEGIN")
try:
    mycursor.execute("SELECT * FROM user_details WHERE user_id = %s", (user_id,))
    exists = mycursor.fetchone()

    if exists:
        password = input("Enter password : ")
        # password = "1973"
        mycursor.execute(
            "SELECT * FROM user_details WHERE user_id = %s AND password = %s", (user_id, password))
        found = mycursor.fetchone()
        if found:
            print("\nWELCOME TO IRCTC\n")
            temp = 1
        else:
            print("Incorrect password")
            exit()
    else:
        print("User does not exist")
        exit()

    mycursor.execute("SELECT station_name FROM station_details")
    r = mycursor.fetchall()

    routes = PrettyTable(['Route-1', 'Route-2'])
    routes.add_row(['SSS Hubballi', 'SSS Hubballi'])
    routes.add_row(['\u2191\u2193', '\u2191\u2193'])
    routes.add_row(['Ballari', 'Hosapete'])
    routes.add_row(['\u2191\u2193', '\u2191\u2193'])
    routes.add_row(['Guntakal', 'Mahbubnagar'])
    routes.add_row(['\u2191\u2193', '\u2191\u2193'])
    routes.add_row(['Vijayawada', 'Kacheguda'])
    print(routes)

    while temp == 1:
        # Declaring temporary variables
        name = ""
        distance = 0
        time.sleep(1)
        # Taking User inputs
        starting_station_name = input("Enter your Start point : ")
        destination_station_name = input("Enter your destination point : ")
        time.sleep(0.5)

        # fetching details
        print("\n\nTrains available for your journey")
        mycursor.execute("select * from train_schedule as t1, train_schedule as t2 where t1.station_name = (%s) and t2.station_name = (%s) and t1.schedule_id < t2.schedule_id and t1.train_number = t2.train_number",
                         (starting_station_name, destination_station_name))
        rows = mycursor.fetchall()
        for x in rows:
            mycursor.execute(
                "SELECT train_name FROM train_details WHERE train_number = (%s)", (x[1],))
            name = mycursor.fetchall()

        # Entering details in a table
        train_details = PrettyTable(['Train_number', 'Train_name', 'From_station',
                                     'Arrival_time', 'Departure_time', 'To_station', 'Reach_time', 'Distance'])
        trainNo = 0
        for data in rows:
            distance = data[11] - data[5]
            train_details.add_row(
                [data[1], name[0][0], data[2], data[3], data[4], data[8], data[9], data[11]-data[5]])
            trainNo = data[1]
        if (len(train_details._rows)):
            print(train_details)
            print("\n")
            temp = 0
        else:
            print("\nNO TRAIN AVAILABLE IN THIS ROUTE\n\n")
    time.sleep(1)

    while (True):
        date_of_travel = input("Enter date of travel (YYYY-MM-DD) : ")
        if (is_valid_date(date_of_travel) >= 0):
            print("Please enter correct date. Earlier dates cant be entered")
            continue
        else:
            break
    time.sleep(1)

    # fetching available classes
    print("\nClass available to travel : ")
    mycursor.execute("SELECT class_name FROM ticket_class")
    classes = mycursor.fetchall()

    # printing in a table
    class_name = PrettyTable(['Ticket_Class'])
    for y in classes:
        class_name.add_row([y[0]])
    print(class_name)
    print("\n")
    time.sleep(1)

    # validating the input from the user and calculating the ticket price
    while (True):

        # taking user input class
        t_class = input("Enter the class you want to travel : ")
        ticket_price = 0
        # print(distance)
        if (t_class == '1A'):
            ticket_price = 4*distance
            break
        elif (t_class == '2A'):
            ticket_price = 3*distance
            break
        elif (t_class == '3A'):
            ticket_price = 2*distance
            break
        elif (t_class == 'SL'):
            ticket_price = 1*distance
            break
        else:
            print("Wrong class entered")

    # Fetching the route info through mapping
    mycursor.execute("select mapval from mapping where start_point = (%s) and destination_point = (%s)",
                     (starting_station_name, destination_station_name))
    mpval = mycursor.fetchone()
    # print(mpval)

    vall = True
    while (vall):
        # Fetching the available seat details
        mycursor.execute("select * from seats where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s)",
                         (trainNo, date_of_travel, t_class, mpval[0], 'AVAILABLE'))
        seat = mycursor.fetchall()
        # print("\n *****")
        # print(seat)
        print("Rules : You cannot book more than 4 tickets at a time \n")
        print("No. of available tickets :", len(seat))
        cnt = int(input("Enter no. of tickets you want to book : "))

        # available seats should be greater than the number of tickets user asked for - 1st condition
        # max ticket a user can book at a time is 4 - 2nd condition
        if len(seat) >= cnt and cnt <= 4:
            # input for seat bookings
            seat_booking = int(
                input("Seats are available. Press 1 to Book or 0 to Exit : "))
            print("\n")
            if seat_booking == 1:
                # Printing Ticket payment information
                print("Ticket price =", ticket_price, "Rupees")
                tot_price = cnt * ticket_price
                print("Total price to pay =", tot_price, "Rupees\n")
                time.sleep(1)

                # Pushing passenger info into a list
                passd = []
                for i in range(cnt):
                    pname = input(f"Enter passenger {i+1} name : ")
                    paage = int(input(f"Enter passenger {i+1} age : "))
                    pgen = input(f"Enter passenger {i+1} gender(M/F) : ")
                    passd.append((pname, paage, pgen))
                # print(passd)
                print("\n")
                time.sleep(0.5)

                # Input for payments
                payment_input = int(
                    input("Press 1 to Pay and Continue or 0 to Exit : "))
                if (payment_input == 0):
                    exit()
                elif (payment_input == 1):
                    mycursor.execute("select * from seats where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s)",
                         (trainNo, date_of_travel, t_class, mpval[0], 'AVAILABLE'))
                    seatct = mycursor.fetchall()
                    if(len(seatct)<cnt):
                        conn.rollback()
                        conn.commit()
                        print(f"ROLLBACK: Error: Tickets Already Booked")
                        exit()
                    time.sleep(1)
                    print("Booking Tickets .......")
                    time.sleep(2)
                    print("Tickets booked.\n\n")
                    time.sleep(1)

                    # lists to maintain passenger's seat and berth numbers
                    seatno = []
                    berthno = []
                    for x in range(len(seatct)):
                        if x >= cnt:
                            break
                        seatno.append(seatct[x][3])
                        berthno.append(seatct[x][4])
                        statement = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                        varb = ('BOOKED', trainNo, date_of_travel,
                                t_class, mpval[0], 'AVAILABLE', seatno[x])
                        mycursor.execute(statement, varb)
                        # code for removing ab and abc for a booked

                    if mpval[0] == 'A':
                        mpl = ['A', 'AB', 'ABC']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'B':
                        mpl = ['B', 'AB', 'BC', 'ABC']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'C':
                        mpl = ['C', 'BC', 'ABC']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'AB':
                        mpl = ['A', 'B', 'AB', 'BC', 'ABC']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'BC':
                        mpl = ['AB', 'B', 'C', 'BC', 'ABC']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'ABC':
                        mpl = ['A', 'B', 'C', 'AB', 'BC', 'ABC']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'A1':
                        mpl = ['A1', 'AB1', 'ABC1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'B1':
                        mpl = ['B1', 'AB1', 'BC1', 'ABC1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'C1':
                        mpl = ['C1', 'BC1', 'ABC1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'AB1':
                        mpl = ['A1', 'B1', 'AB1', 'BC1', 'ABC1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'BC1':
                        mpl = ['AB1', 'B1', 'C1', 'BC1', 'ABC1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'ABC1':
                        mpl = ['A1', 'B1', 'C1', 'AB1', 'BC1', 'ABC1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'D':
                        mpl = ['D', 'DE', 'DEF']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'E':
                        mpl = ['E', 'DE', 'EF', 'DEF']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'F':
                        mpl = ['F', 'EF', 'DEF']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'DE':
                        mpl = ['D', 'E', 'DE', 'EF', 'DEF']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'EF':
                        mpl = ['DE', 'E', 'F', 'EF', 'DEF']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'DEF':
                        mpl = ['D', 'E', 'F', 'DE', 'EF', 'DEF']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'D1':
                        mpl = ['D1', 'DE1', 'DEF1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'E1':
                        mpl = ['E1', 'DE1', 'EF1', 'DEF1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'F1':
                        mpl = ['F1', 'EF1', 'DEF1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'DE1':
                        mpl = ['D1', 'E1', 'DE1', 'EF1', 'DEF1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'EF1':
                        mpl = ['DE1', 'E1', 'F1', 'EF1', 'DEF1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)

                    if mpval[0] == 'DEF1':
                        mpl = ['D1', 'E1', 'F1', 'DE1', 'EF1', 'DEF1']
                        for y in mpl:
                            for xy in seatno:
                                stmt = "update seats set status = (%s) where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s) and seat_no = (%s)"
                                vrq = ('BOOKED', trainNo, date_of_travel,
                                       t_class, y, 'AVAILABLE', xy)
                                mycursor.execute(stmt, vrq)
                    sttement = "insert into reservation(user_id, train_number, start_point, destination_point, journey_date, ticket_fare1, class_name, number_of_seats, ticket_status, quota) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    vdar = (user_id, trainNo, starting_station_name, destination_station_name,
                            date_of_travel, tot_price, t_class, cnt, 'BOOKED', 'GENERAL')
                    mycursor.execute(sttement, vdar)

                    mycursor.execute("select pnr_number from reservation where user_id =(%s) and train_number=(%s) and start_point=(%s) and destination_point = (%s) and journey_date = (%s) and ticket_fare1 = (%s) and class_name = (%s) and number_of_seats = (%s) and ticket_status = (%s) and quota = (%s)", vdar)
                    pnrval = mycursor.fetchone()

                    stment = "select * from seats where train_number = (%s) and journey_date = (%s) and class_name = (%s) and mapval = (%s) and status =(%s)"
                    vrb = (trainNo, date_of_travel, t_class, mpval[0], 'BOOKED')
                    mycursor.execute(stment, vrb)

                    for i in range(cnt):
                        stement = "insert into passenger_details values (%s,%s,%s,%s,%s,%s)"
                        vrbe = (pnrval[0], passd[i][0], passd[i][1],
                                passd[i][2], seatno[i], berthno[i])
                        mycursor.execute(stement, vrbe)
                    mycursor.execute("COMMIT")

                    mycursor.execute(
                        "select * from reservation where user_id = (%s) order by pnr_number desc", (user_id,))
                    print("Your latest transaction : ")
                    resval = mycursor.fetchone()

                    reservation_details = PrettyTable(['PNR', 'User_id', 'Train_number', 'From', 'To',
                                                       'Journey_date', 'Ticket_fare', 'Class_name', 'No.of tickets', 'Ticket_status', 'Quota'])
                    reservation_details.add_row(
                        [resval[0], resval[1], resval[2], resval[3], resval[4], resval[5], resval[6], resval[7], resval[8], resval[9], resval[10]])
                    print(reservation_details)
                    print()
                    time.sleep(0.75)

                    pval = int(pnrval[0])
                    mycursor.execute(
                        "select * from passenger_details where pnr_number = (%s)", (pval,))
                    pass_det = mycursor.fetchall()

                    print("Passenger Details : ")
                    passenger_details = PrettyTable(['PNR', 'Name', 'Age', 'Gender', 'Seat_Number', 'Berth'])
                    for t1 in pass_det:
                        passenger_details.add_row([t1[0], t1[1], t1[2], t1[3], t1[4], t1[5]])
                    print(passenger_details)
                    print()
                    time.sleep(0.75)

                    mycursor.execute(
                        "select * from reservation where user_id = (%s) order by pnr_number desc", (user_id,))
                    resval1 = mycursor.fetchall()

                    print("All of your transactions : ")
                    all_transactions = PrettyTable(['PNR', 'User_id', 'Train_number', 'From', 'To',
                                                       'Journey_date', 'Ticket_fare', 'Class_name', 'No.of tickets', 'Ticket_status', 'Quota'])
                    for t2 in resval1:
                        all_transactions.add_row([t2[0], t2[1], t2[2], t2[3], t2[4], t2[5], t2[6], t2[7], t2[8], t2[9], t2[10]])   
                    print(all_transactions)
                    print()
                    time.sleep(0.75)

            elif seat_booking == 0:
                exit()
            else:
                pass
            vall = False
        else:
            if cnt > 4:
                print("You can book a maximum of 4 tickets at a time")
                ip1 = int(input("Enter 1 to continue or 0 to exit : "))
                if ip1 == 0:
                    vall = False
            else:
                print("Requested no. of Seats not available")
                ip1 = int(input("Enter 1 to continue or 0 to exit : "))
                if ip1 == 0:
                    vall = False
except Exception as e:
    conn.rollback()
    print(f"ROLLBACK: Error: {e}")
finally:
    conn.commit()
    mycursor.close()
    conn.close()