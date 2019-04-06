###############################################################
# pip install .; pytest -v --capture=no -v --nocapture tests/test_printer.py:Test_printer.test_001
# pytest -v --capture=no tests/test_printer.py
# pytest -v  tests/test_printer.py
###############################################################

from __future__ import print_function
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from pprint import pprint

class Test_Printer:

    def setup(self):
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
        print(Printer.flatwrite(self.data,
                            sort_keys=["name"],
                            order=["name", "address.street", "address.city"],
                            header=["Name", "Street", "City"],)
              )