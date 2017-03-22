from __future__ import print_function

import traceback
import textwrap

from colorama import Fore, Back, Style
import colorama

colorama.init()


def indent(text, indent=2, width=128):
    return "\n".join(
        textwrap.wrap(text,
                      width=width,
                      initial_indent=" " * indent,
                      subsequent_indent=" " * indent))


class Console(object):
    """
    A simple way to print in a console terminal in color. Instead of using
    simply the print statement you can use special methods to indicate
    warnings, errors, ok and regular messages.

    Example Usage::

        Console.warning("Warning")
        Console.error("Error")
        Console.info("Info")
        Console.msg("msg")
        Console.ok("Success")

    One can swith the color mode off with::

        Console.color = False
        Console.error("Error")

    The color will be switched on by default.
    """

    color = True
    debug = True

    theme_color = {
        'HEADER': Fore.MAGENTA,
        'BLACK': Fore.BLACK,
        'CYAN': Fore.CYAN,
        'WHITE': Fore.WHITE,
        'BLUE': Fore.BLUE,
        'OKBLUE': Fore.BLUE,
        'OKGREEN': Fore.GREEN,
        'GREEN': Fore.GREEN,
        'FAIL': Fore.RED,
        'WARNING': Fore.MAGENTA,
        'RED': Fore.RED,
        'ENDC': '\033[0m',
        'BOLD': "\033[1m",
    }

    theme_bw = {
        'HEADER': '',
        'BLACK': '',
        'CYAN': '',
        'WHITE': '',
        'BLUE': '',
        'OKBLUE': '',
        'OKGREEN': '',
        'GREEN': '',
        'FAIL': '',
        'WARNING': '',
        'RED': '',
        'ENDC': '',
        'BOLD': "",
    }

    theme = theme_color

    @classmethod
    def set_debug(cls, on=True):
        cls.debug = on

    @staticmethod
    def set_theme(color=True):
        if color:
            Console.theme = Console.theme_color
        else:
            Console.theme = Console.theme_bw
        Console.color = color

    @staticmethod
    def get(name):
        if name in Console.theme:
            return Console.theme[name]
        else:
            return Console.theme['BLACK']

    @staticmethod
    def msg(message, width=90):
        return textwrap.fill(message, width=width)

    @staticmethod
    def msg(message):
        message = message or ""
        print(message)

    @classmethod
    def error(cls, message, prefix=True, traceflag=True):
        message = message or ""
        if prefix:
            text = "ERROR: "
        else:
            text = ""
        if cls.color:
            cls.cprint('FAIL', text, str(message))
        else:
            print(cls.msg(text + str(message)))

        if traceflag and cls.debug:
            trace = traceback.format_exc().strip()
            print
            print("\n".join(str(trace).splitlines()))
            print

    @staticmethod
    def TODO(message, prefix=True, traceflag=True):
        message = message or ""
        if prefix:
            text = "TODO: "
        else:
            text = ""
        if Console.color:
            Console.cprint('FAIL', text, str(message))
        else:
            print(Console.msg(text + str(message)))

        trace = traceback.format_exc().strip()

        if traceflag and trace != "None":
            print
            print("\n".join(str(trace).splitlines()))
            print

    @staticmethod
    def debug_msg(message):
        message = message or ""
        if Console.color:
            Console.cprint('RED', 'DEBUG: ', message)
        else:
            print(Console.msg('DEBUG: ' + message))


    @staticmethod
    def info(message):
        message = message or ""
        if Console.color:
            Console.cprint('OKBLUE', "INFO: ", message)
        else:
            print(Console.msg("INFO: " + message))

    @staticmethod
    def warning(message):
        message = message or ""
        if Console.color:
            Console.cprint('WARNING', "WARNING: ", message)
        else:
            print(Console.msg("WARNING: " + message))

    @staticmethod
    def ok(message):
        message = message or ""
        if Console.color:
            Console.cprint('OKGREEN', "", message)
        else:
            print(Console.msg(message))

    @staticmethod
    def cprint(color, prefix, message):
        message = message or ""
        prefix = prefix or ""
        print((Console.theme[color] +
               prefix +
               message +
               Console.theme['ENDC']))



#
# Example
#


if __name__ == "__main__":
    print(Console.color)

    print(Console.theme)

    Console.warning("Warning")
    Console.error("Error")
    Console.info("Info")
    Console.msg("msg")
    Console.ok("Ok")

    Console.color = False
    print(Console.color)
    Console.error("Error")

    print(Fore.RED + 'some red text')
    print(Back.GREEN + 'and with a green background')
    print(Style.DIM + 'and in dim text')
    print(Fore.RESET + Back.RESET + Style.RESET_ALL)
    print('back to normal now')
