from cloudmesh.common.dotdict import dotdict
from hostlist import expand_hostlist


class Parameter(object):
    @staticmethod
    def parse(arguments, **kwargs):
        """parses arguments based on their kind and aplies Parameter.expand or
        Parameter.arguments.dict. It is defined by specifying the name in arguments,
        followed by the keyword, expand,or dict. Example

        kind={'parameter': 'expand', 'experiment': 'dict', 'COMMAND': "str'}

        arguments = parse(arguments, **kind)
        or
        arguments = parse(parameter='expand', experiment='dict', COMMAND='str')

        here the it will be applied
           arguments.parameter = Parameter.expand(arguments.paramete)
           arguments.experiment = Parameeter.arguments_to_dict(arguments.experiment)

        Args:
            arguments (dict or doctdict): the dict or doctdict with the
                arguments
            kind (dict): dict with the names of the arguments that need
                to be remapped

        Returns:
            dotdict: a doctdict with parsed and remapped arguments
        """
        result = dotdict(arguments)
        if kwargs is not None:
            for k, value in kwargs.items():
                if value == "expand":
                    result[k] = Parameter.expand(result[k])
                elif value == "dict":
                    result[k] = Parameter.expand(result[k])
                    result[k] = Parameter.arguments_to_dict(result[k])
                elif value == "str":
                    result[k] = " ".join(result[k])
        return result

    @staticmethod
    def _expand(values):
        """given a string of the form "a,g-h,k,x-z"
        expand it tl a list with all characters between the - being expanded

        Args:
            values: string of the form "a,g-h,k,x-z"

        Returns:

        """
        if "," in values:
            found = values.split(",")
        elif "-" in values:
            _from, _to = values.split("-")
            upper = [chr(x) for x in range(65, 91)]
            lower = [chr(x) for x in range(97, 123)]
            all = upper + lower
            i_start = all.index(_from)
            i_end = all.index(_to)
            found = all[i_start : i_end + 1]  # not sure why there is +1
        else:
            found = [values]
        return found

    @classmethod
    def expand_string(cls, parameter):
        """can expand strings, but only allows either, or - in [] not mixed

        Args:
            parameter: string of the form prefix[a,g-h,k,x-z]postfix

        Returns:

        """
        print("O", parameter)

        if "[" not in parameter and "-" not in parameter and "," in parameter:
            return parameter.split(",")

        if "[" not in parameter and "-" not in parameter and "," not in parameter:
            return [parameter]

        elif "[" in parameter:
            prefix, found = parameter.split("[", 1)
            found, postfix = found.split("]", 1)

            found = Parameter._expand(found)

            expand = []
            for x in found:
                expand = expand + Parameter._expand(x)

            result = [f"{prefix}{x}{postfix}" for x in expand]
            return result

        return [parameter]

    @classmethod
    def expand(cls, parameter, allow_duplicates=False, sort=False, sep=":"):
        """Parameter.expand("a[0-1]")  -> ["a0", "a1"]
        Content sensitive : expansion
        Parameter.expand("local:a0,a1")  -> ["local:a0", "local:a1"]
        instead of
        Parameter.expand("local:[a0,a1]")  -> ["local:a0", "local:a1"]

        Args:
            parameter
            allow_duplicates
            sort

        Returns:

        """
        if type(parameter) == list or parameter is None:
            return parameter

        parameters = list(
            expand_hostlist(parameter, allow_duplicates=False, sort=False)
        )

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
        """Finds the value for the key name in multiple dicts

        Args:
            name: the key to find
            *dicts: the list of dicts

        Returns:

        """
        for d in dicts:
            if type(d) == str:
                return d
            elif name in d and d[name] is not None:
                return d[name]

        return None

    @staticmethod
    def find_bool(name, *dicts):
        """Finds the value for the key name in multiple dicts

        Args:
            name: the key to find
            *dicts: the list of dicts

        Returns:

        """
        value = False

        for d in dicts:
            if type(d) == str:
                value = d == "True"
            elif name in d:
                value = d[name]
            if type(value) == str:
                value = value == "True"

            if value:
                return True

        return False

    @staticmethod
    def arguments_to_dict(arguments):
        """converts a string of the form "a=1,b=2" to a dict
        {"a":"1", "b":"2"}
        all values are strings

        Args:
            arguments: the argument string

        Returns:
            a dic of argument and values
        """
        if arguments is None or len(arguments) == 0:
            return None
        parameters = {}
        for argument in Parameter.expand(arguments):
            key, value = argument.split("=", 1)
            parameters[key] = value
        return parameters

    @staticmethod
    def separate(text, sep=":"):
        if sep in text:
            return text.split(sep, 1)
        else:
            return None, text
