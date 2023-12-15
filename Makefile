package=common
UNAME=$(shell uname)
VERSION=`head -1 VERSION`

include makefile-banner.mk

source:
	$(call banner, "Install cloudmesh-${package}")
	pip install -e . -U

include makefile-test.mk

include makefile-clean.mk

include makefile-check.mk

include makefile-pypi.mk
