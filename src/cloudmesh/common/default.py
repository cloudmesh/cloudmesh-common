from pathlib import Path

from cloudmesh.common.base import Base
from cloudmesh.common.strdb import YamlDB
from cloudmesh.common.util import path_expand


# noinspection PyPep8
class Default(object):
    """
    A class used to manage default variables stored in a YAML database.

    This class provides methods for creating a unique index for each key-value pair in the data dictionary,
    initializing the default variables, and managing the YAML database where these variables are stored.

    Attributes:
        filename (Path): The path to the YAML database file.
        data (YamlDB): The YAML database where the default variables are stored.

    Methods:
        _index(context: str, key: str) -> str:
            Creates a unique index for each key-value pair in the data dictionary.
    """

    def _index(self, context, key):
        """
        Creates a unique index for the data dictionary.

        This method combines the context and the key into a single string, separated by a comma.
        This string serves as a unique index for each key-value pair in the data dictionary.

        Args:
            context (str): The context in which the key exists.
            key (str): The actual key for the value.

        Returns:
            str: The unique index for the key-value pair.
        """
        return str(context) + "," + str(key)

    def __init__(self, filename=None):
        """
        initializes the default variables. The default file is defined by the following order
        1. filename
        2. $CLOUDMESH_CONFIG_DIR/default-data
        2. ./.cloudmesh/default-data if .cloudmesh exists
        3, ~/.cloudmesh/default-data

        :param filename:
        """

        if filename is None:
            base = Base()

            self.filename = Path(path_expand(f"{base.path}/default-data"))
        else:
            self.filename = Path(path_expand(filename))

        self.data = YamlDB(str(self.filename))

    def __getitem__(self, context_key):
        """
        Retrieves the value of a specific key in the data dictionary.

        This method allows the use of bracket notation for getting values from the data dictionary.
        The key can be a tuple containing the context and the key, or a single string key.

        Args:
            context_key (Union[tuple, str]): A tuple containing the context and the key, or a single string key.
                                             The context is a string representing the context in which the key exists.
                                             The key is a string representing the actual key for the value.

        Returns:
            Any: The value associated with the specified key. If the key does not exist, returns None.

        Raises:
            TypeError: If the context_key is not a tuple or a string.
        """
        # noinspection PyPep8
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
        except:  # noqa: E722
            return None

    def __setitem__(self, context_key, value):
        """
        Sets the value of a specific key in the data dictionary.

        This method allows the use of bracket notation for setting values in the data dictionary.
        The key is expected to be a tuple containing the context and the key.

        Args:
            context_key (tuple): A tuple containing the context and the key. The context is a string
                                 representing the context in which the key exists. The key is a string
                                 representing the actual key for the value.
            value (Any): The value to set for the specified key.

        Raises:
            TypeError: If the context_key is not a tuple.
        """
        context, key = context_key
        self.data[self._index(context, key)] = value

    def __delitem__(self, context_key):
        """
        Deletes a specific key-value pair from the data dictionary.

        This method allows the use of bracket notation for deleting values in the data dictionary.
        The key can be a tuple containing the context and the key, or a single string key.

        Args:
            context_key (Union[tuple, str]): A tuple containing the context and the key, or a single string key.
                                             The context is a string representing the context in which the key exists.
                                             The key is a string representing the actual key for the value.

        Raises:
            KeyError: If the specified key does not exist in the data dictionary.
        """
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
        """
        Checks if a specific value exists in the data dictionary.

        This method allows the use of the 'in' keyword to check if a value exists in the data dictionary.

        Args:
            item (Any): The value to check for in the data dictionary.

        Returns:
            bool: True if the value exists in the data dictionary, False otherwise.
        """
        for key in self.data:
            if item == self.data[key]:
                return True
        return False

    def __str__(self):
        """
        Returns a string representation of the data dictionary.

        This method converts the data dictionary into a nested dictionary where the outer dictionary's keys are the contexts,
        and the values are inner dictionaries with the keys and values from the original data dictionary.
        The nested dictionary is then converted into a string.

        Returns:
            str: A string representation of the data dictionary.
        """
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
        """
        Returns a dictionary representation of the data dictionary.

        This method converts the data dictionary into a nested dictionary where the outer dictionary's keys are the contexts,
        and the values are inner dictionaries with the keys and values from the original data dictionary.

        Returns:
            dict: A dictionary representation of the data dictionary.
        """
        d = {}
        for element in self.data:
            context, key = element.split(",")
            value = self.data[element]
            if context not in d:
                d[context] = {}

            d[context][key] = value
        return d

    def __repr__(self):
        """
        Returns a string representation of the data dictionary suitable for debugging.

        This method returns a string that, if fed to the eval() function, should produce an equivalent object.
        In this case, it returns a string representation of the data dictionary.

        Returns:
            str: A string representation of the data dictionary.
        """
        return str(self.data)

    def __len__(self):
        """
        Returns the number of key-value pairs in the data dictionary.

        This method allows the use of the len() function on the data dictionary.

        Returns:
            int: The number of key-value pairs in the data dictionary.
        """
        return len(self.data)

    # def __add__(self, directory):
    #    for key in directory:
    #        self.data[key] = directory[key]

    # def __sub__(self, keys):
    #    for key in keys:
    #        del self.data[key]

    def close(self):
        """
        Closes the data dictionary.

        This method is used to safely close the data dictionary when it is no longer needed,
        freeing up any resources it was using.

        Raises:
            Exception: If the data dictionary cannot be closed.
        """
        # ... existing code ...

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
    assert v["chameleon"]["image"] == "i_c"
    print(v["bla"])
    assert v["bla"] is None
