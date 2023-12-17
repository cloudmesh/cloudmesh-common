###############################################################
# pytest -v --capture=no tests/test_ping.py
# pytest -v  tests/test_ping.py
# pytest -v --capture=no  tests/test_ping..py::Test_ping::<METHODNAME>
###############################################################

import sys

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import HEADING

Benchmark.debug()

cloud = "local"

# https://github.com/actions/runner-images/issues/1519 ping does not work in github runner so we skip it.
import os
from cloudmesh.common.util import str_bool
github_action = str_bool(os.getenv('GITHUB_ACTIONS', 'false'))

# multiping only works if you have root, so we can not use it
# from multiping import MultiPing

hosts = ['127.0.0.1',
         'localhost']
other_hosts = [
         'www.pbs.org',
         'www.github.com',
         'www.redhat.com',
         'www.openstack.org',
         'www.bbc.com',
         'www.ec2instances.info',
         'aws.amazon.com']


@pytest.mark.incremental
@pytest.mark.skipif(github_action, reason='GitHub Runner uses Azure and Azure disables ping. :( Too bad!')
class Test_ping:

    def ping(self, processors=1):
        StopWatch.start(f"total p={processors} c=1")
        r = Host.ping(hosts, processors=processors, count=1)
        StopWatch.stop(f"total p={processors} c=1")
        StopWatch.status(f"total p={processors} c=1", r[0]['success'])

        return r

    def test_internal_ping(self):
        HEADING()
        StopWatch.start("total _ping")

        for host in hosts:
            location = {
                'ip': host,
                'count': 1,
            }

            StopWatch.start(f"ping {host}")
            result = Host._ping(location)
            StopWatch.stop(f"ping {host}")
            StopWatch.status(f"ping {host}", result['success'])

            StopWatch.stop("total _ping")
            StopWatch.status("total _ping", True)

            if b'Access denied' in result['stdout'] and sys.platform == "win32":
                print("ERROR: This test must be run in an administrative "
                      "terminal")
            assert result['success']

    def test_ping_processor(self):
        HEADING()
        print()
        print (hosts)
        for processors in range(1, len(hosts)):
            print("Processors:", processors)
            results = self.ping(processors=processors)
            print(Printer.write(results,
                                order=['host',
                                       'success',
                                       'max',
                                       'min',
                                       'stddev']
                                ))
            for result in results:
                assert result['success']

    #
    # only works if you have root, so not suitable
    #
    # def test_multi_ping(self):
    #     ping = MultiPing(hosts)
    #     responses, no_responses = ping(hosts, timeout=2, retry=1)

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag=cloud)
