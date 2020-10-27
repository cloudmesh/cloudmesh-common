# !/usr/bin/env python

import glob
import os
import sys
import textwrap

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile

repo = sys.argv[1]
command = sys.argv[2]

warning = f"""
> **Note:** The README.md page is outomatically generated, do not edit it.
> To modify  change the content in
> <https://github.com/cloudmesh/{repo}/blob/main/README-source.md>
> Curley brackets must use two in README-source.md
"""
#
# Find icons
#

icons = f"""
[![image](https://img.shields.io/pypi/v/{repo}.svg)](https://pypi.org/project/{repo}/)
[![Python](https://img.shields.io/pypi/pyversions/{repo}.svg)](https://pypi.python.org/pypi/{repo})
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/cloudmesh/{repo}/blob/main/LICENSE)
[![Format](https://img.shields.io/pypi/format/{repo}.svg)](https://pypi.python.org/pypi/{repo})
[![Status](https://img.shields.io/pypi/status/{repo}.svg)](https://pypi.python.org/pypi/{repo})
[![Travis](https://travis-ci.com/cloudmesh/{repo}.svg?branch=main)](https://travis-ci.com/cloudmesh/{repo})
"""

#
# Find Tests
#
tests = sorted(glob.glob('tests/test_**.py'))
links = [
    "[{name}]({x})".format(x=x, name=os.path.basename(x).replace('.py', '')) for
    x in tests]

tests = " * " + "\n * ".join(links)

#
# get manual
#
if repo == "cloudmesh-installer":
    manual = Shell.run("cloudmesh-installer --help")
else:
    manual = Shell.run(f"cms help {command}")

man = []
start = False
for line in manual.splitlines():
    start = start or "Usage:" in line
    if start:
        if not line.startswith("Timer:"):
            man.append(line)
manual = textwrap.dedent('\n'.join(man)).strip()
manual = "```bash\n" + manual + "\n```\n"

#
# create readme
#
source = readfile("README-source.md")
readme = source.format(**locals())
writefile("README.md", readme)
