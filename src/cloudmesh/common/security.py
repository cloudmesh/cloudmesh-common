import random
import string
import os
import subprocess


def can_use_sudo():
    """Checks if the current user has sudo privileges.

    Returns:
        bool: True if the user has sudo privileges, False otherwise.
    """
    try:
        # The 'id -u' command returns the user ID. When run with sudo, it should return 0 (the ID of the root user).
        output = subprocess.check_output("sudo id -u", shell=True).decode().strip()
        return output == "0"
    except subprocess.CalledProcessError:
        return False


def generate_strong_pass():
    """Generates a password from letters, digits and punctuation

    Returns:
        str: password
    """
    length = random.randint(10, 15)
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(password_characters) for i in range(length))
