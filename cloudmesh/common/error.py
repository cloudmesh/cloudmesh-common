import sys
import traceback


class Error(object):
    @classmethod
    def msg(cls, error=None, debug=True, trace=True):
        if debug and error is not None:
            print(error)
        if trace:
            print(traceback.format_exc())

    @classmethod
    def traceback(cls, error=None, debug=True, trace=True):
        Error.msg(error=error, debug=debug, trace=trace)

    @classmethod
    def info(cls, msg):
        # TODO: if info:
        print(msg)

    @classmethod
    def warning(cls, msg):
        # TODO: if warning:
        print(msg)

    @classmethod
    def debug(cls, msg):
        # TODO: if debug:
        print(msg)

    @classmethod
    def exit(cls, msg):
        # TODO: if debug:
        print(msg)
        sys.exit()
