from cloudmesh.common.JobSet import JobSet
import os
import textwrap
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.Tabulate import Printer
from pprint import pprint
from cloudmesh.common.console import Console


class JobScript:
    '''
    The jobscript is a simple mechanism to run a number of commands formylated
    in a script. The script is interpreted line by line and does not support
    multi line commands at this time. (Not difficult to implement when
    looking at \ at the end of a line.)

    It can be either used a static call or as variable invocation. Often the
    static call will be sufficient.

    Static method::

        from cloudmesh.common.JobSet import JobScript
        from cloudmesh.common.Tabulate import Printer

        result = JobScript.execute("""
            # This is a comment

            pwd                             # tag: pwd
            uname -a
        """)
        print(Printer.write(result,
                order=["name", "command", "status", "stdout", "returncode"]))

    Variable invocation::

        from cloudmesh.common.Tabulate import Printer

        job = JobScript()
        job.run(name="variable script",
                script="""
                    # This is a comment

                    pwd                    # tag: pwd
                    uname -a
                """)
        print(Printer.write(
            job.array(),
            order=["name", "command", "status", "stdout", "returncode"]))

        Each line is augmented with a name, so you can easily retrive the result
        content by that name. By default the name is the line number, however it
        can be overwritten with `# tag:` at the end of the line. The line number
        starts at 1.

    Partial example output:

        # +------+-----------+--------+------------------------+--------------+
        # | name | command   | status |                        |   returncode |
        # |------+-----------+--------+------------------------+--------------|
        # | pwd  | pwd       | done   | /Users/.../cloudmesh   |            0 |
        # | 4    | uname -a  | done   | Darwin gray 19.4.0 ... |            0 |
        # +------+-----------+--------+------------------------+--------------+
    '''

    def __init__(self):
        self.script = None

    def run(self, script=None, name="script", host=None, executor=JobSet.ssh,
            **kwargs):
        # Prepare parameters
        if script is None:
            Console.error("The script is not defined, found None as content")
            return
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
        counter = 1
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") or stripped == "":
                pass
            else:
                tag = counter
                if "# tag:" in line:
                    line, tag = line.split("# tag:", 1)
                    tag = tag.strip()
                    line = line.strip()
                jobs.add({
                    "script": name,
                    "name": tag,
                    "tag": tag,
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
        job.run(script=script, name=name, host=host, **kwargs)
        return job.array()

    @staticmethod
    def _array():
        return

    def array(self):
        return [self.job[x] for x in self.job]


if __name__ == '__main__':
    #
    # Tow ways to run.
    #

    # Static method
    result = JobScript.execute("""
        # This is a comment
        
        pwd                             # tag: pwd
        uname -a
    """)
    print(Printer.write(
        result,
        order=["name", "command", "status", "stdout", "returncode"]))

    # Variables
    job = JobScript()
    job.run(name="variable script",
            script="""
                # This is a comment
        
                pwd                    # tag: pwd
                uname -a
            """)
    print(Printer.write(
        job.array(),
        order=["name", "command", "status", "stdout", "returncode"]))

#
# Partial example output
#
# +------+-----------+--------+-------------------------------+--------------+
# | name | command   | status |                               |   returncode |
# |------+-----------+--------+-------------------------------+--------------|
# | pwd  | pwd       | done   | /Users/..../cloudmesh/common  |            0 |
# | 4    | uname -a  | done   | Darwin gray 19.4.0 Darwin ... |            0 |
# +------+-----------+--------+-------------------------------+--------------+
