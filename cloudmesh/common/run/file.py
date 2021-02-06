import os

from cloudmesh.common.util import readfile


def run(command):
    """
    run the command, redirect the outout to a file and display the content once
    it is completed.

    :param command:
    :return:
    """
    os.system(f"{command} &> ./cmd-output")
    content = readfile("./cmd-output")
    return content
