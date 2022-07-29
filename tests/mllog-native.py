import logging
import time

import yaml

from cloudmesh.common.Shell import Shell
# MLCommons logging
from mlperf_logging import mllog

mlperf_logfile = "cloudmesh_mlperf_native.log"
Shell.rm(mlperf_logfile)

mllog.config(filename=mlperf_logfile)
mllogger = mllog.get_mllogger()
logger = logging.getLogger(__name__)

benchmark_config = """
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

data = yaml.safe_load(benchmark_config)
# mllogger.end(key=mllog.constants.RUN_START, value="Benchmark run started")

# Values extracted from cloudMaskConfig.yaml
mllogger.event(key=mllog.constants.SUBMISSION_BENCHMARK, value=data["benchmark"]['name'])
mllogger.event(key=mllog.constants.SUBMISSION_ORG, value=data["benchmark"]['organisation'])
mllogger.event(key=mllog.constants.SUBMISSION_DIVISION, value=data["benchmark"]['division'])
mllogger.event(key=mllog.constants.SUBMISSION_STATUS, value=data["benchmark"]['status'])
mllogger.event(key=mllog.constants.SUBMISSION_PLATFORM, value=data["benchmark"]['platform'])
mllogger.start(key=mllog.constants.INIT_START)

mllogger.event(key='number_of_ranks', value=1)
mllogger.event(key='number_of_nodes', value=1)
mllogger.event(key='accelerators_per_node', value=1)
mllogger.end(key=mllog.constants.INIT_STOP)

# Training
start = time.time()
mllogger.event(key=mllog.constants.EVAL_START, value="Start Taining")
mllogger.event(key=mllog.constants.EVAL_STOP, value="Stop Training")
diff = time.time() - start

# Inference
start = time.time()
mllogger.event(key=mllog.constants.EVAL_START, value="Start Inference")
mllogger.event(key=mllog.constants.EVAL_STOP, value="Stop Inference")

mllogger.end(key=mllog.constants.RUN_STOP, value="Benchmark run finished", metadata={'status': 'success'})
