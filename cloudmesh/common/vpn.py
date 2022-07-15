from cloudmesh.common.Shell import Shell
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.systeminfo import os_is_linux

class Vpn:

    @staticmethod
    @property
    def enabled():
        state = False
        if os_is_windows():
            result = Shell.run("route print").strip()
            state = "Cisco AnyConnect" in result
        elif os_is_mac():
            raise NotImplementedError
        elif os_is_linux():
            result = Shell.ps()
            state = "/usr/sbin/openconnect --servercert pin-sha256:" in result
        return state

    @staticmethod
    @property
    def is_uva(self):
        state = False
        if os_is_windows():
            raise NotImplementedError
        elif os_is_mac():
            raise NotImplementedError
        elif os_is_linux():
            result = Shell.run("route").strip()
            state = "uva-anywhere" in result
        return state

    @staticmethod
    def connect(self):
        raise NotImplementedError
