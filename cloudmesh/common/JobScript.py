from cloudmesh.common.JobSet import JobSet
import os
import textwrap
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.Tabulate import Printer
from pprint import pprint

class JobScript:

    def __init__(self):
        self.script = None

    def run(self, script, name="script", host=None, executor=JobSet.ssh,
            **kwargs):
        # Prepare parameters
        host = host or os.uname()[1]
        if kwargs:
            parameters = dotdict(**kwargs)
        else:
            parameters = dotdict({})
        parameters.host = host
        # Prepare script
        self.script = textwrap.dedent(str(script))
        self.script = self.script.format(**kwargs)

        lines = self.script.splitlines()
        # Add script to jobset and run
        jobs = JobSet("onejob", executor=executor)
        counter = 0
        for line in lines:
            stripped = line.strip()
            print (f">{stripped}<")
            if stripped.startswith("#") or stripped == "":
                pass
            else:
                jobs.add({
                    "script": name,
                    "name": f"{name}-{counter}",
                    "line": counter,
                    "host": host,
                    "counter": counter,
                    "command": line
                })
            counter = counter + 1
        jobs.run(parallel=1)
        self.job = jobs.job
        return self.job

    @staticmethod
    def execute(script, name="script", host=None, executor=JobSet.ssh,
                **kwargs):
        job = JobScript()
        job.run(script, name=name, host=host, **kwargs)
        return job.array()

    @staticmethod
    def _array():
        return

    def array(self):
        return [self.job[x] for x in self.job]

if __name__ == '__main__':
    result = JobScript.execute("""
        # This is a comment
        
        pwd
        uname -a
    """)
    pprint(result)
    print(Printer.write(result,
                        order=["script", "line", "command", "status", "stdout",
                               "returncode"]))
