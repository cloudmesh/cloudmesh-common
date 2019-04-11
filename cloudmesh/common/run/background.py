import subprocess
import time
import sys


class run(object):

    def __init__(self, command):
        self.command = command
        self.pid = None

    def execute(self):
        self.pid = subprocess.Popen(self.command)

    def kill(self):
        if self.pid.poll() is None:
            print("Killing: ", self.command)
            print("Pid", self.pid)


