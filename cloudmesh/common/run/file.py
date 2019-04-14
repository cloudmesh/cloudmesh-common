import subprocess
import os

from cloudmesh.common.util import readfile


def run (command):
    os.system (f"{command} &> ./cmd-output")
    content = readfile("./cmd-output")
    return content
