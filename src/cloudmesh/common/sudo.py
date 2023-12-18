import os
import subprocess

from cloudmesh.common.util import banner


class Sudo:

    @staticmethod
    def password(msg="sudo password: "):
        """Asks for the Sudo password"""
        os.system(f'sudo -p "{msg}"  echo "" > /dev/null')

    @staticmethod
    def expire():
        """Expires the password"""
        os.system("sudo -k")

    @staticmethod
    def execute(command, decode="True", debug=False, msg=None):
        """Executes the command

        Args:
            command (list or str): The command to run

        Returns:

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
        """Reads the content of the file as sudo and returns the result

        Args:
            filename (str): the filename
            split (bool): uf true returns a list of lines
            trim (bool): trim trailing whitespace. This is useful to
                prevent empty string entries when splitting by '\n'

        Returns:
            str or list: the content
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
        """Writes the content in the the given file.

        Args:
            filename (str): the filename
            content (str): the content
            append (bool): if true it append it at the end, otherwise
                the file will be overwritten

        Returns:
            int: the output created by the write process
        """

        os.system("sync")
        Sudo.password()
        if append:
            content = Sudo.readfile(filename, split=False, decode=True) + content

        os.system(f"echo '{content}' | sudo cp /dev/stdin {filename}")
        os.system("sync")

        return content
