from ruamel import yaml

import os.path
import os


################################################################ make yaml understand unicode

def yaml_construct_unicode(self, node):
    return self.construct_scalar(node)

yaml.Loader.add_constructor(u'tag:yaml.org,2002:python/unicode', yaml_construct_unicode)
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:python/unicode', yaml_construct_unicode)


################################################################ the db api

class YamlDB(object):
    """A YAML-backed Key-Value database.

    Assumption
    ==========

    Values are strings so there is no need to pickle/unpickle objects.

    """

    def __init__(self, path):
        self._db = dict()

        self.path = path

        prefix = os.path.dirname(self.path)
        if not os.path.exists(prefix):
            os.makedirs(prefix)

        if os.path.exists(self.path):
            with open(self.path, 'rb') as dbfile:
                self._db = yaml.safe_load(dbfile) or dict()

        self.flush()

    def flush(self):
        with open(self.path, 'wb') as dbfile:
            yaml.dump(self._db, dbfile, default_flow_style=False)

    def __setitem__(self, k, v):
        assert isinstance(v, str) or isinstance(v, unicode), repr(v)
        # the assertion should short-circuit, supporting Py2 and Py3
        self._db[k] = v
        self.flush()

    def __getitem__(self, k):
        return self._db[k]

    def __delitem__(self, k):
        del self._db[k]
        self.flush()

    def __contains__(self, k):
        return k in self._db

    def __iter__(self):
        return iter(self._db)

    def __len__(self):
        return len(self._db)

    def close(self):
        "This is a NoOP for backwards compatibility"
        pass

    def clear(self):
        "Truncate the database"
        self._db.clear()
        self.flush()


################################################################ tests

import unittest
from hypothesis import given
from hypothesis import strategies as st
from tempfile import mkstemp


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
