""" run with

python setup.py install; nosetests -v --nocapture tests/test_configdict.py:Test_configdict.test_001

nosetests -v --nocapture tests/test_printer.py

or

nosetests -v tests/test_printer.py

"""
from __future__ import print_function
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from pprint import pprint

class Test_configdict:

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