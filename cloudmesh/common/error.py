"""
A simple framework to handle error messages
"""
import sys
import traceback
from cloudmesh.common.console import Console


#
# TODO: this class seems to replicate some portions of what Console does
#
class Error(object):
    """
    A class to print error messages
    """

    #
    # TODO: this should probably use Console so we can print in color
    #
    @classmethod
    def msg(cls, error=None, debug=True, trace=True):
        """
        prints the error message

        :param error: the error message
        :param debug: only prints it if debug is set to true
        :param trace: if true prints the trace
        :return:
        """
        if debug and error is not None:
            print(error)
        if debug and trace:
            print(traceback.format_exc())

    @classmethod
    def traceback(cls, error=None, debug=True, trace=True):
        """
        prints the trace

        :param error: a message preceding the trace
        :param debug: prints it if debug is set to true
        :param trace:
        :return:
        """
        if debug and trace:
            Error.msg(error=error, debug=debug, trace=trace)

    @classmethod
    def info(cls, msg, debug=True):
        """
        prints an info msg.

        :param msg: the message
        :return:
        """
        if debug:
            Console.info(msg)

    @classmethod
    def warning(cls, msg, debug=True):
        """
        prints a warning message.

        :param msg:
        :return:
        """
        if debug:
            Console.warning(msg)

    @classmethod
    def debug(cls, msg, debug=True):
        """
        prints a debug message.

        :param msg: the message
        :return:
        """
        if debug:
            Console.msg(msg)

    @classmethod
    def exit(cls, msg):
        """
        call a system exit

        :param msg:
        :return:
        """
        Console.error(msg)
        sys.exit()
