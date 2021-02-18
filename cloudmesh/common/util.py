import subprocess
import collections
import glob
import inspect
import os
import random
import re
import shutil
import tempfile
import time
from contextlib import contextmanager
import sys
import psutil
import requests
from pathlib import Path
from cloudmesh.common.console import Console
import pyfiglet

try:
    collectionsAbc = collections.abc
except AttributeError:
    collectionsAbc = collections


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


def check_root(terminate=True):
    """
    Tests if the root user is used

    :param terminate: if true exist the program
    :return:
    """
    uid = os.getuid()
    if uid == 0:
        Console.ok("You are executing a a root user")
    else:
        Console.error("You do not run as root")
        if terminate:
            sys.exit()


def exponential_backoff(fn, sleeptime_s_max=30 * 60):
    """Calls `fn` until it returns True, with an exponentially increasing wait time between calls"""

    sleeptime_ms = 500
    while True:
        if fn():
            return True
        else:
            print('Sleeping {} ms'.format(sleeptime_ms))
            time.sleep(sleeptime_ms / 1000.0)
            sleeptime_ms *= 2

        if sleeptime_ms / 1000.0 > sleeptime_s_max:
            return False


def download(source, destination, force=False):
    """
    Downloads the file from source to destination

    :param source: The http source
    :param destination: The destination in the file system
    :param force: If True the file will be downloaded even if
                  it already exists
    """
    if os.path.isfile(destination) and not force:
        Console.warning(f"File {destination} already exists. "
                        "Skipping download ...")
    else:

        directory = os.path.dirname(destination)
        Path(directory).mkdir(parents=True, exist_ok=True)
        r = requests.get(source, allow_redirects=True)
        open(destination, 'wb').write(r.content)


def search(lines, pattern):
    """
    return all lines that match the pattern
    #TODO: we need an example

    :param lines:
    :param pattern:
    :return:
    """
    p = pattern.replace("*", ".*")
    test = re.compile(p)
    result = []
    for l in lines:
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
        return ''


# noinspection PyPep8
def is_gitbash():
    """
    returns True if you run in a Windows gitbash

    :return: True if gitbash
    """
    try:
        exepath = os.environ['EXEPATH']
        return "Git" in exepath
    except:
        return False


def is_powershell():
    """
    True if you run in powershell

    :return: True if you run in powershell
    """
    # psutil.Process(parent_pid).name() returns -
    # cmd.exe for CMD
    # powershell.exe for powershell
    # bash.exe for git bash
    return (psutil.Process(os.getppid()).name() == "powershell.exe")


def is_cmd_exe():
    """
    return True if you run in a Windows CMD

    :return: True if you run in CMD
    """
    if is_gitbash():
        return False
    else:
        try:
            return os.environ['OS'] == 'Windows_NT'
        except:
            return False


def path_expand(text):
    """ returns a string with expanded variable.

    :param text: the path to be expanded, which can include ~ and environment variables
    :param text: string

    """
    result = os.path.expandvars(os.path.expanduser(text))

    if result.startswith("."):
        result = result.replace(".", os.getcwd(), 1)

    if is_gitbash() or is_cmd_exe():
        result = result.replace("/", "\\")

    return result


def convert_from_unicode(data):
    """
    converts unicode data to a string
    :param data: the data to convert
    :return:
    """
    # if isinstance(data, basestring):

    if isinstance(data, str):
        return str(data)
    elif isinstance(data, collectionsAbc.Mapping):
        return dict(map(convert_from_unicode, data.items()))
    elif isinstance(data, collectionsAbc.Iterable):
        return type(data)(map(convert_from_unicode, data))
    else:
        return data


def yn_choice(message, default='y', tries=None):
    """asks for a yes/no question.

    :param tries: the number of tries
    :param message: the message containing the question
    :param default: the default answer
    """
    # http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input"""
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    if tries is None:
        choice = input("%s (%s) " % (message, choices))
        values = ('y', 'yes', '') if default == 'y' else ('y', 'yes')
        return True if choice.strip().lower() in values else False
    else:
        while tries > 0:
            choice = input(
                "%s (%s) (%s)" % (message, choices, "'q' to discard"))
            choice = choice.strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no', 'q']:
                return False
            else:
                print("Invalid input...")
                tries -= 1


def str_banner(txt=None, c="-", prefix="#", debug=True, label=None,
               color="BLUE", padding=False,
               figlet=False, font="big"):
    """
    prints a banner of the form with a frame of # around the txt::

    # --------------------------
    # txt
    # --------------------------

    :param color: prints in the given color
    :param label: adds a label
    :param debug: prints only if debug is true
    :param txt: a text message to be printed
    :type txt: string
    :param c: the character used instead of c
    :type c: character
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
               txt = pyfiglet.figlet_format(txt,font=font)

            for line in txt.splitlines():
                output += prefix + " " + line + "\n"
            if padding:
                output += prefix + "\n"
            output += prefix + " " + 70 * c + "\n"

    return output

def banner(txt=None, c="-", prefix="#", debug=True, label=None,
           color="BLUE", padding=False,
           figlet=False, font="big"):
    """
    prints a banner of the form with a frame of # around the txt::

    # --------------------------
    # txt
    # --------------------------

    :param color: prints in the given color
    :param label: adds a label
    :param debug: prints only if debug is true
    :param txt: a text message to be printed
    :type txt: string
    :param c: the character used instead of c
    :type c: character
    :param padding: ads additional comment line around the text so the banner is larger
    :type padding: bool
    """

    output = str_banner(txt=txt, c=c, prefix=prefix, debug=debug, label=label,
                        color=color, padding=padding, figlet=figlet, font=font)
    Console.cprint(color, "", output)


# noinspection PyPep8Naming
def HEADING(txt=None, c="#", color="HEADER"):
    """
    Prints a message to stdout with #### surrounding it. This is useful for
    pytests to better distinguish them.

    :param c: uses the given char to wrap the header
    :param txt: a text message to be printed
    :type txt: string
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


def backup_name(filename):
    """
    :param filename: given a filename creates a backup name of the form
                     filename.bak.1. If the filename already exists
                     the number will be increased as  much as needed so
                     the file does not exist in the given location.
                     The filename can consists a path and is expanded
                     with ~ and environment variables.
    :type filename: string
    :rtype: string
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
    """
    creates a version number in the __init__.py file.
    it can be accessed with __version__
    :param class_name:
    :param version:
    :param filename:
    :return:
    """
    version_filename = Path(
        "{classname}/{filename}".format(classname=class_name,
                                        filename=filename))
    with open(version_filename, "r") as f:
        content = f.read()

    if content != '__version__ = "{0}"'.format(version):
        banner("Updating version to {0}".format(version))
        with open(version_filename, "w") as text_file:
            text_file.write('__version__ = "{0:s}"'.format(version))


def auto_create_requirements(requirements):
    """

    creates a requirement.txt file form the requirements in the list. If the file
    exists, it get changed only if the
    requirements in the list are different from the existing file

    :param requirements: the requirements in a list
    """
    banner("Creating requirements.txt file")
    try:
        with open("requirements.txt", "r") as f:
            file_content = f.read()
    except:
        file_content = ""

    setup_requirements = '\n'.join(requirements)

    if setup_requirements != file_content:
        with open("requirements.txt", "w") as text_file:
            text_file.write(setup_requirements)


def copy_files(files_glob, source_dir, dest_dir):
    """
    copies the files to the destination

    :param files_glob: `*.yaml`
    :param source_dir: source directory
    :param dest_dir: destination directory

    """

    files = glob.iglob(os.path.join(source_dir, files_glob))
    for filename in files:
        if os.path.isfile(filename):
            shutil.copy2(filename, dest_dir)


def readfile(filename, mode='r'):
    """
    returns the content of a file
    :param filename: the filename
    :return:
    """
    if mode != 'r' and mode != 'rb':
        Console.error(f"incorrect mode : expected 'r' or 'rb' given {mode}")
    else:
        with open(path_expand(filename), mode)as f:
            content = f.read()
            f.close()
        return content


def writefile(filename, content):
    """
    writes the content into the file
    :param filename: the filename
    :param content: teh content
    :return:
    """
    with open(path_expand(filename), 'w') as outfile:
        outfile.write(content)
        outfile.truncate()


def writefd(filename, content, mode='w', flags=os.O_RDWR | os.O_CREAT, mask=0o600):
    """
    writes the content into the file and control permissions
    :param filename: the full or relative path to the filename
    :param content: the content being written
    :param mode: the write mode ('w') or write bytes mode ('wb')
    :param flags: the os flags that determine the permissions for the file
    :param mask: the mask that the permissions will be applied to
    """
    if mode != 'w' and mode != 'wb':
        Console.error(f"incorrect mode : expected 'w' or 'wb' given {mode}")

    with os.fdopen(os.open(filename, flags, mask), mode) as outfile:
        outfile.write(content)
        outfile.truncate()
        outfile.close()


def sudo_readfile(filename, split=True, trim=False):
    """
    Reads the content of the file as sudo and returns the result

    :param filename: the filename
    :type filename: str
    :param split: uf true returns a list of lines
    :type split: bool
    :param trim: trim trailing whitespace. This is useful to
                 prevent empty string entries when splitting by '\n'
    :type trim: bool
    :return: the content
    :rtype: str or list
    """
    result = subprocess.getoutput(f"sudo cat {filename}")

    if trim:
        result = result.rstrip()

    if split:
        result = result.split('\n')

    return result


def sudo_writefile(filename, content, append=False):
    """
    Writes the content in the the given file.

    :param filename: the filename
    :type filename: str
    :param content: the content
    :type content: str
    :param append: if true it append it at the end, otherwise the file will be overwritten
    :type append: bool
    :return: the output created by the write process
    :rtype: int
    """

    tmp_dir = path_expand("~/.cloudmesh/tmp")
    os.system(f'mkdir -p {tmp_dir}')
    tmp = path_expand("~/.cloudmesh/tmp/tmp.txt")

    if append:
        content = sudo_readfile(filename, split=False) + content

    writefile(tmp, content)

    result = subprocess.getstatusoutput(f"sudo cp {tmp} {filename}")

    # If exit code is not 0
    if result[0] != 0:
        Console.warning(f"{filename} was not created correctly -> {result[1]}")

    try:
        os.remove(tmp)
    except:
        Console.warning(f"{tmp} was not removed correctly.")

    return result[1]


# Reference: http://interactivepython.org/runestone/static/everyday/2013/01/3_password.html
def generate_password(length=8, lower=True, upper=True, number=True):
    """
    generates a simple password. We should not really use this in production.
    :param length: the length of the password
    :param lower: True of lower case characters are allowed
    :param upper: True if upper case characters are allowed
    :param number: True if numbers are allowed
    :return:
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
