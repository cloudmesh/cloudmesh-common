import textwrap

from cloudmesh.common.JobSet import JobSet
from cloudmesh.common.Shell import Shell
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

    def __init__(self, name, script, hosts, executor):
        self.name = name
        self.script = script
        self.hosts = hosts
        self.executor = executor

    def run(self, beginLine=None, endLine=None):
        # Prepare script
        self.script = textwrap.dedent(str(self.script))
        lines = self.script.splitlines()

        # Truncate lines if begin and/or line parameters are set
        if beginLine is not None and endLine is not None:
            lines = Shell.find_lines_between(lines, beginLine, endLine)
        elif beginLine is not None and endLine is None:
            lines = Shell.find_lines_from(lines, beginLine)
        elif beginLine is None and endLine is not None:
            lines = Shell.find_lines_to(lines, endLine)

        # Loop over each line
        for line in lines:
            stripped = line.strip()
            # Check if line is a comment
            if stripped.startswith("#") or stripped == "":
                pass
            else:
                # Create jobSet per line
                job = JobSet(self.name, executor=self.executor)
                if "# tag:" in line:
                    line, tag = line.split("# tag:", 1)
                    tag = tag.strip()
                    line = line.strip()

                # Execute jobSet for each host in parallel
                for host in self.hosts:
                    job.add({"name": host, "host": host, "command": line});
                job.run(parallel=len(self.hosts))
                job.Print()

    @staticmethod
    def execute(script, name="script", hosts=None, executor=JobSet.ssh,
                beginLine=None, endLine=None):
        job = JobMultiHostScript(name, script, hosts, executor)
        job.run(beginLine, endLine)

    # CMS Function
    def cms(self, arguments):
        # Prepare parameters
        script = None
        if arguments.script:
            script = arguments.script

        hosts = None
        if arguments.hosts:
            hosts = arguments.hosts

        name = "script"
        if arguments.name:
            name = name

        executor = JobSet.ssh
        if arguments.executor:
            executor = arguments.executor

        beginLine = None
        if arguments.begin:
            beginLine = arguments.begin

        endLine = None
        if arguments.end:
            endLine = arguments.end

        # Execute
        if script is not None and hosts is not None:
            job = JobMultiHostScript(name, script, hosts, executor)
            job.run(beginLine, endLine)
        else:
            if hosts is None:
                Console.error("The hosts are not defined, found None as content")
            if script is None:
                Console.error("The script is not defined, found None as content")
            return


if __name__ == '__main__':
    script = """
    # This is a comment

    # Task: pwd
    pwd     # tag: pwd

    # Task: uname
    uname -a
    """;

    hosts = Parameter.expand("purple[01-02]")
    result = JobMultiHostScript.execute(script, "script_name", hosts,
                                        beginLine="# Task: pwd", endLine="# Task: uname")
