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

<<<<<<< HEAD
version = '4.3.173'
=======
version = '4.3.176'
>>>>>>> c90c0a1885f61cbc6e9e818f894d4da4a406b818
