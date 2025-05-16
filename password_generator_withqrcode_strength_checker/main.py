import random, os, qrcode


def new_pass():
    char = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%&1234567890"
    password = ''
    length = int(input("Enter the length of password you want: "))
    for i in range(length):
        password += random.choice(char)
    print("Password Generated: ", password)
    print("\nDo you want to generate QR code of the password?")
    qr_choice = input("Enter your choice Y for Yes and N for No: ")
    if qr_choice.lower() == "y":
        qr_gen(password)
    else:
        print("Thank You for using our Passsword Generator!")

def qr_gen(password):
    password = "Your password is: "+password
    img=qrcode.make(password)
    path=os.getcwd()+"\qrcode.png"
    img.save(path)
    print("Your QR Code has been generated at",path)


def strength_check():
    password = input("Enter your password for Strength check: ")
    if len(password) < 8:
        print("WEAK Password!")
    elif len(password)>8:
        a =False
        b=False
        c = False
        for i in password:
            if i.isupper():
                a=True
            elif i.islower():
                b=True
            elif i.isdigit():
                c = True
        if a and b and c:
            print("STRONG Password!")
        else:
            print("MODERATE Password!")
    else:
        print("Invalid Input!\n")



#MAIN Program!!
while True:
    print("\nWelcome to PASSWORD GENERATOR")
    print("Made by: @artisticpy\n")
    print("Type 1 for Generating Password")
    print("Type 2 for Password Strenght Check")
    print("Type 3 to EXIT\n")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        new_pass()
    elif choice == 2:
        strength_check()
    elif choice == 3:
        break
    else:
        print("Invalid Input!")