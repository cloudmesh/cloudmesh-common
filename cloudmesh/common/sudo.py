import os
import subprocess
from cloudmesh.common.util import banner


class Sudo:

    @staticmethod
    def password(msg="sudo password: "):
        """
        Asks for the Sudo password
        """
        os.system(f'sudo -p "{msg}"  echo "" > /dev/null')

    @staticmethod
    def expire():
        """
        Expires the password
        """
        os.system("sudo -k")

    @staticmethod
    def execute(command, decode="True", debug=False, msg=None):
        """
        Executes the command

        :param command: The command to run
        :type command: list or str
        :return:
        :rtype:
        """

        Sudo.password()
        if type(command) == str:
            sudo_command = "sudo " + command
            sudo_command = sudo_command.split(" ")
        else:
            sudo_command = ["sudo"] + command
        if msg is None:
            pass
        elif msg == "command":
            print("Executing:", " ".join(sudo_command))
        else:
            print("Executing:", " ".join(msg))
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
        Sudo.password()
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
        Sudo.password()
        if append:
            content = Sudo.readfile(filename, split=False, decode=True) + content

        os.system(f"echo '{content}' | sudo cp /dev/stdin {filename}")
        os.system("sync")

        return content
