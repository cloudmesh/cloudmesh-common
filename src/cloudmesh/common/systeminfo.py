import multiprocessing
import os
import platform
import re
import sys
from collections import OrderedDict
from pathlib import Path

import humanize
import pip
import psutil
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.util import readfile


def os_is_windows():
    """Checks if the os is windows

    Returns:
        bool: True is windows
    """
    return platform.system() == "Windows"


# noinspection PyBroadException
def os_is_linux():
    """Checks if the os is linux

    Returns:
        bool: True is linux
    """
    try:
        content = readfile("/etc/os-release")
        return platform.system() == "Linux" and "raspbian" not in content
    except:  # noqa: E722
        return False


def os_is_mac():
    """Checks if the os is macOS

    Returns:
        bool: True is macOS
    """
    return platform.system() == "Darwin"


# noinspection PyBroadException
def os_is_pi():
    """Checks if the os is Raspberry OS

    Returns:
        bool: True is Raspberry OS
    """
    try:
        content = readfile("/etc/os-release")
        return platform.system() == "Linux" and "raspbian" in content
    except:  # noqa: E722
        return False


def has_window_manager():
    if os_is_mac() or os_is_windows():
        return True
    else:
        return (
            "GNOME_TERMINAL_SCREEN" in os.environ
            or "GNOME_TERMINAL_SERVICE" in os.environ
        )


def sys_user():
    """TODO

    Returns:

    """
    if "COLAB_GPU" in os.environ:
        return "collab"
    try:
        if sys.platform == "win32":
            return os.environ["USERNAME"]
    except:  # noqa: E722
        pass
    try:
        return os.environ["USER"]
    except:  # noqa: E722
        pass
    try:
        if os.environ["HOME"] == "/root":
            return "root"
    except:  # noqa: E722
        pass

    return "None"


def get_platform():
    """TODO

    Returns:

    """
    if sys.platform == "darwin":
        return "macos"
    elif sys.platform == "win32":
        return "windows"
    try:
        content = readfile("/etc/os-release")
        if sys.platform == "linux" and "raspbian" in content:
            return "raspberry"
        else:
            return sys.platform
    except:  # noqa: E722
        return sys.platform


def systeminfo(info=None, user=None, node=None):
    """TODO

    Args:
        info (TODO):  TODO
        user (str): TODO
        node (str): TODO

    Returns: dict of the info

    """
    uname = platform.uname()
    mem = psutil.virtual_memory()

    # noinspection PyPep8
    def add_binary(value):
        try:
            r = humanize.naturalsize(value, binary=True)
        except:  # noqa: E722
            r = ""
        return r

    try:
        frequency = psutil.cpu_freq()
    except:  # noqa: E722
        frequency = None

    try:
        cores = psutil.cpu_count(logical=False)
    except:  # noqa: E722
        cores = "unkown"

    operating_system = get_platform()

    description = ""
    try:
        if operating_system == "macos":
            description = os.popen("sysctl -n machdep.cpu.brand_string").read()
        elif operating_system == "win32":
            description = platform.processor()
        elif operating_system == "linux":
            lines = readfile("/proc/cpuinfo").strip().splitlines()
            for line in lines:
                if "model name" in line:
                    description = re.sub(".*model name.*:", "", line, 1)
    except:  # noqa: E722
        pass

    data = OrderedDict(
        {
            "cpu": description.strip(),
            "cpu_count": multiprocessing.cpu_count(),
            "cpu_threads": multiprocessing.cpu_count(),
            "cpu_cores": cores,
            "uname.system": uname.system,
            "uname.node": uname.node,
            "uname.release": uname.release,
            "uname.version": uname.version,
            "uname.machine": uname.machine,
            "uname.processor": uname.processor,
            "sys.platform": sys.platform,
            "python": sys.version,
            "python.version": sys.version.split(" ", 1)[0],
            "python.pip": pip.__version__,
            "user": sys_user(),
            "mem.percent": str(mem.percent) + " %",
            "frequency": frequency,
        }
    )
    for attribute in [
        "total",
        "available",
        "used",
        "free",
        "active",
        "inactive",
        "wired",
    ]:
        try:
            data[f"mem.{attribute}"] = humanize.naturalsize(
                getattr(mem, attribute), binary=True
            )
        except:  # noqa: E722
            pass
    # svmem(total=17179869184, available=6552825856, percent=61.9,

    if data["sys.platform"] == "darwin":
        data["platform.version"] = platform.mac_ver()[0]
    elif data["sys.platform"] == "win32":
        data["platform.version"] = platform.win32_ver()
    else:
        data["platform.version"] = uname.version

    try:
        release_files = Path("/etc").glob("*release")
        for filename in release_files:
            content = readfile(filename.resolve()).splitlines()
            for line in content:
                if "=" in line:
                    attribute, value = line.split("=", 1)
                    attribute = attribute.replace(" ", "")
                    data[attribute] = value
    except:  # noqa: E722
        pass
    if info is not None:
        data.update(info)
    if user is not None:
        data["user"] = user
    if node is not None:
        data["uname.node"] = node
    data["date"] = str(DateTime.now())
    return dict(data)
