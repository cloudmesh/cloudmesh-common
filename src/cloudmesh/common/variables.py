from cloudmesh.common.base import Base
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.strdb import YamlDB
from cloudmesh.common.util import path_expand


class Variables(object):
    """A class for managing and manipulating variables using a YAML-based storage.

    Attributes:
        filename (str): The path to the YAML file storing the variables.
        data (YamlDB): An instance of the YamlDB class for YAML file manipulation.

    Methods:
        save(): Save changes to the YAML file.
        get(key, default=None): Retrieve the value associated with a key.
        __getitem__(key): Retrieve the value associated with a key using square bracket notation.
        __setitem__(key, value): Set the value associated with a key using square bracket notation.
        __delitem__(key): Delete the key-value pair associated with the specified key.
        __contains__(item): Check if a key exists in the stored data.
        __str__(): Return a string representation of the stored data.
        __len__(): Return the number of key-value pairs in the stored data.
        __add__(directory): Add key-value pairs from a dictionary-like object.
        __sub__(keys): Remove key-value pairs for specified keys.
        __iter__(): Return an iterator for keys in the stored data.
        close(): Close the connection to the YAML file.
        clear(): Clear all key-value pairs in the stored data.
        dict(): Return the underlying dictionary used for storage.
        parameter(attribute, position=0): Retrieve and expand a parameterized value.
        boolean(key, value): Set a boolean value based on string representation.

    Examples:
        v = Variables()
        print(v)

        v["gregor"] = "gregor"
        assert "gregor" in v
        del v["gregor"]
        assert "gregor" not in v
    """

    def __init__(self, filename=None):
        """Initialize the Variables instance.

        Args:
            filename (str): The path to the YAML file storing the variables.
        """
        if filename is None:
            base = Base()
            self.filename = f"{base.path}/variables.dat"
        else:
            self.filename = path_expand(filename or "~/.cloudmesh/variables.dat")
        self.data = YamlDB(self.filename)

    def save(self):
        """Save changes to the YAML file."""
        self.data.flush()

    def get(self, key, default=None):
        """Retrieve the value associated with a key.

        Args:
            key (str): The key whose value is to be retrieved.
            default: The default value to return if the key is not found.

        Returns:
            The value associated with the specified key, or the default value if the key is not found.
        """
        return self.data.get(key, default)

    def __getitem__(self, key):
        """Retrieve the value associated with a key using square bracket notation.

        Args:
            key (str): The key for which the value is to be retrieved.

        Returns:
            Any: The value associated with the specified key.

        Note:
            If the key is not found, the method returns None.
        """
        if key not in self.data:
            return None
        else:
            return self.data[key]

    def __setitem__(self, key, value):
        """Set the value associated with a key using square bracket notation.

        Args:
            key (str): The key for which the value is to be set.
            value: The value to be associated with the key.
        """
        # print("set", key, value)
        self.data[str(key)] = value

    def __delitem__(self, key):
        """Delete the key-value pair associated with the specified key.

        Args:
            key (str): The key for which the key-value pair is to be deleted.
        """
        if key in self.data:
            del self.data[str(key)]

    def __contains__(self, item):
        """Check if a key exists in the stored data.

        Args:
            item: The key to be checked for existence.

        Returns:
            bool: True if the key exists; otherwise, False.
        """
        return str(item) in self.data

    def __str__(self):
        """Return a string representation of the stored data.

        Returns:
            str: A string representation of the stored data.
        """
        return str(self.data)

    def __len__(self):
        """Return the number of key-value pairs in the stored data.

        Returns:
            int: The number of key-value pairs in the stored data.
        """
        return len(self.data)

    def __add__(self, directory):
        """Add key-value pairs from a dictionary-like object.

        Args:
            directory (dict): A dictionary-like object containing key-value pairs to be added.
        """
        for key in directory:
            self.data[key] = directory[key]

    def __sub__(self, keys):
        """Remove key-value pairs for specified keys.

        Args:
            keys (list): A list of keys for which the key-value pairs are to be removed.
        """
        for key in keys:
            del self.data[key]

    def __iter__(self):
        """Return an iterator for keys in the stored data.

        Returns:
            iter: An iterator for keys in the stored data.
        """
        return iter(self.data)

    def close(self):
        """Close the connection to the YAML file."""
        self.data.close()

    def clear(self):
        """Clear all key-value pairs in the stored data."""
        self.data.clear()

    def dict(self):
        """Return the underlying dictionary used for storage.

        Returns:
            dict: The underlying dictionary used for storage.
        """
        return self.data._db

    def parameter(self, attribute, position=0):
        """Retrieve and expand a parameterized value.

        Args:
            attribute (str): The attribute for which the parameterized value is to be retrieved.
            position (int): The position of the expanded value in the parameterized string.

        Returns:
            str: The expanded value of the parameterized attribute.
        """
        value = str(self.data[attribute])
        expand = Parameter.expand(value)[position]
        return expand

    def boolean(self, key, value):
        """Set a boolean value based on string representation.

        Args:
            key (str): The key for which the boolean value is to be set.
            value: The value to be interpreted as a boolean.

        Raises:
            ConsoleError: If the provided value is not a valid boolean representation.
        """
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
