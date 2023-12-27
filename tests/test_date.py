###############################################################
# pytest -v --capture=no  tests/test_date.py
# pytest -v --capture=no  tests/test_date..py::test_date.test_001
# pytest -v tests/test_date.py
###############################################################

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common.DateTime import DateTime
import datetime


# ./cloudmesh-cc/tests/test_199_workflow_clean.py:from cloudmesh.common.DateTime import DateTime
# ./cloudmesh-cc/src/cloudmesh/cc/labelmaker.py:from cloudmesh.common.DateTime import DateTime
# ./cloudmesh-cc/src/cloudmesh/cc/workflow.py:from cloudmesh.common.DateTime import DateTime
# ./cloudmesh-multipass/src/cloudmesh/multipass/Provider.py:from cloudmesh.common.DateTime import DateTime
# ./cloudmesh-common/tests/test_date.py:from cloudmesh.common.DateTime import DateTime
# ./cloudmesh-common/src/cloudmesh/common/Host.py:from cloudmesh.common.DateTime import DateTime
# ./cloudmesh-common/src/cloudmesh/common/systeminfo.py:from cloudmesh.common.DateTime import DateTime
# ./cloudmesh-common/src/cloudmesh/common/StopWatch.py:from cloudmesh.common.DateTime import DateTime
# ./cloudmesh-common/src/cloudmesh/common/Printer.py:from cloudmesh.common.DateTime import DateTime


class TestDateTime:
    def test_now(self):
        HEADING()
        now = DateTime.now()
        print(now)
        assert isinstance(now, str)

    def test_utc_now(self):
        HEADING()
        utc_now = DateTime.utc_now()
        print(utc_now)
        assert isinstance(utc_now, str)

    def test_natural(self):
        HEADING()
        time = "2019-08-03 21:34:14"
        natural_time = DateTime.natural(time)
        print(natural_time)
        assert isinstance(natural_time, str)

    def test_datetime(self):
        HEADING()
        time = "2019-08-03 21:34:14"
        d = DateTime.datetime(time)
        print(d)
        print(type(d))
        assert isinstance(d, datetime.datetime)

    def test_humanize(self):
        HEADING()
        time = "2019-08-03 21:34:14"
        humanized_time = DateTime.humanize(time)
        print(humanized_time)
        assert isinstance(humanized_time, str)

    def test_utc(self):
        HEADING()
        time = "2019-08-03 21:34:14"
        utc_time = DateTime.utc(time)
        print(utc_time)  # Print utc_time before assert
        assert isinstance(utc_time, str)

    # class failed:

    def test_local(self):
        HEADING()
        time = "2019-08-03 21:34:14"
        local_time = DateTime.local(time)
        print(local_time)  # Print local_time before assert
        assert isinstance(local_time, str)

    def test_string(self):
        HEADING()
        time = "2019-08-03 21:34:14"
        string_time = DateTime.string(time)
        print(string_time)
        assert isinstance(string_time, str)

    def test_delta(self):
        HEADING()
        delta = DateTime.delta(1)
        print(delta)
        print(type(delta))
        assert delta == datetime.timedelta(seconds=1)
        assert str(delta) == "0:00:01"

    def test_words(self):
        HEADING()
        time = "2019-08-03 21:34:14"
        words = DateTime.words(time)
        print(words)
        assert isinstance(words, str)

    def test_print(self):
        HEADING()

        start = DateTime.datetime(DateTime.now())

        stop = start + DateTime.delta(2)

        print("START", start)
        print("STOP", stop)
        print("HUMANIZE STOP", DateTime.humanize(stop - start))
        print("LOCAL", DateTime.local(start))
        print("UTC", DateTime.utc(start))
        print("NATURAL", DateTime.natural(start))
        print("WORDS", DateTime.words(start))
        print("TIMEZONE", DateTime.timezone)

        # print("CONVERT", DateTime.local("2019-08-03 20:48:27.205442 UTC"))
        """
        START 2019-08-03 21:34:14.019147
        STOP 2019-08-03 21:34:15.019150
        HUMANIZE STOP a second ago
        LOCAL 2019-08-03 17:34:14 EST
        UTC 2019-08-03 21:34:14.019147 UTC
        NATURAL 2019-08-03 21:34:14.019147 UTC
        WORDS Sat 6 Aug 2019, 21:34:14 UTC
        TIMEZONE EST
        """
