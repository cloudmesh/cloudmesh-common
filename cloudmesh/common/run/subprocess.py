import subprocess

def run(command, shell=True):
    result = subprocess.check_output(command, shell=shell)
    return result.decode("utf-8")

