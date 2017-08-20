from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from ruamel import yaml


class Config(object):
    def __init__(self, filename=None):
        self.filename = filename
        if self.filename is None:
            self.filename = path_expand("~/.cloudmesh/cloudmesh2.yaml")
        content = readfile(self.filename)
        self.data = yaml.load(content, Loader=yaml.RoundTripLoader)

    def cloud(self, name):
        return self.data["cloudmesh"]["clouds"][name]

    def credentials(self, name):
        return dotdict(self.cloud(name)["credentials"])


'''
if __name__ == "__main__":
    from pprint import pprint
    c = Config()
    pprint(c.credentials("jet"))
'''
