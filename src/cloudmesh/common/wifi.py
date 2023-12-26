"""Implementation of a function the set the WIFI configuration.
This function is primarily developed for a Raspberry PI
"""
import textwrap

from cloudmesh.common.console import Console
from cloudmesh.common.sudo import Sudo
from cloudmesh.common.util import writefile


class Wifi:
    """The class is used to group a number of useful variables and functions so
    it is easier to program and manage Wifi configurations.

    The default location for the configuration file is

    /etc/wpa_supplicant/wpa_supplicant.conf

    """

    location = "/etc/wpa_supplicant/wpa_supplicant.conf"

    template_key = textwrap.dedent(
        """
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country={country}

        network={{
                ssid="{ssid}"
                key_mgmt=NONE
        }}
    """
    )

    template_psk = textwrap.dedent(
        """
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country=US

        network={{
                ssid="{ssid}"
                psk="{password}"
                key_mgmt=WPA-PSK
        }}
    """
    )  # noqa: W293

    template = template_psk

    @staticmethod
    def set(
        ssid=None, password=None, country="US", psk=True, location=location, sudo=False
    ):
        """Sets the wifi. Only works for psk based wifi

        Args:
            ssid (str): The ssid
            password (str): The password
            country (str): Two digit country code
            psk (bool): If true uses psk authentication
            location (str): The file where the configuration file should
                be written to
            sudo (bool): If tru the write will be done with sudo

        Returns:
            bool: True if success
        """

        if ssid is None or (psk and password is None):
            Console.error("SSID or password not set")
            return False

        if psk:
            config = Wifi.template.format(**locals())
        else:
            config = Wifi.template_key.format(**locals())
        try:
            if sudo:
                Sudo.writefile(location, config)
            else:
                writefile(location, config)

        except FileNotFoundError as e:  # noqa: F841
            Console.error(f"The file does not exist: {location}")
            return False
        return True
