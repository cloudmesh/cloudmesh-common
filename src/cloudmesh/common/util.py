import csv
import csv
import glob
import inspect
import os
import platform
import random
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping, Iterable
from contextlib import contextmanager
from getpass import getpass
from pathlib import Path

import pyfiglet
import requests
from cloudmesh.common.console import Console


@contextmanager
def tempdir(*args, **kwargs):
    """A contextmanager to work in an auto-removed temporary directory

    Arguments are passed through to tempfile.mkdtemp

    example:

    >>> with tempdir() as path:
    ...    pass
    """

    d = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield d
    finally:
        shutil.rmtree(d)


def check_root(dryrun=False, terminate=True):
    """check if I am the root user. If not, simply exits the program.

    Args:
        dryrun (bool): if set to true, does not terminate if not root
            user
        terminate (bool): terminates if not root user and dryrun is
            False
    """
    uid = os.getuid()
    if uid == 0:
        Console.ok("You are executing as a root user")
    else:
        Console.error("You do not run as root")
        if terminate and not dryrun:
            sys.exit()


def exponential_backoff(fn, sleeptime_s_max=30 * 60):
    """Calls `fn` until it returns True, with an exponentially increasing wait
    time between calls

    Args:
        fn (object): the function to be called that returns Truw or
            False
        sleeptime_s_max (int): the sleep time in milliseconds

    Returns:
        None
    """
    sleeptime_ms = 500
    while True:
        if fn():
            return True
        else:
            print("Sleeping {} ms".format(sleeptime_ms))
            time.sleep(sleeptime_ms / 1000.0)
            sleeptime_ms *= 2

        if sleeptime_ms / 1000.0 > sleeptime_s_max:
            return False


def download(source, destination, force=False):
    """Downloads the file from source to destination

    For large files, see cloudmesh.common.Shell.download

    Args:
        source: The http source
        destination: The destination in the file system
        force: If True the file will be downloaded even if it already
            exists
    """
    if os.path.isfile(destination) and not force:
        Console.warning(f"File {destination} already exists. " "Skipping download ...")
    else:
        directory = os.path.dirname(destination)
        Path(directory).mkdir(parents=True, exist_ok=True)
        r = requests.get(source, allow_redirects=True)
        open(destination, "wb").write(r.content)


def csv_to_list(csv_string, sep=","):
    """Converts a CSV table from a string to a list of lists

    Args:
        csv_string (string): The CSV table

    Returns:
        list: list of lists
    """
    reader = csv.reader(csv_string.splitlines(), delimiter=sep)

    # Read the CSV table into a list of lists.
    list_of_lists = []
    for row in reader:
        list_of_lists.append(row)
    return list_of_lists


def search(lines, pattern):
    """return all lines that match the pattern
    #TODO: we need an example

    Args:
        lines
        pattern

    Returns:

    """
    p = pattern.replace("*", ".*")
    test = re.compile(p)
    result = []
    for l in lines:  # noqa: E741
        if test.search(l):
            result.append(l)
    return result


def grep(pattern, filename):
    """Very simple grep that returns the first matching line in a file.
    String matching only, does not do REs as currently implemented.
    """
    try:
        # for line in file
        # if line matches pattern:
        #    return line
        return next((L for L in open(filename) if L.find(pattern) >= 0))
    except StopIteration:
        return ""


def is_local(host):
    """Checks if the host is the localhost

    Args:
        host: The hostname or ip

    Returns:
        True if the host is the localhost
    """
    return host in [
        "127.0.0.1",
        "localhost",
        socket.gethostname(),
        # just in case socket.gethostname() does not work  we also try the following:
        platform.node(),
        socket.gethostbyaddr(socket.gethostname())[0],
    ]


# noinspection PyPep8
def is_gitbash():
    """returns True if you run in a Windows gitbash

    Returns:
        True if gitbash
    """
    try:
        exepath = os.environ["EXEPATH"]
        return "Git" in exepath
    except:  # noqa: E722
        return False


def is_powershell():
    """True if you run in powershell

    Returns:
        True if you run in powershell
    """
    # psutil.Process(parent_pid).name() returns -
    # cmd.exe for CMD
    # powershell.exe for powershell
    # bash.exe for git bash
    if platform.system() == "Windows":
        import psutil

        return psutil.Process(os.getppid()).name() == "powershell.exe"
    else:
        return False


def is_cmd_exe():
    """return True if you run in a Windows CMD

    Returns:
        True if you run in CMD
    """
    if is_gitbash():
        return False
    else:
        try:
            return os.environ["OS"] == "Windows_NT"
        except:  # noqa: E722
            return False


def path_expand(text, slashreplace=True):
    """returns a string with expanded variable.

    :param text: the path to be expanded, which can include ~ and environment variables
    :param text: string

    """
    result = os.path.expandvars(os.path.expanduser(text))

    if result.startswith("./"):
        result = result.replace(".", os.getcwd(), 1)

    if is_gitbash() or is_cmd_exe():
        if slashreplace:
            result = result.replace("/", "\\")

    return result


def convert_from_unicode(data):
    """Converts unicode data to a string

    Args:
        data: the data to convert

    Returns:
        converted data
    """
    if isinstance(data, str):
        return str(data)
    elif isinstance(data, Mapping):
        return dict(map(convert_from_unicode, data.items()))
    elif isinstance(data, Iterable):
        return type(data)(map(convert_from_unicode, data))
    else:
        return data


def yn_choice(message, default="y", tries=None):
    """asks for a yes/no question.

    Args:
        tries: the number of tries
        message: the message containing the question
        default: the default answer
    """
    # http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input"""
    choices = "Y/n" if default.lower() in ("y", "yes") else "y/N"
    if tries is None:
        choice = input(f"{message} ({choices}) ")
        values = ("y", "yes", "") if default == "y" else ("y", "yes")
        return True if choice.strip().lower() in values else False
    else:
        while tries > 0:
            choice = input(f"{message} ({choices}) ('q' to discard)")
            choice = choice.strip().lower()
            if choice in ["y", "yes"]:
                return True
            elif choice in ["n", "no", "q"]:
                return False
            else:
                print("Invalid input...")
                tries -= 1


def str_banner(
    txt=None,
    c="-",
    prefix="#",
    debug=True,
    label=None,
    color="BLUE",
    padding=False,
    figlet=False,
    font="big",
):
    """prints a banner of the form with a frame of # around the txt::

    # --------------------------
    # txt
    # --------------------------

    Args:
        color: prints in the given color
        label: adds a label
        debug: prints only if debug is true
        txt (string): a text message to be printed
        c (character): the character used instead of c
    """
    output = ""
    if debug:
        output = "\n"
        output += prefix + " " + 70 * c + "\n"
        if padding:
            output += prefix + "\n"
        if label is not None:
            output += prefix + " " + label + "\n"
            output += prefix + " " + 70 * c + "\n"

        if txt is not None:
            if figlet:
                txt = pyfiglet.figlet_format(txt, font=font)

            for line in txt.splitlines():
                output += prefix + " " + line + "\n"
            if padding:
                output += prefix + "\n"
            output += prefix + " " + 70 * c + "\n"

    return output


def banner(
    txt=None,
    c="-",
    prefix="#",
    debug=True,
    label=None,
    color="BLUE",
    padding=False,
    figlet=False,
    font="big",
):
    """prints a banner of the form with a frame of # around the txt::

    # --------------------------
    # txt
    # --------------------------

    Args:
        color: prints in the given color
        label: adds a label
        debug: prints only if debug is true
        txt (string): a text message to be printed
        c (character): the character used instead of c
        padding (bool): ads additional comment line around the text so
            the banner is larger
    """

    output = str_banner(
        txt=txt,
        c=c,
        prefix=prefix,
        debug=debug,
        label=label,
        color=color,
        padding=padding,
        figlet=figlet,
        font=font,
    )
    Console.cprint(color, "", output)


# noinspection PyPep8Naming
def HEADING(txt=None, c="#", color="HEADER"):
    """Prints a message to stdout with #### surrounding it. This is useful for
    pytests to better distinguish them.

    Args:
        c: uses the given char to wrap the header
        txt (string): a text message to be printed
    """
    frame = inspect.getouterframes(inspect.currentframe())

    filename = frame[1][1].replace(os.getcwd(), "")
    line = frame[1][2] - 1
    method = frame[1][3]
    if txt is None:
        msg = "{} {} {}".format(method, filename, line)
    else:
        msg = "{}\n {} {} {}".format(txt, method, filename, line)

    print()
    banner(msg, c=c, color=color)


# noinspection PyPep8Naming
def FUNCTIONNAME():
    """Returns the name of a function."""
    frame = inspect.getouterframes(inspect.currentframe())

    filename = frame[1][1].replace(os.getcwd(), "")
    line = frame[1][2] - 1
    method = frame[1][3]
    return method


def backup_name(filename):
    """
    Args:
        filename (string): given a filename creates a backup name of the
            form filename.bak.1. If the filename already exists the
            number will be increased as  much as needed so the file does
            not exist in the given location. The filename can consists a
            path and is expanded with ~ and environment variables.

    Returns:
        string
    """
    location = path_expand(filename)
    n = 0
    found = True
    backup = None
    while found:
        n += 1
        backup = "{0}.bak.{1}".format(location, n)
        found = os.path.isfile(backup)
    return backup


def auto_create_version(class_name, version, filename="__init__.py"):
    """creates a version number in the __init__.py file.
    it can be accessed with __version__

    Args:
        class_name
        version
        filename

    Returns:

    """
    version_filename = Path(
        "{classname}/{filename}".format(classname=class_name, filename=filename)
    )
    with open(version_filename, "r") as f:
        content = f.read()

    if content != '__version__ = "{0}"'.format(version):
        banner("Updating version to {0}".format(version))
        with open(version_filename, "w") as text_file:
            text_file.write('__version__ = "{0:s}"'.format(version))


def auto_create_requirements(requirements):
    """creates a requirement.txt file form the requirements in the list. If the file
    exists, it get changed only if the
    requirements in the list are different from the existing file

    Args:
        requirements: the requirements in a list
    """
    banner("Creating requirements.txt file")
    try:
        with open("requirements.txt", "r") as f:
            file_content = f.read()
    except:  # noqa: E722
        file_content = ""

    setup_requirements = "\n".join(requirements)

    if setup_requirements != file_content:
        with open("requirements.txt", "w") as text_file:
            text_file.write(setup_requirements)


def copy_files(files_glob, source_dir, dest_dir):
    """copies the files to the destination

    Args:
        files_glob: `*.yaml`
        source_dir: source directory
        dest_dir: destination directory
    """

    files = glob.iglob(os.path.join(source_dir, files_glob))
    for filename in files:
        if os.path.isfile(filename):
            shutil.copy2(filename, dest_dir)


def readfile(filename, mode="r", encoding=None):
    """returns the content of a file

    Args:
        filename: the filename
        encoding: type of encoding to read the file.
    if None then no encoding is used.
    other values are utf-8, cp850

    Returns:

    """
    if mode != "r" and mode != "rb":
        Console.error(f"incorrect mode : expected 'r' or 'rb' given {mode}")
    else:
        content = None
        if encoding is None:
            with open(path_expand(filename), mode) as f:
                content = f.read()
                f.close()
        else:
            with open(path_expand(filename), mode, encoding=encoding) as f:
                content = f.read()
                f.close()
        return content


def writefile(filename, content):
    """writes the content into the file

    Args:
        filename: the filename
        content: teh content

    Returns:

    """
    directory = os.path.dirname(filename)
    if directory not in [None, ""]:
        os.makedirs(directory, exist_ok=True)
    with open(path_expand(filename), "w") as outfile:
        outfile.write(content)
        outfile.truncate()


def appendfile(filename, content):
    """writes the content into the file

    Args:
        filename: the filename
        content: teh content

    Returns:

    """
    with open(path_expand(filename), "a") as outfile:
        outfile.write(content)


def writefd(filename, content, mode="w", flags=os.O_RDWR | os.O_CREAT, mask=0o600):
    """writes the content into the file and control permissions

    Args:
        filename: the full or relative path to the filename
        content: the content being written
        mode: the write mode ('w') or write bytes mode ('wb')
        flags: the os flags that determine the permissions for the file
        mask: the mask that the permissions will be applied to
    """
    if mode != "w" and mode != "wb":
        Console.error(f"incorrect mode : expected 'w' or 'wb' given {mode}")

    with os.fdopen(os.open(filename, flags, mask), mode) as outfile:
        outfile.write(content)
        outfile.truncate()
        outfile.close()


def sudo_readfile(filename, split=True, trim=False):
    """Reads the content of the file as sudo and returns the result

    Args:
        filename (str): the filename
        split (bool): uf true returns a list of lines
        trim (bool): trim trailing whitespace. This is useful to prevent
            empty string entries when splitting by '\n'

    Returns:
        str or list: the content
    """
    result = subprocess.getoutput(f"sudo cat {filename}")

    if trim:
        result = result.rstrip()

    if split:
        result = result.split("\n")

    return result


# Reference: http://interactivepython.org/runestone/static/everyday/2013/01/3_password.html
def generate_password(length=8, lower=True, upper=True, number=True):
    """generates a simple password. We should not really use this in production.

    Args:
        length: the length of the password
        lower: True of lower case characters are allowed
        upper: True if upper case characters are allowed
        number: True if numbers are allowed

    Returns:

    """
    lletters = "abcdefghijklmnopqrstuvwxyz"
    uletters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # This doesn't guarantee both lower and upper cases will show up
    alphabet = lletters + uletters
    digit = "0123456789"
    mypw = ""

    def _random_character(texts):
        return texts[random.randrange(len(texts))]

    if not lower:
        alphabet = uletters
    elif not upper:
        alphabet = lletters

    for i in range(length):
        # last half length will be filled with numbers
        if number and i >= int(length / 2):
            mypw = mypw + _random_character(digit)
        else:
            mypw = mypw + _random_character(alphabet)
    return mypw


def str_bool(value):
    return str(value).lower() in ["yes", "1", "y", "true", "t"]


def get_password(prompt):
    from cloudmesh.common.systeminfo import os_is_windows

    try:
        if os_is_windows() and is_gitbash():
            continuing = True
            while continuing:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                subprocess.check_call(["stty", "-echo"])
                password = input()
                subprocess.check_call(["stty", "echo"])
                sys.stdout.write("Please retype the password:\n")
                sys.stdout.flush()
                subprocess.check_call(["stty", "-echo"])
                password2 = input()
                subprocess.check_call(["stty", "echo"])
                if password == password2:
                    continuing = False
                else:
                    Console.error("Passwords do not match\n")
            return password
        else:
            continuing = True
            while continuing:
                password = getpass(prompt)
                password2 = getpass("Please retype the password:\n")
                if password == password2:
                    continuing = False
                else:
                    Console.error("Passwords do not match\n")
            return password
    except KeyboardInterrupt:
        # Console.error('Detected Ctrl + C. Quitting...')
        if is_gitbash():
            subprocess.check_call(["stty", "echo"])
        raise ValueError("Detected Ctrl + C. Quitting...")
