import os
from cloudmesh.common.util import readfile

def run(command):
    """
    Run the specified command, redirect the output to a file,
    and return the content once it is completed.

    Args:
        command (str): The command to be executed.

    Returns:
        str: The content of the command's output.
    """
    os.system(f"{command} &> ./cmd-output")
    content = readfile("./cmd-output")
    return content
