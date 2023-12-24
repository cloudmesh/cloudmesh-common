# noinspection PyPep8Naming
class dotdict(dict):
    """A convenient dot dict class::

        a = dotdict({"argument": "value"})

    print (a.argument)

    Nested dot documentation is not supported.
    """

    def __getattr__(self, attr):
        """retirns an element

        Args:
            attr: the attribute key

        Returns:
            teh value
        """
        return self.get(attr)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
