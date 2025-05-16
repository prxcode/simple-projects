from sys import exit
from os import system, name
from math import log2
from random import randint
from time import time
from pprint import PrettyPrinter

try:
    from password_strength import PasswordStats
    from mysql.connector import connect, ProgrammingError
    from rsa import decrypt, encrypt, newkeys, pkcs1, PublicKey, PrivateKey
    from pyotp import TOTP
    from hashlib import sha256
    try:
        with open('keys/public_key.pem', 'rb') as pubkey, open('keys/private_key.pem', 'rb') as privkey:
            publickey = PublicKey.load_pkcs1(pubkey.read())
            privatekey = PrivateKey.load_pkcs1(privkey.read())
        print("[1/4] Loading encryption keys")
    except FileNotFoundError:
        print("Generating encryption keys (please be patient, this may take some time)")
        (public_key, private_key) = newkeys(512)
        with open('keys/public_key.pem', 'wb') as pubkey, open('keys/private_key.pem', 'wb') as privkey:
            pubkey.write(public_key.save_pkcs1())
            privkey.write(private_key.save_pkcs1())
        print("Encryption keys generated. Please start the program again.")
        exit()

    print("[2/4] Initializing database")
    try:
        with open("files/sql-variables.txt", "r") as sqlvar:
            lines = sqlvar.readlines()
            host = lines[0][:-1]
            passwd = lines[1][:-1]
        user = "root"
        database = "passdb"
        connection = connect(host=host, user=user,
                             password=passwd, database=database)
        cursor = connection.cursor()
        print("[3/4] Creating tables if they do not exist")
        creatingtable = """
        CREATE TABLE IF NOT EXISTS users (
            userid INT AUTO_INCREMENT PRIMARY KEY,
            service VARCHAR(500),
            username VARCHAR(500),
            email VARCHAR(500),
            password LONGBLOB,
            twofa VARCHAR(500),
            notes VARCHAR(500)
        );
        """
        hashtable = """
        CREATE TABLE IF NOT EXISTS mp (
            masterpass VARCHAR(500)
        );
        """
        cursor.execute(creatingtable)
        cursor.execute(hashtable)
    except (ProgrammingError, FileNotFoundError, IndexError):
        print(
            "Your SQL host and password are incorrectly set. Please enter the correct ones.")
        host = input("Enter the host (localhost is default) >> ")
        if host == '':
            host = 'localhost'
        passwd = input("Enter the root password >> ")
        with open("files/sql-variables.txt", "w") as sqlvar:
            sqlvar.writelines([host + '\n', passwd + '\n'])
        print("\nSQL variables saved. Please restart the program.")
        exit()
    print("[4/4] Opening common passwords and password generation pool")
    with open("files/common-passwords.txt", "r") as common, open("files/generation/adjectives.txt", "r") as adj, open("files/generation/nouns.txt", "r") as nouns:
        common_passwd = common.read()
        adjpool = adj.readlines()
        nounpool = nouns.readlines()

    cursor.execute("SELECT * FROM mp")
    recordlist = list(cursor.fetchall())
    if recordlist == []:
        while True:
            mp, mp2 = input("You have not set up a master password. This compromises the security of the software. Please enter one now below 55 characters >> "), input(
                "Please enter it again >> ")
            if mp != mp2:
                print("You have entered different passwords. Please try again.")
            else:
                break
        hashed = sha256()
        hashed.update(mp.encode('utf-8'))
        hashed_mp = hashed.hexdigest()
        insertingdata = """
        INSERT INTO mp (masterpass)
        VALUES (%s);
        """
        cursor.execute(insertingdata, (hashed_mp, ))
        connection.commit()
        print("[INFO] Master password saved! Please restart the program to use it.")
    else:
        cursor.execute("SELECT * FROM mp;")
        correctmp = cursor.fetchall()[0][0]
        while True:
            mp = input("Enter master password >> ")
            hashed = sha256()
            hashed.update(mp.encode('utf-8'))
            hashed_mp = hashed.hexdigest()
            if hashed_mp == correctmp:
                break
            else:
                print("[INFO] Incorrect password. Try again.")

    def add():
        service = input("Enter service: ")
        username = input("Enter username: ")
        email = input("Enter email: ")
        while True:
            try:
                passinput = input(
                    "Enter password (please limit to 55 characters): ")
                break
            except OverflowError:
                print(
                    "Your password has exceeded 55 characters. Please enter a smaller password.")
        twofa = input("Enter 2FA secret (type NONE in all caps if none): ")
        notes = input(
            "Enter any notes (ex: security questions)(type NONE in all caps if none): ")
        notes = "NONE" if notes[0].lower() == 'n' else notes
        password = encrypt(passinput.encode('utf-8'), publickey)
        insertingdata = """
        INSERT INTO users (service, username, email, password, twofa, notes)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        row = (service, username, email, password, twofa, notes)
        cursor.execute(insertingdata, row)
        connection.commit()
        print("[INFO] Record added to password manager.")

    def view():
        try:
            cursor.execute("SELECT * FROM users")
            recordlist = list(cursor.fetchall())
            if recordlist == []:
                print("[INFO] No records available.")
            else:
                for i in recordlist:
                    print(
                        f"[RECORD {i[0]}] --> (SERVICE) = {i[1]} && (USERNAME) = {i[2]}")
                record_display = input(
                    "Enter the ID of the record to display >> ")
                for i in recordlist:
                    if str(i[0]) == record_display:
                        encryptedpasswd = i[4]
                        passwd = decrypt(
                            encryptedpasswd, privatekey).decode('utf-8')
                        twofa = "NONE" if str(i[5])[0].lower() == "n" else TOTP(
                            str(i[5])).at(int(time()))
                        print(
                            f"[RECORD {i[0]}]:\n\n[SERVICE]: {i[1]}\n[USERNAME]: {i[2]}\n[EMAIL]: {i[3]}\n[PASSWORD]: {passwd}\n[2FA CODE]: {twofa}\n[NOTES]: {i[6]}")
        except pkcs1.DecryptionError:
            print("Failed to decrypt password. It seems like you deleted the public and private keys associated with this entry. There is no way to recover this entry if you did not make a backup of the public and private keys. If you have the keys in a different location, please copy them to the 'keys' directory")

    def generate():
        userpass = input(
            "Would you like to generate a username or password? [u/p] >> ")
        if userpass[0].lower() == "u":
            adjnum = randint(0, 1346)
            nounnum = randint(0, 991)
            randnum = randint(0, 999999)
            username = f"{adjpool[adjnum][0:-1]}{nounpool[nounnum][0:-1]}{randnum}"
            print(f"Your generated username is {username}")
        else:
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            symbols = "`~!@#$%^&*()-_=+\|]}[{':;/?.>,<"
            length = int(
                input(">> Enter the length of the password you want to generate > "))
            print(
                "\nThese are the complexity options available:\n\n     1. Simple (A-Z, a-z) [NOT RECOMMENDED]\n     2. Difficult (A-Z, a-z, 0-9)\n     3. Uncrackable (A-Z, a-z, 0-9, special characters) [RECOMMENDED]\n")
            complexity = int(
                input(">> Enter the complexity of the password you want to generate > "))
            passwd = ""
            count = 1
            if complexity == 1:
                while count <= length:
                    randpool = randint(1, 2)
                    randchar = randint(0, 25)
                    if randpool == 1:
                        passwd += alphabet[randchar].upper()
                    else:
                        passwd += alphabet[randchar].lower()
                    count += 1
            elif complexity == 2:
                while count <= length:
                    randpool = randint(1, 3)
                    randchar = randint(0, 25)
                    if randpool == 1:
                        passwd += alphabet[randchar].upper()
                    elif randpool == 2:
                        passwd += alphabet[randchar].lower()
                    else:
                        passwd += str(randint(0, 9))
                    count += 1
            else:
                while count <= length:
                    randpool = randint(1, 4)
                    randchar = randint(0, 25)
                    randsymb = randint(0, 30)
                    if randpool == 1:
                        passwd += alphabet[randchar].upper()
                    elif randpool == 2:
                        passwd += alphabet[randchar].lower()
                    elif randpool == 3:
                        passwd += str(randint(0, 9))
                    else:
                        passwd += symbols[randsymb]
                    count += 1
            print(f"Your generated password is {passwd}")

    def replace():
        try:
            cursor.execute("SELECT * FROM users")
            recordlist = list(cursor.fetchall())
            if recordlist == []:
                print("[INFO] No records available.")
            else:
                for i in recordlist:
                    print(
                        f"[RECORD {i[0]}] --> (SERVICE) = {i[1]} && (USERNAME) = {i[2]}")
                record_display = input(
                    "Enter the ID of the record to modify >> ")
                for i in recordlist:
                    if str(i[0]) == record_display:
                        encryptedpasswd = i[4]
                        passwd = decrypt(
                            encryptedpasswd, privatekey).decode('utf-8')
                        if str(i[5])[0].lower() == "n":
                            twofa = "NONE"
                        else:
                            secret = str(i[5])
                            totp = TOTP(secret)
                            twofa = totp.at(int(time()))
                        print(
                            f"[RECORD {i[0]}]:\n\n[SERVICE]: {i[1]}\n[USERNAME]: {i[2]}\n[EMAIL]: {i[3]}\n[PASSWORD]: {passwd}\n[2FA CODE]: {twofa}\n[NOTES]: {i[6]}\n")
                    record_row_modify = input(
                        "Enter the name of the detail you would like to modify (everything except record ID) >> ")
                    quitFunction = False
                    if record_row_modify[0].lower() == 's':
                        new_data = input("Enter the new service >> ")
                        replace_keyword = 'service'
                    elif record_row_modify[0].lower() == 'u':
                        new_data = input("Enter the new username >> ")
                        replace_keyword = 'username'
                    elif record_row_modify[0].lower() == 'e':
                        new_data = input("Enter the new email >> ")
                        replace_keyword = 'email'
                    elif record_row_modify[0].lower() == 'p':
                        passinput = input("Enter the new password >> ")
                        new_data = encrypt(
                            passinput.encode('utf-8'), publickey)
                        replace_keyword = 'password'
                    elif record_row_modify[0].lower() == 't':
                        new_data = input("Enter the new 2FA secret >> ")
                        replace_keyword = 'twofa'
                    elif record_row_modify[0].lower() == 'n':
                        new_data = input("Enter new notes >> ")
                        replace_keyword = 'notes'
                    else:
                        new_data = ''
                        replace_keyword = ''
                        quitFunction = True

                    if not quitFunction:
                        replace_query = f'''
                        UPDATE users
                        SET {replace_keyword}=%s
                        WHERE userid=%s
                        '''
                        cursor.execute(
                            replace_query, (new_data, record_display))
                        connection.commit()
        except pkcs1.DecryptionError:
            print("Failed to decrypt password. It seems like you deleted the public and private keys associated with this entry. There is no way to recover this entry if you did not make a backup of the public and private keys. If you have the keys in a different location, please copy them to the 'keys' directory")

    def delete():
        cursor.execute("SELECT * FROM users")
        recordlist = list(cursor.fetchall())
        if recordlist == []:
            print("[INFO] No records available.")
        else:
            for i in recordlist:
                print(
                    f"[RECORD {i[0]}] --> (SERVICE) = {i[1]} && (USERNAME) = {i[2]}")
            record_delete = input("Enter the ID of the record to delete >> ")
            for i in recordlist:
                if str(i[0]) == record_delete:
                    print(
                        f"Record to be deleted:\n\n[RECORD {i[0]}]\n[SERVICE]: {i[1]}\n[USERNAME]: {i[2]}\n[EMAIL]: {i[3]}\n")
            confirmation = input(
                "ARE YOU SURE YOU WANT TO DELETE THE RECORD? IT CANNOT BE RECOVERED! TYPE 'YES' IN ALL CAPS >>> ")
            if confirmation == "YES":
                deletequery = "DELETE FROM users WHERE userid = %s"
                cursor.execute(deletequery, (record_delete, ))
                connection.commit()
                print("[INFO] The record has been deleted.")
            else:
                print("[INFO] The deletion process has been cancelled.")

    def wiki():
        print("""
                Q) What is a strong password?
                >> A password that is hard to predict by humans or computers. When people create login credentials, they often defeat the purpose by creating a memorable password.
                They choose their names, phone numbers, birthdays or even the word 'password' itself, the most commonly used password for many years. The key aspects of a strong
                password are length (the longer the better); a mix of letters (upper and lower case), numbers, and symbols, no ties to your personal information, and no dictionary words.
        
                Q) Why do people need strong passwords?
                >> A password is your personal key to a computer system. Passwords help to ensure that only authorized individuals access computer systems. Passwords also help to
                determine accountability for all transactions and other changes made to system resources, including data.
        
                Q) How do you safely secure strong passwords?
                >> There are numerous ways to secure your accounts, namely:
                
                1. Don't reuse your passwords:
                > Reusing the same passwords for multiple accounts is bad practice because it opens you up to credential stuffing attacks, which take leaked credentials from
                one site/service and use them on other sites/services.
        
                2. Use a password manager:
                > It can store all your passwords securely, so you don't have to worry about remembering them which allows you to use unique and strong passwords for all your
                important accounts, Good password managers are KeePass and Bitwarden.
        
                3. Don't write your passwords down:
                > If you write your password down it can be found and read by others.
        
                4. Don't share your password
                > Sharing your password may cause other people to use it maliciously or share it with others. Do not share it with anyone, even people with good intentions.
        
                Q) What are some recommended practices for password management?
                
                1. Always log out of your account if you are using a public computer:
                > This prevents people in public from getting access to your account.
        
                2. Implement 2FA (Two-Factor Authentication):
                > In addition to traditional credentials, like username and password, users have to confirm their identity with a one-time code sent to their mobile device
                or using a personalized USB token. The idea is that with 2FA, guessing or cracking the password alone is not enough for an attacker to gain access.
        
                3. Apply password encryption:
                Encryption provides additional protection for passwords, even if they are stolen by cybercriminals. The best practice is to consider end-to-end encryption
                that is non-reversible. In this way, you can protect passwords in transit over the network. Good examples of such encryption are AES256 and PGP.
        
                These are some good practices a user can do to keep his credentials safe.
                """)

    def strength():
        passwd = input(">> Enter a password to check its strength > ")
        if passwd in common_passwd:
            print("Your password is in the list of 1000 of the most common passwords. Change your password immediately.")
        else:
            poolsize = 0
            for l in passwd:
                if l.islower():
                    poolsize += 26
                elif l.isupper():
                    poolsize += 26
                elif l.isdigit():
                    poolsize += 10
                else:
                    poolsize += 32
            entropy = log2(poolsize**len(passwd))
            passwd = PasswordStats(passwd).strength()
            if passwd < 0.33:
                print(
                    f"[PASSWORD STRENGTH]: {passwd}\n[PASSWORD ENTROPY]: {entropy} bits\n\nYour password is extremely weak. Please change it.")
            elif passwd >= 0.33 and passwd < 0.66:
                print(
                    f"[PASSWORD STRENGTH]: {passwd}\n[PASSWORD ENTROPY]: {entropy} bits\n\nYour password is of fair strength. Please consider changing it to a stronger one.")
            elif passwd >= 0.66 and passwd < 0.80:
                print(
                    f"[PASSWORD STRENGTH]: {passwd}\n[PASSWORD ENTROPY]: {entropy} bits\n\nYour password is strong.")
            elif passwd >= 0.80 and passwd < 0.9:
                print(
                    f"[PASSWORD STRENGTH]: {passwd}\n[PASSWORD ENTROPY]: {entropy} bits\n\nYour password is incredibly strong.")
            else:
                print(
                    f"[PASSWORD STRENGTH]: {passwd}\n[PASSWORD ENTROPY]: {entropy} bits\n\nYour password is practically uncrackable.")

    def help_page():
        print("\nBelow is a list of all help topics that you can view:\n\n1. Usage Help\n2. Encryption Details\n3. About The Program\n")
        command = input(">> Enter the topic you want help with > ")
        if command == '1' or command[0].lower() == 'usa':
            print("\nThese are the commands available:\n\n1. Add Entry - add an entry to the database\n2. View Entries - view entries present in the database\n3. Generate Entry - generate a new username and/or password\n4. Edit Entry - Edit the details of a record.\n5. Delete Entry - delete an entry from the database\n6. Password Wiki - view the wiki for recommendations and common mistakes related to accounts and passwords\n7. Password Strength - check the strength of a password\n8. Help - view this list of commands again\n9. Clear - clear the screen\n10. Exit - exit the program\n")
        elif command == '2' or command[0].lower() == 'enc':
            print("This program uses RSA encrypt passwords. It does not encrypt 2FA secrets or notes. Please do not use this program in an enterprise environment as it was not built for such a purpose. This was made as a school project.")
        elif command == '3' or command[0].lower() == 'abo':
            print("This was a school project. It is a password manager that has a plethora of features like encrypted passwords and master passwords.")

    def clear():
        if name == 'nt':
            system('cls')
        else:
            system('clear')
        print("\nThese are the commands available:\n\n1. Add Entry - add an entry to the database\n2. View Entries - view entries present in the database\n3. Generate Entry - generate a new username and/or password\n4. Edit Entry - Edit the details of a record.\n5. Delete Entry - delete an entry from the database\n6. Password Wiki - view the wiki for recommendations and common mistakes related to accounts and passwords\n7. Password Strength - check the strength of a password\n8. Help - view this list of commands again\n9. Clear - clear the screen\n10. Exit - exit the program\n")

    print("Welcome to password manager!")
    print("\nThese are the commands available:\n\n1. Add Entry - add an entry to the database\n2. View Entries - view entries present in the database\n3. Generate Entry - generate a new username and/or password\n4. Edit Entry - Edit the details of a record.\n5. Delete Entry - delete an entry from the database\n6. Password Wiki - view the wiki for recommendations and common mistakes related to accounts and passwords\n7. Password Strength - check the strength of a password\n8. Help - view this list of commands again\n9. Clear - clear the screen\n10. Exit - exit the program\n")
    while True:
        try:
            try:
                command = input(">> Enter your command here > ")
                if command == '1' or command[0].lower() == 'a':
                    add()
                elif command == '2' or command[0].lower() == 'v':
                    view()
                elif command == '3' or command[0].lower() == 'g':
                    generate()
                elif command == '4' or command[0:2].lower() == 'ed':
                    replace()
                elif command == '5' or command[0].lower() == 'd':
                    delete()
                elif command == '6' or command[0].lower() == 'w':
                    wiki()
                elif command == '7' or command[0].lower() == 's':
                    strength()
                elif command == '8' or command[0].lower() == 'h':
                    help_page()
                elif command == '9' or command[0].lower() == 'c':
                    clear()
                elif command == '10' or command[0:2].lower() == 'ex':
                    print(
                        "\nYou have chosen to exit the program. Thank you for using it!")
                    exit()
                else:
                    print(
                        "You have entered an invalid command. Please type '8' or 'help' to get a list of the commands available.")
            except (EOFError, KeyboardInterrupt):
                print("\n[INFO] Command aborted")
        except IndexError:
            print("Your command cannot be empty. Please try again.")
except ModuleNotFoundError:
    print("\nYou have not installed the required modules. Follow these steps to do so:\n\n1. Open your terminal (Linux, MacOS) or Command Prompt (Windows) in the 'files' directory\n2. Confirm that the 'dependencies.txt' file exists.\n3. Type 'pip install -r dependencies.txt'.\n")
