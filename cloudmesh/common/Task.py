import os
import subprocess
import textwrap
from multiprocessing import Pool
from sys import platform

from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
import threading


class JobSet:

    def __init__(self, name):
        self.name = name
        self.job = {}

    def add(self, spec):
        name = spec["name"]
        print(name, spec)

        self.job[name] = spec
        self.job[name]["status"] = "defined"
        self.job[name]["executor"] = spec.get("executor") or print

    def _run(self, spec):
        result = spec
        result["status"] = "running"
        executor = spec["executor"]
        result["stdout"] = executor(spec)
        result["status"] = "done"

    def run(self, processors=3):
        with Pool(processors) as p:
            res = p.map(self._run, self.job)
            p.close()
            p.join()

        return res

    def __str__(self):
        return str(self.job)


if __name__ == '__main__':
    s = JobSet("test")

    s.add({"name": "a", "value": 1})
    s.add({"name": "b", "value": 2})

    print(s.job)
    print(s.run())
    print(s.job)
