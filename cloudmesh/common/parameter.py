from hostlist import expand_hostlist


class Parameter(object):

    @classmethod
    def expand(cls, parameter, allow_duplicates=False, sort=False, sep=":"):
        """
        Parameter.expand("a[0-1]")  -> ["a0", "a1"]
        Content sensitive : expansion
        Parameter.expand("local:a0,a1")  -> ["local:a0", "local:a1"]
        instead of
        Parameter.expand("local:[a0,a1]")  -> ["local:a0", "local:a1"]

        :param parameter:
        :param allow_duplicates:
        :param sort:
        :return:
        """
        if parameter is None:
            return parameter

        return list(expand_hostlist(parameter,
                                    allow_duplicates=False,
                                    sort=False))
    @classmethod
    def _expand(cls, parameter, allow_duplicates=False, sort=False, sep=":"):
        """
        Parameter.expand("a[0-1]")  -> ["a0", "a1"]
        Content sensitive : expansion
        Parameter.expand("local:a0,a1")  -> ["local:a0", "local:a1"]
        instead of
        Parameter.expand("local:[a0,a1]")  -> ["local:a0", "local:a1"]

        :param parameter:
        :param allow_duplicates:
        :param sort:
        :return:
        """
        if parameter is None:
            return parameter

        parameters = list(expand_hostlist(parameter,
                                          allow_duplicates=False,
                                          sort=False))

        results = [t.split(sep, 1) for t in parameters]
        merge = []

        for entry in results:
            merge = merge + entry

        if len(merge) == len(parameters):
            return parameters

        elif len(merge) == len(parameters) + 1 and len(results[0]) == 2:

            prefix = results[0][0]
            _results = []
            for i in range(1, len(parameters)):
                parameters[i] = f"{prefix}:{parameters[i]}"

            return parameters

        else:

            return parameters

    @staticmethod
    def find(name, *dicts):
        """
        Finds the value for the key name in multiple dicts

        :param name: the key to find
        :param dicts: the list of dicts
        :return:
        """
        for d in dicts:
            if type(d) == str:
                return d
            elif name in d and d[name] is not None:
                return d[name]

        return None

    @staticmethod
    def find_bool(name, *dicts):
        """
        Finds the value for the key name in multiple dicts

        :param name: the key to find
        :param dicts: the list of dicts
        :return:
        """
        value = False

        for d in dicts:
            if type(d) == str:
                value = d == 'True'
            elif name in d:
                value = d[name]
            if type(value) == str:
                value = value == 'True'

            if value:
                return True

        return False

    @staticmethod
    def arguments_to_dict(arguments):
        """
        converts a string of the form "a=1,b=2" to a dict
        {"a":"1", "b":"2"}
        all values are strings

        :param arguments: the argument string
        :return: a dic of argument and values
        """
        if arguments is None or len(arguments) == 0:
            return None
        parameters = {}
        for argument in arguments:
            key, value = arguments.split("=", 1)
            parameters[key] = value
        return parameters

    @staticmethod
    def separate(text, sep=":"):
        if sep in text:
            return text.split(sep, 1)
        else:
            return None, text
