#!/usr/bin/env python
"""tag-rm

Usage:
  github-tag-rm VERSIONS [--dryrun]

Options:
  -h --help       Show this help message and exit.
  --dryrun        Perform a dry run without actually removing tags.

Arguments:
  VERSIONS        Space-separated list of Git tags to be removed.

Description:
  The 'github-tag-rm' script removes specified Git tags locally and pushes the deletion to the remote repository.

Examples:
  tag-rm v1.0 v2.0 --dryrun
  tag-rm v1.1

"""

import os

from cloudmesh.common.parameter import Parameter
from docopt import docopt
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell


def main():
    """
    Main entry point for the tag-rm script.

    Parses command-line arguments, identifies and removes specified Git tags.

    """
    arguments = docopt(__doc__)
    tags = Parameter.expand(arguments["VERSIONS"])

    found = Shell.run("git tag").strip().splitlines()

    for tag in tags:
        if tag in found:
            print(f"Removing tag {tag}")

            script = [
                f"git tag -d {tag}",
                f"git push origin :refs/tags/{tag}"
            ]
            if arguments["--dryrun"]:
                print("  " + '\n  '.join(script))
            else:
                try:
                    for line in script:
                        os.system(line)
                    Console.ok(f"{tag} deleted")
                except:
                    Console.error("Deletion failed")
        else:
            Console.error(f"{tag} does not exist")


if __name__ == '__main__':
    main()

# alternative approach
# git push --delete origin $1
# git tag -d $1
