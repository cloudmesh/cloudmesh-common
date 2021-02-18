"""
common namespace.
"""
import pkg_resources

pkg_resources.declare_namespace(__name__)

from pprint import pprint
import os
import shutil
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.util import banner
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.FlatDict import FlatDict
from cloudmesh.common.variables import Variables

__version__ = "4.3.45"
