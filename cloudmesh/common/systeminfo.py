import platform
import sys
import os
from pathlib import Path
from cloudmesh.common.util import readfile
from collections import OrderedDict
import pip
import psutil
import humanize


def systeminfo():
    uname = platform.uname()
    mem = psutil.virtual_memory()

    def add_binary(value):
        try:
            r = humanize.naturalsize(value, binary=True)
        except:
            r = ""
        return r

    data = OrderedDict({
        'uname.system': uname.system,
        'uname.node': uname.node,
        'uname.release': uname.release,
        'uname.version': uname.version,
        'uname.machine': uname.machine,
        'uname.system': uname.system,
        'uname.processor': uname.processor,
        'sys.platform': sys.platform,
        'python': sys.version,
        'python.version': sys.version.split(" ", 1)[0],
        'python.pip': pip.__version__,
        'user': os.environ['USER'],
        'mem.percent': str(mem.percent) + " %",
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

    return dict(data)
