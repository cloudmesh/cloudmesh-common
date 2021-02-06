from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
from cloudmesh.common.strdb import YamlDB
from cloudmesh.common.console import Console


class Variables(object):
    def __init__(self, filename=None):
        self.filename = path_expand(filename or "~/.cloudmesh/variables.dat")
        self.data = YamlDB(self.filename)

    def __getitem__(self, key):
        if key not in self.data:
            return None
        else:
            return self.data[key]

    def __setitem__(self, key, value):
        # print("set", key, value)
        self.data[str(key)] = value

    def __delitem__(self, key):
        if key in self.data:
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

    def dict(self):
        return self.data._db

    def parameter(self, attribute, position=0):
        value = str(self.data[attribute])
        expand = Parameter.expand(value)[position]
        return expand

    def boolean(self, key, value):
        if str(value).lower() in ["true", "on"]:
            self.data[str(key)] = True
        elif str(value).lower() in ["false", "off"]:
            self.data[str(key)] = False
        else:
            Console.error("Value is not boolean")


if __name__ == "__main__":
    v = Variables()
    print(v)

    v["gregor"] = "gregor"
    assert "gregor" in v
    del v["gregor"]
    assert "gregor" not in v
