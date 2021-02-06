import subprocess


def run(command, shell=True):
    """
    runs the command and returns the output in utf-8 format

    :param command:
    :param shell:
    :return:
    """
    result = subprocess.check_output(command, shell=shell)
    return result.decode("utf-8")
