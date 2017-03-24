"""
Class for starting and stopping named timers.

This class is based on a similar java class in cyberaide, and java cog kit.

"""

import time


class StopWatch(object):

    """
    A class to measure times between events.
    """

    # Timer start dict
    timer_start = {}
    # Timer end dict
    timer_end = {}

    @classmethod
    def keys(cls):
        """returns the names of the timers"""
        return list(cls.timer_end.keys())

    @classmethod
    def start(cls, name):
        """
        starts a timer with the given name.

        :param name: the name of the timer
        :type name: string
        """
        cls.timer_start[name] = time.time()

    @classmethod
    def stop(cls, name):
        """
        stops the timer with a given name.

        :param name: the name of the timer
        :type name: string
        """
        cls.timer_end[name] = time.time()

    @classmethod
    def get(cls, name):
        """
        returns the time of the timer.

        :param name: the name of the timer
        :type name: string
        :rtype: the elapsed time
        """
        time_elapsed = cls.timer_end[name] - \
            cls.timer_start[name]
        return time_elapsed

    @classmethod
    def clear(cls):
        """
        clear start and end timer_start
        """
        cls.timer_start.clear()
        cls.timer_end.clear()
