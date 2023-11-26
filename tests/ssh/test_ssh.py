###############################################################
# pytest -v --capture=no tests/ssh/test_ssh.py
# pytest -v  tests/tests/ssh/test_ssh.py
# pytest -v --capture=no  tests/ssh/test_ssh..py::Test_name::<METHODNAME>
###############################################################

# https://github.com/actions/runner-images/issues/1519 ping does not work in github runner so we skip it.
import os
from distutils.util import strtobool
github_action = strtobool(os.getenv('GITHUB_ACTIONS', 'false'))

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch

Benchmark.debug()

cloud = "local"
# multiping only works if you have root, so we can not use it
# from multiping import MultiPing

thishost = Shell.run('hostname')

hosts = ['127.0.0.1',
         'localhost',
         '127.0.0.1',
         'localhost',
         '127.0.0.1',
         'localhost',
         '127.0.0.1',
         'localhost',
         '127.0.0.1',
         'localhost',
         '127.0.0.1',
         'localhost',
         '127.0.0.1',
         'localhost'
         ]


def craete_location(host):
    return {
        'host': host,
        'username': os.environ['USER'],
        'key': '~/.ssh/id_rsa.pub',
        'command': 'hostname'

    }



@pytest.mark.skipif(not Shell.ssh_enabled(), reason="SSH is not enabled")
@pytest.mark.skipif(github_action, reason='GitHub Runner uses Azure and Azure does not have an ssh key set up!')
@pytest.mark.incremental
class TestSsh:

    def ssh(self, processors=1):
        StopWatch.start(f"total p={processors} c=1")
        r = Host.ssh(hosts,
                     command="hostname",
                     processors=processors)
        StopWatch.stop(f"total p={processors} c=1")
        StopWatch.status(f"total p={processors} c=1", r[0]["success"])

        return r

    def test_ssh_processors(self):

        print()
        for processors in range(1, len(hosts)):
            print("Processors:", processors)
            results = self.ssh(processors=processors)
            print(Printer.write(results))
            for result in results:
                if "denied (publickey)" in result["stderr"].decode():
                    pytest.skip("ssh test cannot proceed because ssh-copy-id not yet "
                                "done.")
                assert result["success"]

    #
    # only works if you have root, so not suitable
    #
    # def test_multi_ping(self):
    #     ping = MultiPing(hosts)
    #     responses, no_responses = ping(hosts, timeout=2, retry=1)

    def test_benchmark(self):
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)
