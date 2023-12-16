###############################################################
# pytest -v --capture=no tests/test_tabulate.py
# pytest -v --capture=no  tests/test_tabulate..py::Test_tabulate.test_001
# pytest -v  tests/test_tabulate.py
###############################################################

from pprint import pprint

import pytest
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.util import HEADING


@pytest.mark.incremental
class Test_Tabulate:

    def setup_method(self):
        self.data = [
            {
                "name": "Gregor",
                "address": {
                    "street": "Funny Lane 11",
                    "city": "Cloudville"
                }
            },
            {
                "name": "Albert",
                "address": {
                    "street": "Memory Lane 1901",
                    "city": "Cloudnine"
                }
            }
        ]


    def test_001_print(self):
        HEADING()
        pprint (self.data)
        table = Printer.flatwrite(self.data,
                            sort_keys=["name"],
                            order=["name", "address.street", "address.city"],
                            header=["Name", "Street", "City"],)

        print(table)
        assert "Name" in str(table)
