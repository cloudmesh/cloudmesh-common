UNAME=$(shell uname)
VERSION=`head -1 VERSION`

define banner
	@echo
	@echo "############################################################"
	@echo "# $(1) "
	@echo "############################################################"
endef

welcome:
	$(call banner, "Install ${package}")

source: welcome
	pip install -e . -U

##############################################################################
# CHECK
##############################################################################

flake8:
	cd ..; flake8 --max-line-length 124 --ignore=E722 $(package)/src/cloudmesh
	cd ..; flake8 --max-line-length 124 --ignore=E722 $(package)/tests

pylint:
	cd ..; pylint --rcfile=$(package)/.pylintrc  $(package)/src/cloudmesh
	cd ..; pylint --rcfile=$(package)/.pylintrc  --disable=F0010 $(package)/tests

##############################################################################
# CLEAN
##############################################################################

clean:
	$(call banner, "CLEAN")
	rm -rf *.egg-info
	rm -rf *.eggs
	rm -rf docs/build
	rm -rf build
	rm -rf dist
	rm -rf .tox
	rm -rf .tmp
	find . -type d -name '__pycache__' -exec rm -rf {} +

##############################################################################
# INFO
##############################################################################

info:
	@echo "================================================="
	@git remote show origin
	@echo "================================================="
	@git shortlog -sne --all
	@echo "================================================="

##############################################################################
# TEST
##############################################################################

test:
	pytest -v --html=.report.html
	open .report.html

dtest:
	pytest -v --capture=no

######################################################################
# PYPI
######################################################################

twine:
	pip install -U twine

.PHONY: dist

dist:
	pip install -q build
	python -m build
	twine check dist/*

local: welcome dist
	pip install dist/*.whl

local-force:
	pip install dist/*.whl --force-reinstall

patch: clean twine
	$(call banner, "patch")
	pip install -r requirements-dev.txt
	cms bumpversion patch
	@VERSION=$$(cat VERSION); \
		git commit -m "bump version ${VERSION}" .; git push
	pip install -q build
	python -m build
	twine check dist/*
	twine upload --repository testpypi  dist/*

minor: clean
	$(call banner, "minor")
	cms bumpversion minor
	@cat VERSION
	@echo

major: clean
	$(call banner, "major")
	cms bumpversion major
	@cat VERSION
	@echo

release: clean
	$(call banner, "release")
	git tag "v$(VERSION)"
	git push origin main --tags
	pip install -q build
	python -m build
	twine upload --repository pypi dist/*
	$(call banner, "install")
	@cat VERSION
	@echo

upload:
	twine check dist/*
	twine upload dist/*

pip:
	pip install --index-url https://test.pypi.org/simple/ $(package) -U

log:
	$(call banner, log)
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push
