"""
A class to call a TODO message. Typically it will just raise na exception. 
However when using the TODO it allows to list the TODO in editors such as 
pycharm to easier find them.
"""


class TODO(object):
    """
    class to raise an exception for code that has not yet been implemented.
    
    import cloudmesh.common.todo
    TODO.implement()
    """

    @classmethod
    def implement(cls, msg="Please implement"):
        """
        Raises an exception as not implemented
        :param msg: the message to print
        :return: 
        """
        print(msg)
        raise NotImplementedError(msg)
