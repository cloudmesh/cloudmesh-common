from hostlist import expand_hostlist


class Parameter(object):
    @classmethod
    def expand(cls, parameter, allow_duplicates=False, sort=False):
        if parameter is None:
            return parameter
        else:
            return expand_hostlist(parameter, allow_duplicates=False, sort=False)

    @staticmethod
    def find_attribute (name, dicts):
        for d in dicts:
            if name in d:
                return d[name]
        return None
