"""A simple framework to handle error messages"""
import sys
import traceback

from cloudmesh.common.console import Console


#
# TODO: this class seems to replicate some portions of what Console does
#
class Error(object):
    """A class to print error messages"""

    #
    # TODO: this should probably use Console so we can print in color
    #
    @classmethod
    def msg(cls, error=None, debug=True, trace=True):
        """prints the error message

        Args:
            error: the error message
            debug: only prints it if debug is set to true
            trace: if true prints the trace

        Returns:
            None
        """
        if debug and error is not None:
            print(error)
        if debug and trace:
            print(traceback.format_exc())

    @classmethod
    def traceback(cls, error=None, debug=True, trace=True):
        """prints the trace

        Args:
            error: a message preceding the trace
            debug: prints it if debug is set to true
            trace

        Returns:
            None
        """
        if debug and trace:
            Error.msg(error=error, debug=debug, trace=trace)

    @classmethod
    def info(cls, msg, debug=True):
        """prints an info msg.

        Args:
            msg: the message

        Returns:
            None
        """
        if debug:
            Console.info(msg)

    @classmethod
    def warning(cls, msg, debug=True):
        """prints a warning message.

        Args:
            msg: the message

        Returns:
            None
        """
        if debug:
            Console.warning(msg)

    @classmethod
    def debug(cls, msg, debug=True):
        """prints a debug message.

        Args:
            msg: the message

        Returns:
            None
        """
        if debug:
            Console.msg(msg)

    @classmethod
    def exit(cls, msg):
        """call a system exit

        Args:
            msg: the message

        Returns:
            None
        """
        Console.error(msg)
        sys.exit()
