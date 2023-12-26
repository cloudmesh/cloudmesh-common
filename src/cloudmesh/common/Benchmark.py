import inspect
import os
from pprint import pprint

import yaml
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables


# pylint: disable=C0103
# noinspection PyPep8Naming
class Benchmark(object):
    """A utility class for benchmarking code execution and generating benchmark-related information.

    Attributes:
        None

    Methods:
        - debug(): Sets the CMS shell variables for trace, debug, and verbosity.
        - name(with_class=False): Retrieves the name of the calling method with an option to include the class name.
        - Start(status=True): Starts a timer associated with the calling method's name.
        - Status(value=True): Prints the status of a timer associated with the calling method's name.
        - Stop(): Stops a timer associated with the calling method's name.
        - print(sysinfo=True, csv=True, tag=None, node=None, user=None): Prints benchmark information with all timers.
        - yaml(path, n): Creates a Cloudmesh service YAML test file with specified attributes.
        - file(path, n): Creates a file of a given size in binary megabytes and returns the size in megabytes.

    Note:
        This class relies on the StopWatch class for timer functionality.
    """

    @staticmethod
    def debug():
        """Sets the CMS shell variables for trace, debug, and verbosity.
        The values will be

            trace = True
            debug = True
            verbose = 10

        Usage:
            Benchmark.debug()
        """
        variables = Variables()
        variables["trace"] = True
        variables["debug"] = True
        variables["verbose"] = 10

    @staticmethod
    def name(with_class=False):
        """Retrieves the name of the calling method with an option to include the class name.

        Args:
            with_class (bool): If True, includes the class name in the method name.

        Returns:
            str: The name of the calling method.
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
        """Starts a timer associated with the calling method's name.

        Args:
            status (bool): If True, starts the timer with the status.

        Usage:
        Benchmark.Start()
        """
        StopWatch.start(Benchmark.name(with_class=True))

    @staticmethod
    def Status(value=True):
        """gives the status of  a timer while using the name of the calling method

        Args:
            value (boolean): if true adds the class

        Returns:
            None

        Usage:
            Benchmark.Status()
        """
        StopWatch.status(Benchmark.name(with_class=True), value)

    @staticmethod
    def Stop():
        """Stops a timer associated with the calling method's name.

        Usage:
            Benchmark.Stop()
        """
        StopWatch.stop(Benchmark.name(with_class=True))
        StopWatch.status(Benchmark.name(with_class=True), True)

    @staticmethod
    def print(
        sysinfo=True,
        csv=True,
        tag=None,
        node=None,
        user=None,
    ):
        """prints the benchmark information with all timers

        Args:
            sysinfo (boolean): if true, prints the system information
            csv (boolean): if true also prints the csv data
            tag (str): the tage to be used
            node (str): the node name to be used
            user (str): the ser to be used

        Returns:
            None
        """
        StopWatch.start("benchmark_start_stop")
        StopWatch.stop("benchmark_start_stop")
        StopWatch.benchmark(sysinfo=sysinfo, csv=csv, tag=tag, user=user, node=node)

    @staticmethod
    def yaml(path, n):
        """Creates a Cloudmesh service YAML test file with specified number of services.

        Args:
            path (str): The path for the YAML file.
            n (int): Number of services to be included in the YAML file.

        Returns:
            None

        Usage:
            Benchmark.yaml("./example.yaml", 10)
        """
        cm = {"cloudmesh": {}}
        for i in range(0, n):
            cm["cloudmesh"][f"service{i}"] = {"attribute": f"service{i}"}
        pprint(cm)
        location = path_expand(path)

        with open(location, "w") as yaml_file:
            yaml.dump(cm, yaml_file, default_flow_style=False)

    # noinspection SpellCheckingInspection
    @staticmethod
    def file(path, n):
        """Creates a file of a given size in binary megabytes and returns the size in megabytes.

        Args:
            path (str): The filename and path for the created file.
            n (int): The size in binary megabytes.

        Returns:
            float: Size of the created file in megabytes.

        Usage:
            s = Benchmark.file("./example.txt", 2)
            print(s)
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

        return int(s / 1048576.0)
