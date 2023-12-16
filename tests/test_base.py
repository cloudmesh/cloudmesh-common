###############################################################
# pytest -v --capture=no tests/test_base.py
# pytest -v  tests/test_base.py
###############################################################


import os
import shutil

import pytest
from cloudmesh.common.base import Base
from cloudmesh.common.util import HEADING

cwd = os.getcwd()


@pytest.mark.incremental
class Test_Base:
    def test_default_path_in_home(self):
        HEADING()
        cloudmesh = Base()
        expected_path = os.path.expanduser("~/.cloudmesh")
        assert cloudmesh.path == expected_path
        assert cloudmesh.config == f"{expected_path}/cloudmesh.yaml"

    def test_custom_path(self):
        HEADING()
        custom_path = "./tmp/.cloudmesh"
        cloudmesh = Base(path=custom_path)
        assert cloudmesh.path == custom_path
        assert cloudmesh.config == f"{custom_path}/cloudmesh.yaml"
        shutil.rmtree("./tmp")

    def test_environment_variable_path(self):
        HEADING()
        os.environ["CLOUDMESH_CONFIG_DIR"] = "./tmp/.cloudmesh"
        cloudmesh = Base()
        assert cloudmesh.path == "./tmp/.cloudmesh"
        assert cloudmesh.config == f"{cloudmesh.path}/cloudmesh.yaml"
        shutil.rmtree("./tmp")
        del os.environ["CLOUDMESH_CONFIG_DIR"]

    def test_cloudmesh_in_cwd(self):
        HEADING()
        tmp_path = "/tmp/test"
        os.makedirs(f"{tmp_path}/.cloudmesh", exist_ok=True)
        os.chdir(tmp_path)
        print("CWD", os.getcwd())
        print(os.listdir())

        cloudmesh = Base()
        print(cloudmesh.path)
        assert cloudmesh.path == ".cloudmesh"
        assert cloudmesh.config == ".cloudmesh/cloudmesh.yaml"
        os.chdir(cwd)
        shutil.rmtree("/tmp/test")
