import subprocess

def run(command, shell=True):
    """
    Run the specified command and return the output in UTF-8 format.

    Args:
        command (str): The command to be executed.
        shell (bool, optional): If True, execute the command through the shell.

    Returns:
        str: The UTF-8 decoded output of the command.
    """
    result = subprocess.check_output(command, shell=shell)
    return result.decode("utf-8")
