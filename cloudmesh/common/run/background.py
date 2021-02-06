import subprocess


class run(object):
    """
    A class to simply execute a comman.

    Example:

        command = run("sleep 100")
        command.execute()

        ...

        command.kill()

    """

    def __init__(self, command):
        """
        Initialize the command so it can later on be executed

        :param command:
        """
        self.command = command
        self.pid = None

    def execute(self):
        """
        Execute the command

        :return:
        """
        self.proc = subprocess.Popen(self.command)
        self.pid = self.proc.pid

    def kill(self):
        """
        Kill the command

        :return:
        """
        if self.proc.poll() is None:
            print("Killing: ", self.command)
            print("Pid", self.pid)
            subprocess.Popen(['kill', f"{self.pid}"])
