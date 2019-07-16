from hostlist import expand_hostlist
from cloudmesh.common.dotdict import dotdict

class Parameter(object):
    @classmethod
    def expand(cls, parameter, allow_duplicates=False, sort=False):
        if parameter is None:
            return parameter
        else:
            return expand_hostlist(parameter, allow_duplicates=False, sort=False)

    @staticmethod
    def find(name, *dicts):
        """
        Finds the value for the key name in multiple dicts

        :param name: the key to find
        :param dicts: the list of dicts
        :return:
        """
        for d in dicts:
            if name in d and d[name] is not None:
                return d[name]
        return None



