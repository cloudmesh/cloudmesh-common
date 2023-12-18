import subprocess

class RunProcess:
    """
    A class to simplify the execution and termination of subprocess commands.

    Example:

        process = RunProcess("sleep 100")
        process.execute()

        ...

        process.kill()

    Methods:
        __init__(self, command):
            Initialize the command for later execution.

        execute(self):
            Execute the specified command.

        kill(self):
            Kill the running command.

    Attributes:
        command (str): The command to be executed.
        pid (int): The process ID (PID) of the running command.
        proc (subprocess.Popen): The subprocess object representing the running command.
    """

    def __init__(self, command):
        """
        Initialize the RunProcess instance.

        Args:
            command (str): The command to be executed.
        """
        self.command = command
        self.pid = None
        self.proc = None

    def execute(self):
        """
        Execute the specified command.

        Returns:
            None
        """
        self.proc = subprocess.Popen(self.command)
        self.pid = self.proc.pid

    def kill(self):
        """
        Kill the running command.

        Returns:
            None
        """
        if self.proc and self.proc.poll() is None:
            print("Killing:", self.command)
            print("Pid:", self.pid)
            subprocess.Popen(['kill', f"{self.pid}"])
