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


def create_cloudmesh_yaml(filename):
    if not os.path.exists(filename):
        path = os.path.dirname(filename)
        if not os.path.isdir(path):
            Shell.mkdir(path)
        etc_path = os.path.dirname(os.path.dirname(__file__))
        etc_file = os.path.join(etc_path, "etc", "cloudmesh.yaml")
        to_dir = path_expand("~/.cloudmesh")
        shutil.copy(etc_file, to_dir)
        os.system("chmod -R go-rwx " + path_expand("~/.cloudmesh"))
        Console.ok("~/.cloudmesh/cloudmesh.yaml created")


def setup_yaml():
    filename = path_expand("~/.cloudmesh/cloudmesh.yaml")
    create_cloudmesh_yaml(filename)


setup_yaml()
