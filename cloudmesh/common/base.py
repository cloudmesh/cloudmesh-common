import os
from cloudmesh.common.Shell import directory_exists


class Cloudmesh:

    def __init__(self, path=None, create=True):

        if path is not None:
            self.path = path

        elif "CLOUDMESH" in os.environ:
            print ("A")
            self.path = os.environ.get("CLOUDMESH")

        elif directory_exists(".cloudmesh"):
            print ("B")
            self.path = ".cloudmesh"

        elif path is None:
            print("C")
            self.path = "~/.cloudmesh"

        # Expand the tilde (~) to the user's home directory path
        self.path = os.path.expanduser(self.path)

        self.config = os.path.join(self.path, "cloudmesh.yaml")
        if create:
            self.create()

    def create(self):
        os.makedirs(self.path, exist_ok=True)
