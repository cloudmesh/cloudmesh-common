import platform
import sys
import os
from pathlib import Path
from cloudmesh.common.util import readfile
from collections import OrderedDict
import pip
import psutil
import humanize
import re
import multiprocessing

def sys_user():
    if "COLAB_GPU" in os.environ:
        return "collab"
    try:
        if sys.platform == "win32":
            return os.environ["USERNAME"]
    except:
        pass
    try:
        return os.environ["USER"]
    except:
        pass
    try:
        if os.environ["HOME"] == "/root":
            return "root"
    except:
        pass

    return "None"

def get_platform():
    if sys.platform == "darwin":
        return "macos"
    elif sys.platform == "win32":
        return "windows"
    try:
        content = readfile('/etc/os-release')
        if sys.platform == 'linux' and "raspbian" in content:
            return "raspberry"
        else:
            return sys.platform
    except:
        return sys.platform


def systeminfo(info=None, user=None, node=None):
    uname = platform.uname()
    mem = psutil.virtual_memory()

    # noinspection PyPep8
    def add_binary(value):
        try:
            r = humanize.naturalsize(value, binary=True)
        except:
            r = ""
        return r

    try:
        frequency = psutil.cpu_freq()
    except:
        frequency = None

    try:
        cores = psutil.cpu_count(logical=False)
    except:
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
    except:
        pass


    data = OrderedDict({
        'cpu': description.strip(),
        'cpu_count': multiprocessing.cpu_count(),
        'cpu_threads': multiprocessing.cpu_count(),
        'cpu_cores': cores,
        'uname.system': uname.system,
        'uname.node': uname.node,
        'uname.release': uname.release,
        'uname.version': uname.version,
        'uname.machine': uname.machine,
        'uname.processor': uname.processor,
        'sys.platform': sys.platform,
        'python': sys.version,
        'python.version': sys.version.split(" ", 1)[0],
        'python.pip': pip.__version__,
        'user': sys_user(),
        'mem.percent': str(mem.percent) + " %",
        'frequency': frequency
    })
    for attribute in ["total",
                      "available",
                      "used",
                      "free",
                      "active",
                      "inactive",
                      "wired"
                      ]:
        try:
            data[f"mem.{attribute}"] = \
                humanize.naturalsize(getattr(mem, attribute), binary=True)
        except:
            pass
    # svmem(total=17179869184, available=6552825856, percent=61.9,

    if data['sys.platform'] == 'darwin':
        data['platform.version'] = platform.mac_ver()[0]
    elif data['sys.platform'] == 'win32':
        data['platform.version'] = platform.win32_ver()
    else:
        data['platform.version'] = uname.version

    try:
        release_files = Path("/etc").glob("*release")
        for filename in release_files:
            content = readfile(filename.resolve()).splitlines()
            for line in content:
                if "=" in line:
                    attribute, value = line.split("=", 1)
                    attribute = attribute.replace(" ", "")
                    data[attribute] = value
    except:
        pass
    if info is not None:
        data.update(info)
    if user is not None:
        data["user"] = user
    if node is not None:
        data["uname.node"] = node
    return dict(data)
