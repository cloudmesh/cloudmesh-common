###############################################################
# pytest -v --capture=no tests/test_parameter.py
# pytest -v --capture=no  tests/test_parameter..py::Test_parameter.test_001
# pytest -v  tests/test_parameter.py
###############################################################

import pytest
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import HEADING


@pytest.mark.incremental
class Test_Parameter:

    def test_expand(self):
        HEADING()

        parameter = "a,b,c"
        check = ["a", "b", "c"]

        result = Parameter._expand(parameter)
        print(result)
        assert result == check

    def test_separate_without_prefix(self):
        HEADING()

        parameter = "a,b,c"
        check = ["a", "b", "c"]

        result = Parameter._expand(parameter)
        print(result)

        assert result == check

    def test_separate_with_one_prefix(self):
        HEADING()

        parameter = "local:a,b,c"
        check = ["local:a", "local:b", "local:c"]

        result = Parameter._expand(parameter)
        print(result)

        assert result == check

    def test_separate_with_all_prefix(self):
        HEADING()

        parameter = "a:a,b:b,c:c"
        check = ["a:a", "b:b", "c:c"]

        result = Parameter._expand(parameter)
        print(result)

        assert result == check

    def test_separate_with_missing_prefix(self):
        HEADING()

        parameter = "local:a,b,local:c"
        check = ["local:a", "b", "local:c"]

        result = Parameter._expand(parameter)
        print(result)

        assert result == check

    def test_separate_with_missing_prefix2(self):
        HEADING()

        parameter = "a,b,local:c"
        check = ["a", "b", "local:c"]

        result = Parameter._expand(parameter)
        print(result)

        assert result == check
