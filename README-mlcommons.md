# StopWatch for MLCommons

Augmentation of codes for consideration into the inclusion of the science benchmarks, must use the

* [MLCommons Logging Library](https://github.com/mlcommons/logging)

However, this library is ment for submisison to MLcommons and does not produce results that are easily readable. 

We have used for a long time Clousmeh StopWatch that produces a nice table. Recently we have augmented 
it so that it can also create automatically mlcommons events. To leverage this feature we showcase
here som simple examples of this integartion. The libarry is located at

* [StopWatch](https://github.com/cloudmesh/cloudmesh-common/blob/main/cloudmesh/common/StopWatch.py) from [cloudmesh-common](https://github.com/cloudmesh/cloudmesh-common)

To integarte is you can use

    git clone https://github.com/mlperf/logging.git mlperf-logging
    cd mlperf-logging
    pip install -e .
    pip install cloudmesh-common

A [pytest](https://github.com/cloudmesh/cloudmesh-common/blob/main/tests/test_stopwatch_mllog.py) documents its use



The elementary functions are

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
    StopWatch.benchmark(sysinfo=False, tag="Earthquake", node="summit", user="Gregor", version="0.1")

The output will be

| Name                | Status   |   Time |   Sum | Start               | tag        | msg   | Node   | User   | OS    |   Version |
| ---------------------| ----------| --------| -------| ---------------------| ------------| -------| --------| --------| -------| -----------|
| test                | ok       |    0   |   0   | 2022-07-23 14:14:58 | Earthquake |       | summit | Gregor | Linux |       0.1 |
| stopwtch dict event | ok       |    0   |   0   | 2022-07-23 14:14:58 | Earthquake |       | summit | Gregor | Linux |       0.1 |
| stopwatch sleep     | ok       |    0.1 |   0.1 | 2022-07-23 14:14:58 | Earthquake |       | summit | Gregor | Linux |       0.1 |

    # csv,timer,status,time,sum,start,tag,msg,uname.node,user,uname.system,platform.version
    # csv,test,ok,0.0,0.0,2022-07-23 14:14:58,Earthquake,None,summit,Gregor,Linux,0.1
    # csv,stopwtch dict event,ok,0.0,0.0,2022-07-23 14:14:58,Earthquake,None,summit,Gregor,Linux,0.1
    # csv,stopwatch sleep,ok,0.1,0.1,2022-07-23 14:14:58,Earthquake,None,summit,Gregor,Linux,0.1

To enable also a system information you can set syinfo to True and you will get a table similar to 

| Attribute           | Value                                                            |
|---------------------| ------------------------------------------------------------------|
| BUG_REPORT_URL      | "https://bugs.launchpad.net/ubuntu/"                             |
| DISTRIB_CODENAME    | focal                                                            |
| DISTRIB_DESCRIPTION | "Ubuntu 20.04.4 LTS"                                             |
| DISTRIB_ID          | Ubuntu                                                           |
| DISTRIB_RELEASE     | 20.04                                                            |
| HOME_URL            | "https://www.ubuntu.com/"                                        |
| ID                  | ubuntu                                                           |
| ID_LIKE             | debian                                                           |
| NAME                | "Ubuntu"                                                         |
| PRETTY_NAME         | "Ubuntu 20.04.4 LTS"                                             |
| PRIVACY_POLICY_URL  | "https://www.ubuntu.com/legal/terms-and-policies/privacy-policy" |
| SUPPORT_URL         | "https://help.ubuntu.com/"                                       |
| UBUNTU_CODENAME     | focal                                                            |
| VERSION             | "20.04.4 LTS (Focal Fossa)"                                      |
| VERSION_CODENAME    | focal                                                            |
| VERSION_ID          | "20.04"                                                          |
| cpu                 | AMD Ryzen 9 5950X 16-Core Processor                              |
| cpu_cores           | 16                                                               |
| cpu_count           | 32                                                               |
| cpu_threads         | 32                                                               |
| date                | 2022-07-23 14:14:58.264322                                       |
| frequency           | scpufreq(current=2309.9574374999997, min=2200.0, max=3400.0)     |
| mem.active          | 12.8 GiB                                                         |
| mem.available       | 111.1 GiB                                                        |
| mem.free            | 70.2 GiB                                                         |
| mem.inactive        | 37.9 GiB                                                         |
| mem.percent         | 11.6 %                                                           |
| mem.total           | 125.7 GiB                                                        |
| mem.used            | 12.8 GiB                                                         |
| platform.version    | #44~20.04.1-Ubuntu SMP Fri Jun 24 13:27:29 UTC 2022              |
| python              | 3.10.5 (main, Jun  7 2022, 06:30:01) [GCC 9.4.0]                 |
| python.pip          | 22.1.2                                                           |
| python.version      | 3.10.5                                                           |
| sys.platform        | linux                                                            |
| uname.machine       | x86_64                                                           |
| uname.node          | summit                                                           |
| uname.processor     | x86_64                                                           |
| uname.release       | 5.15.0-41-generic                                                |
| uname.system        | Linux                                                            |
| uname.version       | #44~20.04.1-Ubuntu SMP Fri Jun 24 13:27:29 UTC 2022              |
| user                | Gregor                                                           |


More advanced features include blocks that wrap start and sop methods so you do not have to call the separately

    with StopWatchBlock("this is a block"):
        time.sleep(1.0)

    with StopWatchBlock("this is a block with data", data=data):
        time.sleep(1.0)
        data["step"] = 1


