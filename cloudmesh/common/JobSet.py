import os
import subprocess
import textwrap
from multiprocessing import Pool
from sys import platform
from pprint import pprint

from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
import threading
from cloudmesh.common.debug import VERBOSE

class JobSet:

    def __init__(self, name, executor=None):
        self.name = name
        self.job = {}
        self.executor = executor or JobSet.execute

    @staticmethod
    def execute(spec):
        result = subprocess.check_output(spec["command"], shell=True)

        return dict({
            "name": spec["name"],
            "stdout": result,
            "stderr": "",
            "returncode": 0,
            "status": "defined"
        })

    @staticmethod
    def identity(entry_with_name):

        return dict({
            "name": entry_with_name["name"],
            "stdout": "identity " + entry_with_name["name"],
            "stderr": "",
            "returncode": 0,
            "status": "defined"
        })

    def add(self, spec, executor=None):
        name = spec["name"]
        self.job[name] = spec
        self.job[name]["status"] = "defined"
        self.job[name]["executor"] = spec.get("executor") or executor or self.executor

    def _run(self, spec):
        result = dict(spec)
        result["status"] = "running"
        executor = spec["executor"]
        res = executor(spec)
        result.update(res)
        result["status"] = "done"
        return result

    def run(self, processors=3):

        joblist = [self.job[x] for x in self.job]
        VERBOSE(joblist)
        with Pool(processors) as p:
            res = p.map(self._run, joblist)
            p.close()
            p.join()

        for entry in res:
            name = entry['name']
            for a in entry:
                self.job[name].update(entry)

        return res

    def __str__(self):
        return str(self.job)

    def Print(self):
        print()
        d = dict(self.job)
        for e in d:
            del d[e]["executor"]
        pprint (d)


if __name__ == '__main__':
    def command_execute(spec):
        return dict({
            "name": spec["name"],
            "stdout": "command " + spec["command"],
            "stderr": "",
            "returncode": 0,
            "status": "defined"
        })


    s = JobSet("test", executor=JobSet.identity)

    s.add({"name": "a", "value": 1})
    s.add({"name": "b", "value": 2})

    pprint(s.job)
    result = s.run()
    pprint (result)

    pprint(s.job)
    s.Print()


    t = JobSet("test2", executor=JobSet.execute)
    t.add({"name": "c", "command": "pwd"})
    t.add({"name": "d", "command": "uname -a"})
    t.add({"name": "e", "command": "uname"})
    t.add({"name": "f", "command": "hostname"})
    t.add({"name": "g", "command": "ps"})
    t.run()
    t.Print()

    #x = {"name": "x", "command": "ls", "executor": command_execute}
    #print (command_execute(x))
