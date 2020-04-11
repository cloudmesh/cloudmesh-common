"""
class that specifies where we read the cloudmesh.yaml file from
"""
import os

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from pathlib import Path
from cloudmesh.common.console import Console

#
# New Code
#

class Location:
    _shared_state = None

    def __init__(self, directory="~/.cloudmesh"):
        if not Location._shared_state:
            self.key = "CLOUDMESH_CONFIG_DIR"

            Location._shared_state = self.__dict__
            directory = path_expand(directory)
            self.directory = os.environ.get(self.key) or directory
        else:
            self.__dict__ = Location._shared_state

    def get(self):
        return self.directory

    def directory(self):
        return self.directory

    def set(self, directory):
        self.directory = path_expand(directory)

    def config(self):
        p = Path(self.directory) / "cloudmesh.yaml"
        return p

    def environment(self, key):
        if key in os.environ:
            value = os.environ[key]
            self.set(value)
        else:
            Console.error(f"Config location: could not find {key}")
            return None

    def __str__(self):
        return self.directory

    def __eq__(self, other):
        return self.directory == other

#
# OLD CODE kept for compatibility
#
__config_dir_prefix__ = os.path.join("~", ".cloudmesh")

__config_dir__ = Location.directory()


def config_file(filename):
    """
    The location of the config file: ~/.cloudmesh/filename. ~ will be expanded
    :param filename: the filename
    """
    return os.path.join(__config_dir__, filename)


def config_file_raw(filename):
    """
    The location of the config file: ~/.cloudmesh/filename. ~ will NOT be
    expanded

    :param filename: the filename
    """
    return os.path.join(__config_dir_prefix__, filename)


def config_file_prefix():
    """
    The prefix of the configuration file location
    """
    return __config_dir_prefix__


def config_dir_setup(filename):
    """
    sets the config file and makes sure the directory exists if it has not yet
    been created.

    :param filename:
    :return: 
    """
    path = os.path.dirname(filename)
    if not os.path.isdir(path):
        Shell.mkdir(path)

