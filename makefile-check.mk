
flake8:
	cd ..; flake8 --max-line-length 124 --ignore=E722 cloudmesh-$(package)/cloudmesh
	cd ..; flake8 --max-line-length 124 --ignore=E722 cloudmesh-$(package)/tests

pylint:
	cd ..; pylint --rcfile=cloudmesh-$(package)/.pylintrc  cloudmesh-$(package)/cloudmesh
	cd ..; pylint --rcfile=cloudmesh-$(package)/.pylintrc  --disable=F0010 cloudmesh-$(package)/tests
