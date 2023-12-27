import os
import subprocess

from cloudmesh.common.util import banner


class Sudo:
    """
     A utility class for executing commands with sudo privileges and performing file operations.

    Methods:
        password(msg="sudo password: "):
            Prompt the user for the sudo password.

        execute(command, decode=True, debug=False, msg=None):
            Execute the specified command with sudo.
            Args:
                command (list or str): The command to run.
                decode (bool, optional): If True, decode the output from bytes to ASCII.
                debug (bool, optional): If True, print command execution details.
                msg (str, optional): Message to print before executing the command.
            Returns:
                subprocess.CompletedProcess: The result of the command execution.

        readfile(filename, split=False, trim=False, decode=True):
            Read the content of the file with sudo privileges and return the result.
            Args:
                filename (str): The filename.
                split (bool, optional): If True, return a list of lines.
                trim (bool, optional): If True, trim trailing whitespace.
                decode (bool, optional): If True, decode the output from bytes to ASCII.
            Returns:
                str or list: The content of the file.

        writefile(filename, content, append=False):
            Write the content to the specified file with sudo privileges.
            Args:
                filename (str): The filename.
                content (str): The content to write.
                append (bool, optional): If True, append the content at the end;
                                         otherwise, overwrite the file.
            Returns:
                str: The output created by the write process.
    """

    @staticmethod
    def password(msg="sudo password: "):
        """Prompt the user for the sudo password.

        Args:
            msg (str, optional): The message to display when prompting for the password.
        """
        os.system(f'sudo -p "{msg}"  echo "" > /dev/null')

    @staticmethod
    def expire():
        """Expires the password"""
        os.system("sudo -k")

    @staticmethod
    def execute(command, decode="True", debug=False, msg=None):
        """Execute the specified command with sudo.

        Args:
            command (list or str): The command to run.
            decode (bool, optional): If True, decode the output from bytes to ASCII.
            debug (bool, optional): If True, print command execution details.
            msg (str, optional): Message to print before executing the command.

        Returns:
            subprocess.CompletedProcess: The result of the command execution.
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
            result.stdout = result.stdout.decode("ascii")
            result.stderr = result.stderr.decode("ascii")

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
        """Read the content of the file with sudo privileges and return the result.

        Args:
            filename (str): The filename.
            split (bool, optional): If True, return a list of lines.
            trim (bool, optional): If True, trim trailing whitespace.
            decode (bool, optional): If True, decode the output from bytes to ASCII.

        Returns:
            str or list: The content of the file.
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
        """Write the content to the specified file with sudo privileges.

        Args:
            filename (str): The filename.
            content (str): The content to write.
            append (bool, optional): If True, append the content at the end; otherwise, overwrite the file.

        Returns:
            str: The output created by the write process.
        """

        os.system("sync")
        Sudo.password()
        if append:
            content = Sudo.readfile(filename, split=False, decode=True) + content

        os.system(f"echo '{content}' | sudo cp /dev/stdin {filename}")
        os.system("sync")

        return content
