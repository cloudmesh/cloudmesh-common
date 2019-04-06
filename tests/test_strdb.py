###############################################################
#  tests

#
# TODO: theres is absolutely no need to use hypothesis. THis code does not
#       follow our convention to develop nose tests. Also using nosetests 
#       allows us to get rid of hypothesis
#
import os
import unittest
from hypothesis import given
from hypothesis import strategies as st
from tempfile import mkstemp
from ruamel import yaml
from cloudmesh.db.strdb import YamlDB


class TestYamlDB(unittest.TestCase):
    def setUp(self):
        self.dbfd, self.dbpath = mkstemp(
            prefix='cloudmesh.db.strdb.TestYamlDB.'
        )
        self.db = YamlDB(path=self.dbpath)

    def tearDown(self):
        os.close(self.dbfd)
        os.unlink(self.dbpath)

    @given(st.text(), st.text())
    def test_insert(self, key, value):
        self.db[key] = value

    @given(st.text(), st.text())
    def test_in(self, key, value):
        self.db[key] = value
        self.assertIn(key, self.db)

    @given(st.text(), st.text())
    def test_get(self, key, value):
        self.db[key] = value
        dbvalue = self.db[key]
        self.assertEqual(value, dbvalue)

    @given(st.text(), st.text())
    def test_del(self, key, value):
        self.db[key] = value
        del self.db[key]
        self.assertNotIn(key, self.db)

    @given(st.text(), st.text())
    def test_persistence(self, key, value):
        self.db[key] = value
        with open(self.dbpath, 'rb') as dbfile:
            db = yaml.safe_load(dbfile)
        self.assertIn(key, db)
        self.assertEqual(value, db[key])

    @given(st.text(), st.text())
    def test_iter(self, key, value):
        self.db[key] = value
        for k in self.db:
            pass

    @given(st.text(), st.text())
    def test_clear(self, key, value):
        self.db[key] = value
        self.db.clear()
        self.assertNotIn(key, self.db)

    @given(st.lists(st.tuples(st.text(), st.text())))
    def test_len(self, entries):
        self.db.clear()

        duplicates = 0
        for k, v in entries:
            duplicates += 1 if k in self.db else 0
            self.db[k] = v
        self.assertEqual(len(self.db), len(entries) - duplicates)


if __name__ == '__main__':
    unittest.main()