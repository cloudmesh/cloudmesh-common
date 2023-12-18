import random
import string


def generate_strong_pass():
    """Generates a password from letters, digits and punctuation

    Returns:
        str: password
    """
    length = random.randint(10, 15)
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(password_characters) for i in range(length))
