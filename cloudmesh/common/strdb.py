import os
import os.path
from builtins import bytes

import oyaml as yaml


#
# TODO: this does not follow our conventions, should this not be done at __init__?
#
###############################################################
#  make yaml understand unicode

def yaml_construct_unicode(self, node):
    return self.construct_scalar(node)


yaml.Loader.add_constructor(u'tag:yaml.org,2002:python/unicode', yaml_construct_unicode)
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:python/unicode', yaml_construct_unicode)


###############################################################
#  the db api

class YamlDB(object):
    """A YAML-backed Key-Value database to store strings
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
        string = yaml.dump(self._db, default_flow_style=False)
        bits = bytes(string, encoding='utf-8')
        with open(self.path, 'wb') as dbfile:
            dbfile.write(bits)

    def __setitem__(self, k, v):
        self._db[str(k)] = str(v)
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
        """This is a NoOP for backwards compatibility"""
        pass

    def clear(self):
        """Truncate the database"""
        self._db.clear()
        self.flush()

    def set(self, **kwargs):
        for name in kwargs:
            self._db[name] = kwargs[name]

    def dict(self):
        return self._db
