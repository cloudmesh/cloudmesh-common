import platform
import sys
import os
from pathlib import Path
from cloudmesh.common.util import readfile

def systeminfo():
    data = {
        'machine': platform.machine(),
        'version': platform.version(),
        'platform': platform.platform(),
        'system': platform.system(),
        'processors': platform.system(),
        'sys': sys.platform,
        'mac_version': "",
        'win_version': ""
    }
    try:
        data['node'] = platform.uname().node,
    except:
        pass
    try:
        data['release'] = platform.uname().release,
    except:
        pass
    try:
        data['machine'] = platform.uname().machine,
    except:
        pass
    try:
        data['processor'] = platform.uname().processor,
    except:
        pass

    try:
        data['user']= os.environ['USER']
    except:
        pass
    try:
        data['mac_version'] = platform.mac_ver()[0]
        if data['mac_version'] == ('', '', '', ''):
            data['mac_version'] = ""
    except:
        pass
    try:
        data['win_version'] = platform.win32_ver()
        if data['win_version'] == ('', '', '', ''):
            data['win_version'] = ""
    except:
        pass

    try:
        release_files = Path("/etc").glob("*release")
        for filename in release_files:
            content = readfile(filename).split("\n")
            for line in content:
                if "=" in line:
                    attribute, value = line.split("=", 1)
                    attribute = attribute.replace(" ", "")
                    data[attribute] = value
    except:
        pass


    return dict(data)
