"""Printing messages in a console"""
import os
import textwrap
import traceback

import colorama
from colorama import Fore, Back, Style

# from cloudmesh.common.variables import Variables

colorama.init()


def is_powershell():
    # this function is better than the one in util
    # but not using that one since it is a circular import
    return len(os.getenv("PSModulePath", "").split(os.pathsep)) >= 3


def indent(text, indent=2, width=128):
    """indents the given text by the indent specified and wrapping to the given width

    Args:
        text: the text to print
        indent: indent characters
        width: the width of the text

    Returns:

    """
    return "\n".join(
        textwrap.wrap(
            text,
            width=width,
            initial_indent=" " * indent,
            subsequent_indent=" " * indent,
        )
    )


class Console(object):
    """A simple way to print in a console terminal in color. Instead of using
    simply the print statement you can use special methods to indicate
    warnings, errors, ok and regular messages.

    Example Usage::

        Console.warning("Warning")
        Console.error("Error")
        Console.info("Info")
        Console.msg("msg")
        Console.ok("Success")

    One can switch the color mode off with::

        Console.color = False
        Console.error("Error")

    The color will be switched on by default.
    """

    color = True
    debug = True

    theme_color = {
        "HEADER": Fore.MAGENTA,
        "BLACK": Fore.BLACK,
        "CYAN": Fore.CYAN,
        "WHITE": Fore.WHITE,
        "BLUE": Fore.BLUE,
        "OKBLUE": Fore.BLUE,
        "OKGREEN": Fore.GREEN,
        "GREEN": Fore.GREEN,
        "FAIL": Fore.RED,
        "WARNING": Fore.MAGENTA,
        "RED": Fore.RED,
        "ENDC": Style.RESET_ALL,
        "BOLD": Style.BRIGHT,
        "NORMAL": Style.NORMAL
        # 'ENDC': '\033[0m',
        # 'BOLD': "\033[1m",
    }

    theme_bw = {
        "HEADER": "",
        "BLACK": "",
        "CYAN": "",
        "WHITE": "",
        "BLUE": "",
        "OKBLUE": "",
        "OKGREEN": "",
        "GREEN": "",
        "FAIL": "",
        "WARNING": "",
        "RED": "",
        "ENDC": "",
        "BOLD": "",
        "NORMAL": "",
    }

    theme = theme_color

    try:
        size = os.get_terminal_size()
        columns = size.columns
        lines = size.lines
    except:  # noqa: E722
        columns = 79
        lines = 24

    def line(self, c="="):
        try:
            size = os.get_terminal_size()
            columns = size.columns
        except:  # noqa: E722
            columns = 79

        # lines = size.lines

        print(columns * c)

    # noinspection PyPep8Naming
    def red(msg):
        print(Fore.RED + msg + Style.RESET_ALL)

    # noinspection PyPep8Naming
    def green(msg):
        print(Fore.GREEN + msg + Style.RESET_ALL)

    # noinspection PyPep8Naming
    def blue(msg):
        print(Fore.BLUE + msg + Style.RESET_ALL)

    @staticmethod
    def init():
        """initializes the Console"""
        colorama.init()

    @staticmethod
    def terminate():
        """terminates the program"""
        os._exit(1)

    @classmethod
    def set_debug(cls, on=True):
        """sets debugging on or of

        Args:
            on: if on debugging is set

        Returns:

        """
        cls.debug = on

    @staticmethod
    def set_theme(color=True):
        """defines if the console messages are printed in color

        Args:
            color: if True its printed in color

        Returns:

        """
        if color:
            Console.theme = Console.theme_color
        else:
            Console.theme = Console.theme_bw
        Console.color = color

    @staticmethod
    def get(name):
        """returns the default theme for printing console messages

        Args:
            name: the name of the theme

        Returns:

        """
        if name in Console.theme:
            return Console.theme[name]
        else:
            return Console.theme["BLACK"]

    @staticmethod
    def txt_msg(message, width=79):
        """prints a message to the screen

        Args:
            message: the message to print
            width: teh width of the line

        Returns:

        """
        return textwrap.fill(message, width=width)

    @staticmethod
    def msg(*message):
        """prints a message

        Args:
            *message: the message to print

        Returns:

        """
        str = " ".join(message)
        print(str)

    @staticmethod
    def bullets(elements):
        """prints elemnets of a list as bullet list

        Args:
            elements: the list
        """
        for name in elements:
            print("*", name)

    @classmethod
    def error(cls, message, prefix=True, traceflag=False):
        """prints an error message

        Args:
            message: the message
            prefix: a prefix for the message
            traceflag: if true the stack trace is retrieved and printed

        Returns:

        """
        # print (message, prefix)
        # variables = Variables()
        # traceflag = traceflag or variables['trace']

        message = message or ""
        if prefix:
            text = "ERROR: "
        else:
            text = ""
        if cls.color:
            if is_powershell():
                print(
                    Fore.RED + Back.WHITE + text + message + Console.theme_color["ENDC"]
                )
            else:
                cls.cprint("FAIL", text, str(message))
        else:
            print(cls.txt_msg(text + str(message)))

        if traceflag and cls.debug:
            trace = traceback.format_exc().strip()
            if trace:
                print()
                print("Trace:")
                print("\n    ".join(str(trace).splitlines()))
                print()

    @staticmethod
    def TODO(message, prefix=True, traceflag=True):
        """prints a TODO message

        Args:
            message: the message
            prefix: if set to true it prints TODO: as prefix
            traceflag: if true the stack trace is retrieved and printed

        Returns:

        """
        message = message or ""
        if prefix:
            text = "TODO: "
        else:
            text = ""
        if Console.color:
            Console.cprint("FAIL", text, str(message))
        else:
            print(Console.msg(text + str(message)))

        trace = traceback.format_exc().strip()

        if traceflag and trace != "None":
            print()
            print("\n".join(str(trace).splitlines()))
            print()

    @staticmethod
    def debug_msg(message):
        """print a debug message

        Args:
            message: the message

        Returns:

        """
        message = message or ""
        if Console.color:
            Console.cprint("RED", "DEBUG: ", message)
        else:
            print(Console.msg("DEBUG: " + message))

    @staticmethod
    def info(message):
        """prints an informational message

        Args:
            message: the message

        Returns:

        """
        message = message or ""
        if Console.color:
            Console.cprint("OKBLUE", "INFO: ", message)
        else:
            print(Console.msg("INFO: " + message))

    @staticmethod
    def warning(message):
        """prints a warning

        Args:
            message: the message

        Returns:

        """
        message = message or ""
        if Console.color:
            if is_powershell():
                # fixes powershell problem https://github.com/nodejs/node/issues/14243
                print(
                    Fore.MAGENTA
                    + Style.BRIGHT
                    + "WARNING: "
                    + message
                    + Console.theme_color["ENDC"]
                )
            else:
                Console.cprint("WARNING", "WARNING: ", message)
        else:
            print(Console.msg("WARNING: " + message))

    @staticmethod
    def ok(message):
        """prints an ok message

        Args:
            message: the message<

        Returns:

        """
        message = message or ""
        if Console.color:
            Console.cprint("OKGREEN", "", message)
        else:
            print(Console.msg(message))

    @staticmethod
    def cprint(color="BLUE", prefix="", message=""):
        """prints a message in a given color

        Args:
            color: the color as defined in the theme
            prefix: the prefix (a string)
            message: the message

        Returns:

        """
        message = message or ""
        prefix = prefix or ""

        print(
            Console.theme_color[color] + prefix + message + Console.theme_color["ENDC"]
        )

    @staticmethod
    def text(color="RED", prefix=None, message=None):
        """returns a message in a given color

        Args:
            color: the color as defined in the theme
            prefix: the prefix (a string)
            message: the message

        Returns:

        """
        message = message or ""
        prefix = prefix or ""
        return Console.theme[color] + prefix + message + Console.theme["ENDC"]


#
# Example
#


if __name__ == "__main__":
    print(Console.color)

    print(Console.theme)

    Console.line()
    Console.warning("Warning")
    Console.error("Error")
    Console.info("Info")
    Console.msg("msg")
    Console.ok("Ok")

    Console.color = False
    print(Console.color)
    Console.error("Error")

    print(Fore.RED + "some red text")
    print(Back.GREEN + "and with a green background")
    print(Style.DIM + "and in dim text")
    print(Fore.RESET + Back.RESET + Style.RESET_ALL)
    print("back to normal now")
    Console.line()
