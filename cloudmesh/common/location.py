"""
class that specifies where we read the cloudmesh.yaml file from
"""
import os

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.common.util import readfile
from pathlib import Path
from cloudmesh.common.console import Console


class Location:
    _shared_state = None

    def __init__(self, directory="~/.cloudmesh"):
        if not Location._shared_state:
            self.key = "CLOUDMESH_CONFIG_DIR"

            Location._shared_state = self.__dict__
            directory = path_expand(directory)
            self.directory = os.environ.get(self.key) or directory
            if not os.path.isdir(directory):
                Shell.mkdir(directory)
        else:
            self.__dict__ = Location._shared_state

    def write(self, filename, content):
        """
        Write a file to the configuration directory

        :param filename: The filename
        :param content:  The content
        :return:
        """
        path = Path(self.directory) / filename
        directory = os.path.dirname(path)
        Shell.mkdir(directory)
        writefile(filename, content)

    def read(self, filename):
        """
        Read a file from the configuration directory

        :param filename: The filename
        :return: The content
        """
        return readfile(filename)

    def file(self, filename):
        """
        The location of the config file in the cloudmesh configuration directory

        :param filename: the filenam
        """
        return Path(self.directory) / filename

    def get(self):
        return self.directory

    def set(self, directory):
        self.directory = path_expand(directory)

    def config(self):
        return self.file("cloudmesh.yaml")

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
