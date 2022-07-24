import time

import yaml

from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch

Shell.rm("cloudmesh_mllog.log")
StopWatch.clear()
# this code is in a manula README-mlcommons.md

# define the organization

config = """
benchmark:
  name: Earthquake
  user: Gregor von Laszewski
  e-mail: laszewski@gmail.com
  organisation:  University of Virginia
  division: BII
  status: success
  platform: rivanna
  badkey: ignored
""".strip()

submitter = yaml.safe_load(config)

# activate the MLcommons logger
StopWatch.activate_mllog()

StopWatch.organization_mllog(**submitter)

# save an event with a value
StopWatch.event("test", values="1")

# save a dict in an event
data = {"a": 1}
StopWatch.event("stopwtch dict event", values=data)

# start a timer
StopWatch.start("stopwatch sleep")

# do some work
time.sleep(0.1)

# stop the timer
StopWatch.stop("stopwatch sleep")

# print the table
StopWatch.benchmark(tag="Earthquake", node="summit", user="Gregor", version="0.1")
