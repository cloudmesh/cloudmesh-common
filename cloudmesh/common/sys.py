import platform
import sys
import os

def info():
    data = {
        'machine': platform.machine(),
        'version': platform.version(),
        'platform': platform.platform(),
        'node': platform.uname().node,
        'release': platform.uname().release,
        'machine': platform.uname().machine,
        'processor': platform.uname().processor,
        'system': platform.system(),
        'processors': platform.system(),
        'sys': sys.platform,
    }
    try:
        data['user']= os.environ['USER']
    except:
        pass
    try:
        data['mac ver'] = platform.mac_ver()
    except:
        pass
    try:
        data['win ver'] = platform.win32_ver()
    except:
        pass


    return dict(data)
