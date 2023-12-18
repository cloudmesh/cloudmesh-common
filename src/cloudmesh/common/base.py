import os


def directory_exists(directory_name):
    # Get the current directory
    current_dir = os.getcwd()

    location = os.path.join(current_dir, directory_name)
    # Check if the directory exists
    return os.path.exists(location) and os.path.isdir(location)


class Base:

    """The Base path for te cloudmesh.yaml file can be set automatically with this class
    The following test are done in that order

    base = Base()

    if CLOUDMESH_CONFIG_DIR is set as environment variable it uses that base

    if Base(path=..) is used that path is used
    if a .cloudmesh dir exists in the current directory that dir is used
    otherwise ~/.cloudmesh is used

    """

    def __init__(self, path=None, create=True):
        self.key = "CLOUDMESH_CONFIG_DIR"

        if path is not None:
            self.path = path

        elif self.key in os.environ:
            self.path = os.environ.get(self.key)

        elif directory_exists(".cloudmesh"):
            self.path = ".cloudmesh"

        elif path is None:
            self.path = "~/.cloudmesh"

        # Expand the tilde (~) to the user's home directory path
        self.path = os.path.expanduser(self.path)

        self.config = os.path.join(self.path, "cloudmesh.yaml")
        if create:
            self.create()

    def create(self):
        os.makedirs(self.path, exist_ok=True)
