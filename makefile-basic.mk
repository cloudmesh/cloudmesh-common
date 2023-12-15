UNAME=$(shell uname)
VERSION=`head -1 VERSION`

define banner
	@echo
	@echo "############################################################"
	@echo "# $(1) "
	@echo "############################################################"
endef

source:
	$(call banner, "Install cloudmesh-${package}")
	pip install -e . -U
