###############################################################
# pip install .; pytest -v --capture=no  tests/test_verbose.py:Test_verbose.test_001
# pytest -v --capture=no  tests/test_verbose.py
# pytest -v tests/test_verbose.py
###############################################################

from pprint import pprint

from cloudmesh.common.util import HEADING
from cloudmesh.DEBUG import VERBOSE
import io
from contextlib import redirect_stdout
import pytest


@pytest.mark.incremental
class Test_Verbose:


    
    def test_001_VERBOSE(self):
        HEADING()

        help = "hallo"
        with io.StringIO() as buf, redirect_stdout(buf):
            VERBOSE(help)
            output = buf.getvalue()
        print (output)

        assert "help" in output
        assert "hallo" in output
        assert "#" in output
        
