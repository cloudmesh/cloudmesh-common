import os
import subprocess
import sys
from cloudmesh.common.util import banner

class Sudo:

    @staticmethod
    def password():
        """
        Asks for the Sudo password
        """
        os.system('sudo -p "sudo password: "  echo ""')

    @staticmethod
    def expire():
        """
        Expires the password
        """
        os.system("sudo -k")

    @staticmethod
    def execute(command, decode="True", debug=False):
        """
        Executes the command

        :param command: The command to run
        :type command: list or str
        :return:
        :rtype:
        """

        if type(command) == str:
            sudo_command = "sudo " + command
            sudo_command = sudo_command.split(" ")
        else:
            sudo_command = ["sudo"] + command
        print("Executing:", " ".join(sudo_command))
        os.system("sync")
        result = subprocess.run(sudo_command, capture_output=True)
        os.system("sync")
        if decode:
            result.stdout = result.stdout.decode('ascii')
            result.stderr = result.stderr.decode('ascii')

        if debug:
            banner("stdout")
            print(result.stdout)
            banner("stderr")
            print(result.stderr)
            banner("result")
            print(result)
