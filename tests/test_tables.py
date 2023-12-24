###############################################################
# npytest -v --capture=no  tests/test_tables..py::Test_tables.test_001
# pytest -v --capture=no  tests/test_tables.py
# pytest -v tests/test_tables.py
###############################################################

from pprint import pprint

import pytest
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING


@pytest.mark.incremental
class Test_tables:
    """define tests for dict printer so you test
    yaml
    json
    table
    csv
    dict
    printing
    """

    def setup_method(self):
        self.d = [
            {
                "id": "a",
                "x": 1,
                "y": 2,
            },
            {
                "id": "b",
                "x": 3,
                "y": 4,
            },
        ]

    # noinspection PyPep8Naming
    def tearDown(self):
        pass

    def test_001_yaml(self):
        HEADING("Printer.write of a yaml object")
        output = Printer.write(self.d, order=None, header=None, output="yaml", sort_keys=True)
        print(output)
        assert ":" in output

    def test_002_json(self):
        HEADING("Printer.write of a json object")
        output = Printer.write(self.d, order=None, header=None, output="json", sort_keys=True)
        print(output)
        assert "{" in output

    def test_003_dict(self):
        HEADING("Printer.write of a dict object")
        output = Printer.write(self.d, order=None, header=None, output="dict", sort_keys=True)
        pprint(output)
        assert type(output) == dict

    def test_004_table(self):
        HEADING("Printer.write of a table object")
        output = Printer.write(self.d, order=None, header=None, output="table", sort_keys=True)
        print(output)
        # assert "id" in str(output)

    def test_005_csv(self):
        HEADING("Printer.write of a csv object")
        output = Printer.write(self.d, order=None, header=None, output="csv", sort_keys=True)
        print(output)
        # assert "id" in str(output)
