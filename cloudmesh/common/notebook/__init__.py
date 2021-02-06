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
