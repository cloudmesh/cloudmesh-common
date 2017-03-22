class TODO(object):

    @classmethod
    def implement(cls, msg="Please implement"):
        """temporary function to use to indicate that the code is not
           yet implemented"""
        raise NotImplementedError(msg)
