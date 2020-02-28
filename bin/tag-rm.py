# !/usr/bin/env python
"""tag-rm

Usage:
  tag-rm VERSIONS [--dryrun]

"""
import os

from cloudmesh.common.parameter import Parameter
from docopt import docopt
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell


def main():
    arguments = docopt(__doc__)
    tags = Parameter.expand(arguments["VERSIONS"])


    found = Shell.run("git tag").strip().splitlines()

    # print (found)

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
                    Console.error ("Deletion failed")
        else:
            Console.error(f"{tag} does not exist")

if __name__ == '__main__':
    main()

# alternative approach
# git push --delete origin $1
# git tag -d $1
