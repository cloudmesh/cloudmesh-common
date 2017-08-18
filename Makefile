package=common
UNAME=$(shell uname)
export ROOT_DIR=${PWD}/cloudmesh/rest/server
VERSION=`head -1 VERSION`

define banner
	@echo
	@echo "###################################"
	@echo $(1)
	@echo "###################################"
endef

ifeq ($(UNAME),Darwin)
define terminal
	osascript -e 'tell application "Terminal" to do script "$(1)"'
endef
endif
ifeq ($(UNAME),Linux)
define terminal
	echo "Linux not yet supported, fix me"
endef
endif
ifeq ($(UNAME),Windows)
define terminal
	echo "Windows not yet supported, fix me"
endef
endif

source:
	python setup.py install

test:
	pytest -v 

dtest:
	pytest -v --capture=no

nosetests:
	nosetests -v --nocapture tests/test_mongo.py


clean:
	rm -rf *.zip
	rm -rf *.egg-info
	rm -rf *.eggs
	rm -rf docs/build
	rm -rf build
	rm -rf dist
	find . -name '__pycache__' -delete
	find . -name '*.pyc' -delete
	rm -rf .tox
	rm -f *.whl


######################################################################
# PYPI
######################################################################

dist: clean
	@echo "######################################"
	@echo "# $(VERSION)"
	@echo "######################################"
	python setup.py sdist --formats=gztar,zip
	python setup.py bdist
	python setup.py bdist_wheel

upload_test:
	python setup.py	 sdist bdist bdist_wheel upload -r https://testpypi.python.org/pypi

log:
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push

register: dist
	@echo "######################################"
	@echo "# $(VERSION)"
	@echo "######################################"
	twine register dist/cloudmesh.$(package)-$(VERSION)-py2.py3-none-any.whl
	#twine register dist/cloudmesh.$(package)-$(VERSION).macosx-10.12-x86_64.tar.gz

upload: dist
	twine upload dist/*

#
# GIT
#

tag:
	touch README.rst
	git tag $(VERSION)
	git commit -a -m "$(VERSION)"
	git push
