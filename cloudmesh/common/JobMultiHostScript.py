from cloudmesh.common.JobSet import JobSet
import os
import textwrap
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.Tabulate import Printer
from pprint import pprint
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter

class JobMultiHostScript:
    '''
    The JobMultiHostScript is a simple mechanism to run a number of commands formylated
    in a script in parallel over the hosts provided. The script is interpreted line
    by line and does not support multi line commands at this time. (Not difficult
    to implement when looking at \ at the end of a line.)

    Static method::
        script = """
          # This is a comment
          pwd     # tag: pwd
          uname -a
        """;

        hosts = Parameter.expand("purple[01-02]")
        result = JobMultiHostScript.execute(script, "script_name", hosts)
    '''

    def __init__(self, name):
        self.name = name

    def reset(self, name):
        self.name = name

    def run(self, script=None, hosts=None, executor=JobSet.ssh,
            **kwargs):
        # Prepare parameters
        if script is None:
            Console.error("The script is not defined, found None as content")
            return

        if kwargs:
            parameters = dotdict(**kwargs)
        else:
            parameters = dotdict({})
        #parameters.host = host

        # Prepare script
        self.script = textwrap.dedent(str(script))
        self.script = self.script.format(**kwargs)
        lines = self.script.splitlines()

        # Loop over each line
        for line in lines:
            stripped = line.strip()
            # Check if line is a comment
            if stripped.startswith("#") or stripped == "":
                pass
            else:
                # Create jobSet per line
                job = JobSet(line, executor=executor)
                tag = counter
                if "# tag:" in line:
                    line, tag = line.split("# tag:", 1)
                    tag = tag.strip()
                    line = line.strip()

                for host in hosts:
                    job.add({"name": host, "host": host, "command": line});
                job.run(parallel=len(hosts))
                job.Print()


    @staticmethod
    def execute(script, name="script", hosts=None, executor=JobSet.ssh,
                **kwargs):
        job = JobMultiHostScript(name)
        if hosts is not None:
            job.run(script=script, name=name, hosts=hosts,
                                   executor=executor, **kwargs)

    def __len__(self):
        return len(self.job)

    def __repr__(self):
        return str(self.job)

    def __str__(self):
        return str(self.job)


if __name__ == '__main__':
    script = """
    # This is a comment
    pwd     # tag: pwd
    uname -a
    """;

    hosts = Parameter.expand("purple[01-02]")
    print(hosts)
    result = JobMultiHostScript.execute(script, "script_name", hosts)
