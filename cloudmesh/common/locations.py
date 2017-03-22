import os

from cloudmesh_client.common.Shell import Shell
from cloudmesh_client.common.util import path_expand

__config_dir_prefix__ = os.path.join("~", ".cloudmesh")

__config_dir__ = path_expand(__config_dir_prefix__)


def config_file(filename):
    """
    The location of the config file: ~/.cloudmesh/filename. ~ will be expanded
    :param filename: the filename
    """
    return os.path.join(__config_dir__, filename)


def config_file_raw(filename):
    """
    The location of the config file: ~/.cloudmesh/filename. ~ will NOT be expanded
    :param filename: the filename
    """
    return os.path.join(__config_dir_prefix__, filename)


def config_file_prefix():
    """
    The prefix of the configuration file location
    """
    return __config_dir_prefix__


def config_dir_setup(filename):
    path = os.path.dirname(filename)
    if not os.path.isdir(path):
        Shell.mkdir(path)

