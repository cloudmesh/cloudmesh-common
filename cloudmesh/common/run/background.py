import subprocess
import time
import sys


class run(object):

    def __init__(self, command):
        self.command = command
        self.pid = None

    def execute(self):
        self.proc = subprocess.Popen(self.command)
        self.pid = self.proc.pid

    def kill(self):
        if self.proc.poll() is None:
            print("Killing: ", self.command)
            print("Pid", self.pid)
            subprocess.Popen(['kill', f"{self.pid}"])
