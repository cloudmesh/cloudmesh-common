"""
common namespace.
"""
import pkg_resources

pkg_resources.declare_namespace(__name__)

import os
import shutil
from cloudmesh.common.util import path_expand
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell
