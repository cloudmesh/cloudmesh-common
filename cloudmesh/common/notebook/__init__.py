import os
import sys

#
# add user COLAB
#

IN_COLAB = 'google.colab' in sys.modules

if IN_COLAB:
    os.environ["USER"] = "COLAB"

#
# use full width of jupyter notebook windows
#
try:
    __IPYTHON__
    from IPython.core.display import display, HTML
    display(HTML("<style>.container { width:100% !important; }</style>"))

    from pprint import pprint  # noqa: F401

    from cloudmesh.common.util import banner

    banner("Cloudmesh")

except NameError:
    pass
