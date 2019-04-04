package=common
UNAME=$(shell uname)
export ROOT_DIR=${PWD}/cloudmesh/rest/server
VERSION=`head -1 VERSION`

define banner
	@echo
	@echo "############################################################"
	@echo $(1)
	@echo "############################################################"
endef

source:
	$(call banner, "Install cloudmesh-sommon")
	pip install -e . -U 

test:
	pytest -v 

dtest:
	pytest -v --capture=no

nosetests:
	nosetests -v --nocapture tests/test_mongo.py


clean:
	$(call banner, "CLEAN")
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


twine:
	pip install -U twine

dist: clean
	$(call banner, $VERSION)
	python setup.py sdist bdist_wheel
	twine check dist/*

upload_test: twine dist
	twine upload --repository testpypi https://test.pypi.org/legacy/ dist/*

log:
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push

register: dist
	$(call banner, $VERSION)
	twine register dist/cloudmesh-$(package)-$(VERSION)-py2.py3-none-any.whl

upload: clean dist
	twine upload dist/*

#
# GIT
#

tag:
	touch README.rst
	git tag $(VERSION)
	git commit -a -m "$(VERSION)"
	git push



pip: upload_test
	pip install --index-url https://test.pypi.org/simple/ \
	    --extra-index-url https://pypi.org/simple cloudmesh-$(package)


bump:
	git checkout master
	git pull
	tox
	bumpversion release
	python setup.py sdist bdist_wheel upload
	bumpversion --no-tag patch
	git push origin master --tags