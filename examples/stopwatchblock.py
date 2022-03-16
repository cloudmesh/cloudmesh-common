from cloudmesh.common.StopWatch import StopWatchBlock
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import readfile


import time

data = {"step": "value"}

StopWatch.event("event-start")

with StopWatchBlock("total"):
    time.sleep(1.0)

with StopWatchBlock("dict", data=data):
    time.sleep(1.0)
    data["step"] = 1

with StopWatchBlock("file", data=data, log="a.log", mode="w"):
    time.sleep(1.0)
    data["step"] = 2

with StopWatchBlock("append", data=data, log="a.log", mode="a"):
    time.sleep(1.0)
    data["step"] = 3

content = readfile ("a.log")
print (79*"=")
print (content.strip())
print (79*"=")


StopWatch.event("event-stop")
    
StopWatch.benchmark(sysinfo=False, user="gregor", node="computer",
                    attributes=["timer", "status", "time", "start"]
)


