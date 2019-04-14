from __future__ import print_function

from cloudmesh.db.strdb import YamlDB
from cloudmesh.common.util import path_expand


class Variables(object):
    def __init__(self, filename=None):
        self.filename = path_expand(filename or "~/.cloudmesh/var-data")
        self.data = YamlDB(self.filename)

    def __getitem__(self, key):
        if key not in self.data:
            return None
        else:
            return self.data[key]

    def __setitem__(self, key, value):
        print("set", key, value)
        self.data[str(key)] = value

    def __delitem__(self, key):
        del self.data[str(key)]

    def __contains__(self, item):
        return str(item) in self.data

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def __add__(self, directory):
        for key in directory:
            self.data[key] = directory[key]

    def __sub__(self, keys):
        for key in keys:
            del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def close(self):
        self.data.close()

    def clear(self):
        self.data.clear()


if __name__ == "__main__":
    v = Variables()
    print(v)

    v["gregor"] = "gregor"
    assert "gregor" in v
    del v["gregor"]
    assert "gregor" not in v
