###############################################################
# pip install .; pytest -v --capture=no  tests/test_verbose.py:Test_verbose.test_001
# pytest -v --capture=no  tests/test_verbose.py
# pytest -v tests/test_verbose.py
###############################################################

from cloudmesh.common.util import HEADING
from cloudmesh.common.debug import VERBOSE
import io
import pytest
from contextlib import redirect_stdout



@pytest.mark.incremental
class Test_Verbose:

    def test_VERBOSE(self):
        HEADING()

        help = "hallo"
        with io.StringIO() as buf, redirect_stdout(buf):
            VERBOSE(help)
            output = buf.getvalue()
        print (output)

        assert "help" in output
        assert "hallo" in output
        assert "#" in output
        
