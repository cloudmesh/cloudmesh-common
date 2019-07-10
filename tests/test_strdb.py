###############################################################
# pip install .; npytest -v --capture=no  tests/test_strdb.py:Test_strdb.test_001
# pytest -v --capture=no  tests/test_strdb.py
# pytest -v tests/test_strdb.py
###############################################################

import os
import pytest
from tempfile import mkstemp
import oyaml as yaml
from cloudmesh.db.strdb import YamlDB

@pytest.mark.incremental
class TestYamlDB:

    def setup(self):
        self.key = "key"
        self.value = "value"
        self.dbfd, self.dbpath = mkstemp(
            prefix='cloudmesh.db.strdb.TestYamlDB.'
        )
        self.db = YamlDB(path=self.dbpath)

    def test_insert(self):
        self.db[self.key] = self.value

    def test_in(self):
        self.db[self.key] = self.value
        assert self.key in self.db

    def test_get(self):
        self.db[self.key] = self.value
        dbvalue = self.db[self.key]
        assert self.value == dbvalue

    def test_del(self):
        self.db[self.key] = self.value
        del self.db[self.key]
        assert self.key not in self.db

    def test_persistence(self):
        self.db[self.key] = self.value
        with open(self.dbpath, 'rb') as dbfile:
            db = yaml.safe_load(dbfile)
        assert self.key in db
        assert self.value == db[self.key]

    def test_iter(self):
        self.db[self.key] = self.value
        for k in self.db:
            pass

    def test_clear(self):
        self.db[self.key] = self.value
        self.db.clear()
        assert self.key not in self.db

    def test_len(self):
        self.db.clear()
        entries = ['a', 'b', 'c']

        for k in entries:
            self.db[k] = k
        assert len(self.db) == len(entries)


    def tearDown(self):
        os.close(self.dbfd)
        os.unlink(self.dbpath)
