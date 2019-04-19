import platform


def info():
    data = {
        'machine': platform.machine(),
        'version': platform.version(),
        'platform': platform.platform(),
        'uname': platform.uname(),
        'system': platform.system(),
        'processors': platform.system()
    }
    return data
