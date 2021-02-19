import os
import subprocess
import sys
from cloudmesh.common.util import banner
from cloudmesh.common.util import writefile
from cloudmesh.common.util import path_expand

from cloudmesh.common.console import Console

class Sudo:

    @staticmethod
    def password(msg="sudo password: "):
        """
        Asks for the Sudo password
        """
        os.system(f'sudo -p "{msg}"  echo ""')

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
        return result

    @staticmethod
    def readfile(filename, split=False, trim=False, decode=True):
        """
        Reads the content of the file as sudo and returns the result

        :param filename: the filename
        :type filename: str
        :param split: uf true returns a list of lines
        :type split: bool
        :param trim: trim trailing whitespace. This is useful to
                     prevent empty string entries when splitting by '\n'
        :type trim: bool
        :return: the content
        :rtype: str or list
        """
        os.system("sync")
        result = Sudo.execute(f"cat {filename}", decode=decode)

        content = result.stdout

        if trim:
            content = content.rstrip()

        if split:
            content = content.splitlines()

        return content

    @staticmethod
    def writefile(filename, content, append=False):
        """
        Writes the content in the the given file.

        :param filename: the filename
        :type filename: str
        :param content: the content
        :type content: str
        :param append: if true it append it at the end, otherwise the file will
                       be overwritten
        :type append: bool
        :return: the output created by the write process
        :rtype: int
        """

        os.system("sync")
        tmp_dir = path_expand("~/.cloudmesh/tmp")
        os.system(f'mkdir -p {tmp_dir}')
        tmp = path_expand("~/.cloudmesh/tmp/tmp.txt")

        if append:
            content = Sudo.readfile(filename, split=False, decode=True) + content

        writefile(tmp, content)

        os.system("sync")
        result = Sudo.execute(f"sudo cp {tmp} {filename}")
        os.system("sync")

        # If exit code is not 0
        if result.returncode != 0:
            Console.warning(f"{filename} was not created correctly -> {result.stderr}")

        try:
            os.remove(tmp)
        except:
            Console.warning(f"{tmp} was not removed correctly.")

        return content
