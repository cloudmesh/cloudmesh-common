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

        result = Parameter.expand(parameter)
        print(result)
        assert result == check

    def test_separate_without_prefix(self):
        HEADING()

        parameter = "a,b,c"
        check = ["a", "b", "c"]

        result = Parameter.expand(parameter)
        print(result)

        assert result == check

    def test_separate_with_one_prefix(self):
        HEADING()

        parameter = "local:a,b,c"
        check = ["local:a", "local:b", "local:c"]

        result = Parameter.expand(parameter)
        print(result)

        assert result == check

    def test_separate_with_all_prefix(self):
        HEADING()

        parameter = "a:a,b:b,c:c"
        check = ["a:a", "b:b", "c:c"]

        result = Parameter.expand(parameter)
        print(result)

        assert result == check

    def test_separate_with_missing_prefix(self):
        HEADING()

        parameter = "local:a,b,local:c"
        check = ["local:a", "b", "local:c"]

        result = Parameter.expand(parameter)
        print(result)

        assert result == check

    def test_separate_with_missing_prefix2(self):
        HEADING()

        parameter = "a,b,local:c"
        check = ["a", "b", "local:c"]

        result = Parameter.expand(parameter)
        print(result)

        assert result == check

    def test_string_expand_comma(self):
        HEADING()

        parameter = "prefix-[a,b,c]-postfix"
        check = ["prefix-a-postfix", "prefix-b-postfix", "prefix-c-postfix"]

        result = Parameter.expand_string(parameter)
        print(result)

        assert result == check

    def test_string_expand_dash(self):
        HEADING()

        parameter = "prefix-[a-c]-postfix"
        check = ["prefix-a-postfix", "prefix-b-postfix", "prefix-c-postfix"]

        result = Parameter.expand_string(parameter)
        print(result)

        assert result == check

    def test_string_expand_comma(self):
        HEADING()

        parameter = "a,b,c"
        check = ["a", "b", "c"]

        result = Parameter.expand_string(parameter)
        print(result)

        assert result == check
