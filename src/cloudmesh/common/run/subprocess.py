import subprocess


def run(command, shell=True):
    """runs the command and returns the output in utf-8 format

    Args:
        command
        shell

    Returns:

    """
    result = subprocess.check_output(command, shell=shell)
    return result.decode("utf-8")
