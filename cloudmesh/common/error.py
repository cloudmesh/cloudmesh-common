"""
A simple framework to handle error messages 
"""
import sys
import traceback


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
        # TODO: BUG: trace should only be printed if debug is true
        if trace:
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
        # TODO: if debug:
        Error.msg(error=error, debug=debug, trace=trace)

    @classmethod
    def info(cls, msg):
        """
        prints an info msg. 
        :param msg: the message
        :return: 
        """
        # TODO: if info:
        print(msg)

    @classmethod
    def warning(cls, msg):
        """
        prints a warning message. 
        :param msg: 
        :return: 
        """
        # TODO: if warning:
        print(msg)

    @classmethod
    def debug(cls, msg):
        """
        prints a debug message.
        :param msg: the message
        :return: 
        """
        # TODO: if debug:
        print(msg)

    @classmethod
    def exit(cls, msg):
        """
        call a system exit
        :param msg: 
        :return: 
        """
        # TODO: if debug:
        print(msg)
        sys.exit()

        # TODO: adding methods for setting and getting info and debug are missing
