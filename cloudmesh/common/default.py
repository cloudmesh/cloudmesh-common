from __future__ import print_function

from cloudmesh.db.strdb import YamlDB
from cloudmesh.common.util import path_expand


class Default(object):
    def _index(self, context, key):
        return str(context) + "," + str(key)

    def __init__(self, filename=None):
        if filename is None:
            self.filename = path_expand("~/.cloudmesh/default-data")

        self.data = YamlDB(self.filename)

    def __getitem__(self, context_key):
        try:
            if type(context_key) == tuple:
                context, key = context_key
                index = self._index(context, key)
                if index not in self.data:
                    return None
                else:
                    return self.data[index]
            else:
                d = self.__dict__()
                if context_key not in d:
                    return None
                else:
                    return self.__dict__()[context_key]
        except:
            return None

    def __setitem__(self, context_key, value):
        context, key = context_key
        self.data[self._index(context, key)] = value

    def __delitem__(self, context_key):
        print("DEL")
        if type(context_key) == tuple:
            context, key = context_key
            del self.data[self._index(context, key)]
        else:
            context = context_key
            for element in self.data:
                print("E", element, context)
                if element.startswith(context + ","):
                    del self.data[element]

    def __contains__(self, item):
        for key in self.data:
            if item == self.data[key]:
                return True
        return False

    def __str__(self):
        d = {}
        for element in self.data:
            context, key = element.split(",")
            value = self.data[element]
            if context not in d:
                d[context] = {}

            d[context][key] = value
        # return (str(self.data))
        return str(self.__dict__())

    def __dict__(self):
        d = {}
        for element in self.data:
            context, key = element.split(",")
            value = self.data[element]
            if context not in d:
                d[context] = {}

            d[context][key] = value
        return d

    def __repr__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    # def __add__(self, directory):
    #    for key in directory:
    #        self.data[key] = directory[key]

    # def __sub__(self, keys):
    #    for key in keys:
    #        del self.data[key]

    def close(self):
        self.data.close()


if __name__ == "__main__":
    v = Default()
    print(v)
    v["kilo", "gregor"] = "value"

    assert "value" in v
    del v["kilo", "gregor"]
    # assert "gregor" not in v

    v["kilo", "image"] = "i_k"
    v["kilo", "flavor"] = "f_k"

    v["chameleon", "image"] = "i_c"
    v["chameleon", "flavor"] = "f_c"

    print(v)

    print(v.__repr__())

    print(v["chameleon", "bla"])
    assert v["chameleon", "bla"] is None

    print(v["chameleon"])
    assert v["chameleon"]['image'] == 'i_c'
    print(v["bla"])
    assert v["bla"] is None
