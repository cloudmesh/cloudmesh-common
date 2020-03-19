import inspect
import os
from pprint import pprint

import yaml
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from pathlib import Path


# noinspection PyPep8Naming
class Benchmark(object):

    @staticmethod
    def debug():
        """
        sets the cms shell variables

          trace = True
          debug = True
          verbose = 10

        """
        variables = Variables()
        variables["trace"] = True
        variables["debug"] = True
        variables["verbose"] = 10

    @staticmethod
    def name(with_class=False):
        """
        name of the calling method

        :return: the name
        """
        frame = inspect.getouterframes(inspect.currentframe())
        method = frame[2][3]

        # pprint (frame[2])

        if with_class:
            classname = os.path.basename(frame[2].filename).replace(".py", "")
            method = classname + "/" + method
        return method

    @staticmethod
    def Start(status=True):
        """
        starts a timer while using the name of the calling method
        """
        StopWatch.start(Benchmark.name(with_class=True))

    @staticmethod
    def Status(value=True):
        """
        starts a timer while using the name of the calling method
        """
        StopWatch.status(Benchmark.name(with_class=True), value)

    @staticmethod
    def Stop():
        """
        stops a timer while using the name of the calling method
        """
        StopWatch.stop(Benchmark.name(with_class=True))
        StopWatch.status(Benchmark.name(with_class=True), True)

    @staticmethod
    def print(sysinfo=True, csv=True, tag=None):
        """
        prints the benchmark information with all timers
        """
        StopWatch.start("benchmark_start_stop")
        StopWatch.stop("benchmark_start_stop")

        StopWatch.benchmark(sysinfo=sysinfo, csv=csv, tag=tag)

    @staticmethod
    def yaml(path, n):
        """
        creates a cloudmesh service yaml test file

        Example: BenchmarkFiles.yaml("./t.yaml", 10)

        :param path: the path
        :param n: number of services
        :return:
        """
        cm = {
            "cloudmesh": {}
        }
        for i in range(0, n):
            cm["cloudmesh"][f"service{i}"] = {
                "attribute": f"service{i}"
            }
        pprint(cm)
        location = path_expand(path)

        with open(location, 'w') as yaml_file:
            yaml.dump(cm, yaml_file, default_flow_style=False)

    # noinspection SpellCheckingInspection
    @staticmethod
    def file(path, n):
        """
        create a file of given size in MB, the MB here is in binary not SI
        units.
        e.g. 1,048,576 Bytes

        Example: s = BenchmarkFiles.size("./sise.txt", 2)
                 print(s)

        :param path: the filename and path
        :type path: string
        :param n: the size in binary MB
        :type n: integer
        :return: size in MB
        :rtype: float
        """
        location = path_expand(path)
        size = 1048576 * n  # size in bytes
        with open(path, "wb") as f:
            f.write(os.urandom(size))

        s = os.path.getsize(location)
        # try:
        #    os.system(f"ls -lhs {location}")
        #    os.system(f"du -h {location}")
        # except:
        #    pass

        return s / 1048576.0
