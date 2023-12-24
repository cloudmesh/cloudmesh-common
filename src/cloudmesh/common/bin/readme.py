#!/usr/bin/env python

import glob
import os
import sys
import textwrap

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile

def generate_readme(repo, command):
    """
    Generate a README.md file based on a template (README-source.md) and dynamic content.

    Args:
        repo (str): The name of the GitHub repository.
        command (str): The command for which the README is generated.

    Note:
        This script is designed to be executed with two command-line arguments:
        - sys.argv[1]: The name of the GitHub repository.
        - sys.argv[2]: The command for which the README is generated.

        The README.md page is automatically generated, do not edit it directly.
        To modify, change the content in README-source.md. Curly brackets must use two in README-source.md.
    """
    warning = """
    > **Note:** The README.md page is automatically generated, do not edit it.
    > To modify, change the content in
    > <https://github.com/cloudmesh/{repo}/blob/main/README-source.md>
    > Curly brackets must use two in README-source.md.
    """

    # Find icons
    icons = """
    [![image](https://img.shields.io/pypi/v/{repo}.svg)](https://pypi.org/project/{repo}/)
    [![Python](https://img.shields.io/pypi/pyversions/{repo}.svg)](https://pypi.python.org/pypi/{repo})
    [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/cloudmesh/{repo}/blob/main/LICENSE)
    [![Format](https://img.shields.io/pypi/format/{repo}.svg)](https://pypi.python.org/pypi/{repo})
    [![Status](https://img.shields.io/pypi/status/{repo}.svg)](https://pypi.python.org/pypi/{repo})
    [![Travis](https://travis-ci.com/cloudmesh/{repo}.svg?branch=main)](https://travis-ci.com/cloudmesh/{repo})
    """

    # Find Tests
    tests = sorted(glob.glob('tests/test_**.py'))
    links = [
        "[{name}]({x})".format(x=x, name=os.path.basename(x).replace('.py', '')) for
        x in tests]

    tests = " * " + "\n * ".join(links)

    # Get manual
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

    # Create README
    source = readfile("README-source.md")
    readme = source.format(**locals())
    writefile("README.md", readme)

# Command-line execution
if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else ""
    command = sys.argv[2] if len(sys.argv) > 2 else ""
    generate_readme(repo, command)
