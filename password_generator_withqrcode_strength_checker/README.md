# Password Generator with QR Code and Strength Checker

This Python script generates secure, random passwords, provides the option to create a QR code for easy sharing, and includes a password strength checker. The strength checker evaluates passwords based on criteria like length, uppercase letters, lowercase letters, and digits. This script aims to help users create strong, secure passwords and offers a convenient way to share them via QR codes.

## Features

- **Password Generation**: Generates random passwords with customizable length and character set, including uppercase, lowercase, digits, and special symbols.
- **Password Strength Check**: Evaluates the strength of a user-provided password based on length and character diversity (uppercase, lowercase, digits).
- **QR Code Generation**: Optionally generates a QR code for the generated password, which can be securely stored or shared.
- **Interactive Interface**: Prompts users to choose between generating a new password or checking the strength of an existing password.

## Repository

This project is hosted on GitHub as **[password_generator_withqrcode_strength_checker](https://github.com/artisticpy/password_generator_withqrcode_strength_checker)**. Clone or download the repository to use the script.

## Usage

1. **Clone the repository** or download the `password_generator_withqrcode_strength_checker.py` script:
    ```bash
    git clone https://github.com/artisticpy/password_generator_withqrcode_strength_checker.git
    ```
2. **Run the script** with Python. You can execute the script in your terminal or command prompt by navigating to the folder containing the file and running:
    ```bash
    python password_generator_withqrcode_strength_checker.py
    ```
3. **Select an option** from the menu:
   - Choose **1** to generate a random password.
   - Choose **2** to check the strength of an existing password.
   - Choose **3** to exit the program.
4. If you choose to generate a password, the script will:
   - Prompt you for the desired password length.
   - Display the generated password.
   - Offer to create a QR code for the password.
5. If you choose to check the password strength, enter your password when prompted, and the script will evaluate it for strength based on the following:
   - **Weak**: Password is shorter than 8 characters.
   - **Moderate**: Password is at least 8 characters but lacks a mix of character types.
   - **Strong**: Password includes a mix of uppercase letters, lowercase letters, and digits.
6. If a QR code is generated, the script will save it as a PNG file in the current directory.

## Dependencies

To run the script, you will need the following Python libraries:

- `qrcode`: Used to generate the QR code for the password.
- `os` and `random`: Used for file operations and generating random characters, respectively.

Install the required library using `pip`:

```bash
pip install qrcode
