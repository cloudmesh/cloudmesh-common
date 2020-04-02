###############################################################
# pytest -v --capture=no tests/ssh/test_ssh.py
# pytest -v  tests/tests/ssh/test_ssh.py
# pytest -v --capture=no  tests/ssh/test_ssh..py::Test_name::<METHODNAME>
###############################################################

import os

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Host import Host
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch

Benchmark.debug()

cloud = "local"
# multiping only works if you have root, so we can not use it
# from multiping import MultiPing

thishost = Shell.execute('hostname')

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


@pytest.mark.incremental
class TestSsh:

    def ssh(self, processors=1):
        StopWatch.start(f"total p={processors} c=1")
        r = Host.ssh(hosts,
                     command="hostname",
                     processors=processors)
        StopWatch.stop(f"total p={processors} c=1")

        return r

    def test_internal_ssh(self):
        print()
        StopWatch.start("total _ssh")

        for host in hosts:
            location = {
                'host': host,
                'username': os.environ['USER'],
                'key': '~/.ssh/id_rsa.pub',
                'command': 'uname -a'

            }

            StopWatch.start(f"ssh {host}")
            result = Host._ssh(location)
            StopWatch.stop(f"ssh {host}")

            StopWatch.stop("total _ssh")

            assert result.success

    def test_ssh_processors(self):

        print()
        for processors in range(1, len(hosts)):
            print("Processors:", processors)
            results = self.ssh(processors=processors)
            # print(Printer.write(results))
            for result in results:
                assert result.success

    #
    # only works if you have root, so not suitable
    #
    # def test_multi_ping(self):
    #     ping = MultiPing(hosts)
    #     responses, no_responses = ping(hosts, timeout=2, retry=1)

    def test_benchmark(self):
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)
