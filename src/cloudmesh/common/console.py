"""Printing messages in a console"""
import os
import textwrap
import traceback

from rich.console import Console as RichConsole
from rich.text import Text
# from cloudmesh.common.variables import Variables

RichConsole = RichConsole()


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
        "HEADER": "magenta",
        "BLACK": "black",
        "CYAN": "cyan",
        "WHITE": "white",
        "BLUE": "blue",
        "OKBLUE": "blue",
        "OKGREEN": "green",
        "GREEN": "green",
        "FAIL": "red",
        "WARNING": "magenta",
        "RED": "red",
        "ENDC": "default",
        "BOLD": "bold",
        "NORMAL": "default",
        "MAGENTA": "magenta"
    }

    if is_powershell():
        for key in theme_color:
            theme_color[key] = "bold " + theme_color[key]
        theme_color["BLUE"] = "blue on white"

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
        "MAGENTA": ""
    }

    theme = theme_color

    try:
        size = os.get_terminal_size()
        columns = size.columns
        lines = size.lines
    except:  # noqa: E722
        columns = 79
        lines = 24

    @classmethod
    def line(self, c="="):
        try:
            size = os.get_terminal_size()
            columns = size.columns
        except:  # noqa: E722
            columns = 79

        # lines = size.lines

        print(columns * c)

    def red(msg):
        RichConsole.print(msg, style="red")

    def green(msg):
        RichConsole.print(msg, style="green")

    def blue(msg):
        RichConsole.print(msg, style="blue")

    @staticmethod
    def init():
        """deprecated: is no longer needed"""
        pass

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
            cls.cprint(str(message), cls.theme_color["FAIL"], text)
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
            Console.cprint(str(message), "FAIL", text)
        else:
            Console.msg(text + str(message))

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
            Console.cprint(message, "RED", "DEBUG: ")
        else:
            Console.msg("DEBUG: " + message)

    @staticmethod
    def info(message):
        """prints an informational message

        Args:
            message: the message

        Returns:

        """
        message = message or ""
        if Console.color:
            RichConsole.print(f"INFO: {message}", style=Console.theme_color["BLUE"])
        else:
            Console.msg("INFO: " + message)

    @staticmethod
    def warning(message):
        """prints a warning

        Args:
            message: the message

        Returns:

        """
        message = message or ""
        if Console.color:
            Console.cprint(message, Console.theme_color["WARNING"], "WARNING: ")
        else:
            Console.msg("WARNING: " + message)

    @staticmethod
    def ok(message):
        """prints an ok message

        Args:
            message: the message

        Returns:

        """
        message = message or ""
        if Console.color:
            Console.cprint(message, Console.theme_color["OKGREEN"], "")
        else:
            Console.msg(message)

    @staticmethod
    def cprint(message, color="BLUE", prefix=""):
        """prints a message in a given color

        Args:
            color: the color as defined in the theme
            prefix: the prefix (a string)
            message: the message

        Returns:

        """
        message = message or ""
        prefix = prefix or ""
        #RichConsole.print(prefix + message, style=color.lower())

        # print(
            # Console.theme_color[color] + prefix + message + Console.theme_color["ENDC"]
        # )
        if isinstance(message, Text):
            RichConsole.print(prefix, message, sep="")
        else:
            RichConsole.print(prefix + message, style=color)

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
        return Text(prefix + message, style=color.lower())
        # return Console.theme[color] + prefix + message + Console.theme["ENDC"]
    
    @staticmethod
    def background(msg, background_color="white", text_color="black"):
        """prints a message in a given background color

        Args:
            msg: the message
            background_color: the background color
            text_color: the text color

        Returns:

        """
        RichConsole.print(msg, style=f"{text_color} on {background_color}")


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

    Console.red("some red text")

    Console.background("and with a green background", background_color="green")
    RichConsole.print("and in dim text", style="dim")

    Console.msg("back to normal now")
    Console.line()
