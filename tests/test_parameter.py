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
    def test_string_expand_none(self):
        HEADING()

        parameter = "a"
        check = ["a"]

        result = Parameter.expand_string(parameter)
        print(result)

        assert result == check

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

    def test_string_expand_comma_no_postfix(self):
        HEADING()

        parameter = "prefix-[a,b,c]"
        check = ["prefix-a", "prefix-b", "prefix-c"]

        result = Parameter.expand_string(parameter)
        print(result)

        assert result == check

    def test_string_expand_comma_no_prefix(self):
        HEADING()

        parameter = "[a,b,c]-postfix"
        check = ["a-postfix", "b-postfix", "c-postfix"]

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

    def test_string_expand_mix(self):
        HEADING()

        parameter = "x[a,b-d,g,x-z]"
        check = ["xa", "xb", "xc", "xd", "xg", "xx", "xy", "xz"]

        result = Parameter.expand_string(parameter)
        print(result)

        assert result == check

    def test_mixed_hosts(self):
        HEADING()

        parameter = "red[01-02],red"

        check = ["red01", "red02", "red"]

        result = Parameter.expand(parameter)
        print(result)

        assert result == check
