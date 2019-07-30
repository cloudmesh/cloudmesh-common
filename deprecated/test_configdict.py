###############################################################
# pip install .; pytest -v --capture=no  tests/test_configdict.py:Test_configdict.test_001
# pytest -v --capture=no tests/test_configdictr.py
# pytest -v  tests/test_configdict.py
###############################################################

from __future__ import print_function

import os

from cloudmesh.common.ConfigDict import ConfigDict
from cloudmesh.common.util import HEADING
import pytest

@pytest.mark.incremental
class Test_configdict:

    # noinspection PyPep8Naming
    def tearDown(self):
        pass

    def test_001_read(self):
        HEADING("test if cloudmesh.yaml is loaded")
        d = ConfigDict("cloudmesh.yaml",
                       verbose=True)

        assert d["cloudmesh"]["profile"]["firstname"] != ""
        assert len(d["cloudmesh"]["clouds"]) > 0

        """
        #
        # DO NOT DO THIS TEST AS LOGIC OF AUTOCREATION HAS CHANGED
        #
        # try:
        #     d = ConfigDict("cloudmesh.yam",
        #                    verbose=True)
        #     print("the file cloudmesh.yam should not exists")
        #     assert False
        # except Exception as e:
        #     print (">>>>>>>", e)
        #     assert str(e).startswith("Could not find")
        """

    """ do not test for etc
    def test_002_set(self):
        HEADING("testing to set a value in the dict")
        shutil.copy(self.etc_yaml, self.tmp_yaml)
        d = ConfigDict("cloudmesh.yaml",
                       load_order=[self.tmp_dir],
                       verbose=True)
        d["cloudmesh"]["profile"]["firstname"] = "Gregor"
        d.save()

        d = ConfigDict("cloudmesh.yaml",
                       load_order=[self.tmp_dir],
                       verbose=True)
        assert d["cloudmesh"]["profile"]["firstname"] == "Gregor"
    """
        
    def test_003_json(self):
        HEADING("test if json is produced")
        d = ConfigDict("cloudmesh.yaml",
                       verbose=True)

        assert d.json.startswith('{')

        try:
            assert not isinstance(d.json, str)
            print("json should be string")
            assert False
        except Exception as e:
            assert isinstance(d.json, str)

    def test_004_yaml(self):

        HEADING("test if yaml is produced")
        d = ConfigDict("cloudmesh.yaml",
                       verbose=True)
        result = d.yaml

        try:
            assert result.startswith("meta")
        except Exception as e:
            print("not valid yaml file.")
            assert False


"""	def main():
    d = ConfigDict("cmd3.yaml")
    print (d, end='')
    print(Printer.write(self.cm.info()))


    print (d["meta"])
    print (d["meta.kind"])
    print (d["meta"]["kind"])

    # this does not yet work
    print (d)
    d.save()

    import os
    os.system("cat cmd3.yaml")

    print(d.json)
    print(d.filename)

if __name__ == "__main__":
    main()
"""
