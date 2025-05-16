import csv


def new_booking():
    append_data = []
    hotel_file = open('hotel-db.csv', 'a+')
    writer = csv.writer(hotel_file)
    reader = csv.reader(hotel_file)

    countrydict = {1: 'Qatar', 2: 'UAE', 3: 'Saudi'}
    currdict = {1: 'QAR', 2: 'UAE', 3: 'SAR'}
    roomdict = {1: 'Single Room', 2: 'Double Room',
                3: 'Triple Room', 4: 'Deluxe Room'}

    print("These are the following countries where you can book a hotel room:\n\n    1. Qatar\n    2. United Arab Emirates\n    3. Saudi Arabia\n\n")
    country = int(
        input(">> Enter the INDEX NUMBER of the country which you want to choose: "))
    currency = currdict[country]

    pricelow = int(input(">> Enter the LOWER END of your price range: "))
    pricehigh = int(input(">> Enter the HIGHER END of your price range: "))
    if pricelow > pricehigh:
        pricelow, pricehigh = pricehigh, pricelow

    print("These are the available ratings:\n\n    1. 4 Stars\n    2. 5 Stars\n\n")
    stars = int(input(">> Enter the MINIMUM RATING of your hotel: "))
    if stars == 1:
        stars = 4
    else:
        stars = 5

    print("These are the following countries where you can book a hotel room:\n\n    1. Single Room\n    2. Double Room\n    3. Triple Room\n    4. Deluxe Room\n\n")
    room = int(input(">> Enter the TYPE OF ROOM you want: "))

    try:
        country = countrydict[country]
        room = roomdict[room]
        print(
            f"[CONFIRMATION] Filters:\n\n[COUNTRY]: {country}\n[PRICE RANGE]: {pricelow} - ${pricehigh}\n[TYPE OF ROOM]: {room}\n[ROOM RATING]: Above {stars} stars")
        confirmation = input(
            "Are you sure that this is the correct filter? Type 'YES' in all caps to confirm: ")
        if confirmation == 'YES':
            possiblechoices = []
            with open('rooms.csv', 'r') as fh:
                r_obj = csv.reader(fh)
                n = 1
                for row in r_obj:
                    if str(row[1]) == country:
                        price = int(row[2])
                        if price > pricelow and price < pricehigh:
                            if str(row[3]) == room:
                                if int(row[5]) >= stars:
                                    print(
                                        f"[ROOM {n}]\nn[NAME]: {row[0]}\n[COUNTRY]: {row[1]}\n[PRICE]: {row[2]}\n[ROOM TYPE]: {row[3]}\n[ROOM NUMBER]: {row[4]}\n[ROOM RATING]: {row[5]} Stars\n[AVAILABILITY]: Available")
                                    n += 1
                                    possiblechoices.append(row[4])
                print("\n--- [END OF RECORDS] ---")
            for i in range(1):
                guest_name = input(">> GUEST NAME: ")
                guest_mb = int(input(">> GUEST PHONE NUMBER: "))
                guest_roomno = 0

                booking = False
                while booking == False:
                    guest_roomno = int(input(">> GUEST ROOM NUMBER: "))
                    if guest_roomno > 15 or guest_roomno < 1:
                        print(
                            "You have entered a non-existent room number. Please try again.")
                    else:
                        booking = True

                begdate = ""
                enddate = ""
                begyr = ""
                begday = input("Enter the day you want to book in: ")
                begmon = input("Enter the month you want to book in: ")
                while int(begyr) < 2023:
                    begyr = input("Enter the day you want to book in: ")
                    if int(begyr) < 2023:
                        print("Bookings in the past cannot be made.")

                endyr = ""
                endday = input("Enter the day you want to check out: ")
                endmon = input("Enter the month you want to check out: ")
                while int(endyr) < 2023:
                    endyr = input("Enter the day you want to check out: ")
                    if int(endyr) < 2023:
                        print("Bookings in the past cannot be made.")

                begdate = begday + "/" + begmon + "/" + begyr
                enddate = endday + "/" + endmon + "/" + endyr

                print(
                    f"\nThese are the details under which the room will be booked:\n\n[ROOM NUMBER]: {guest_roomno}\n[GUEST NAME]: {guest_name}\n[GUEST PHONE NUMBER]: {guest_mb}\n[BOOK-IN DATE]: {begdate}\n[CHECK-OUT DATE]: {enddate}\n")

                confirmation = input(">> CONFIRMATION: ")
                if confirmation == 'YES':
                    append_data = [guest_name, guest_mb,
                                   guest_roomno, begdate, enddate]
                    writer.writerow(append_data)
                    print("[INFO] The hotel booking has been made.")
                else:
                    print("[INFO] The hotel booking has been cancelled.")
            hotel_file.close()
        else:
            print("The booking has been aborted")
    except KeyError:
        print("[ABORT] You have entered either the country or the room incorrectly.")


def view_bookings():
    try:
        try:
            with open('hotel-db.csv', 'r') as fh:
                r_obj = csv.reader(fh)
                n = 1
                for rec in r_obj:
                    print(f"--- [RECORD {n}] ---\n\n[GUEST NAME]: ", rec[0],
                          "\n[GUEST PHONE NUMBER]: ", rec[1], "\n[GUEST ROOM NUMBER]: ", rec[2], "\n")
                    n += 1
                if n != 1:
                    print("--- [END OF RECORDS] ---")
                else:
                    print("[INFO] No bookings exist.")
        except IndexError:
            print("[INFO] No bookings exist.")
    except FileNotFoundError:
        print("[INFO] No bookings exist.")


def delete_booking():
    try:
        view_bookings()
        bookingExists = False
        with open('hotel-db.csv', 'r') as fh:
            r_obj = csv.reader(fh)
            lines = []
            room_no = input(">> ROOM NUMBER TO DELETE: ")
            for rec in r_obj:
                lines.append(rec)
                for field in rec:
                    if str(field) == room_no:
                        lines.remove(rec)
                        bookingExists = True
        with open('hotel-db.csv', 'w') as fh:
            w_obj = csv.writer(fh)
            w_obj.writerows(lines)
            if bookingExists:
                print(f"Record with room number {room_no} deleted.")
            else:
                print(f"Record with room number {room_no} does not exist.")
    except FileNotFoundError:
        print("[INFO] Unable to delete non-existent bookings")


# ----Main Program----- #
print("HOTEL BOOKING PORTAL\n\nGreetings! Welcome to our hotel booking portal. Below is a list of all the commands available.\n\n    1. New Booking\n    2. View Bookings\n    3. Delete Booking\n    4. About\n    5. Help\n    6. Quit\n")

while True:
    choice = input(">> COMMAND: ")
    if choice == "1" or choice[0].lower() == 'n':
        new_booking()
    elif choice == "2" or choice[0].lower() == 'v':
        view_bookings()
    elif choice == "3" or choice[0].lower() == 'd':
        delete_booking()
    elif choice == "4" or choice[0].lower() == 'a':
        print("\nWelcome to our hotel booking portal, your ultimate destination for finding the perfect accommodation for your travels. We are honored to be part of your journey, and we look forward to helping you find the perfect accommodation for your next adventure. Start exploring our wide range of hotels today and embark on a remarkable travel experience with us.\n")
    elif choice == "5" or choice[0].lower() == 'h':
        print("\nBelow is a list of all commands available and their explanation:\n\n    1. New Booking - book a room in a hotel\n    2. View Bookings - view current bookings\n    3. Delete Booking - select and delete a booking based on the room number\n    4. About - learn more about this project\n    5. Help - view this list\n    6. Quit - quits the program\n")
    elif choice == "6" or choice[0].lower() == 'q':
        break
    else:
        print("\nYou have entered an invalid command. Please view the 'help' page for all available commands by sending the command '4' without quotes.\n")

print("\nYou have chosen to quit the program. Thank you for using our portal!")
