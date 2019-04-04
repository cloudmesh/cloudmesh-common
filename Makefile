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

dist:
	python setup.py sdist bdist_wheel
	twine check dist/*

patch: clean
	$(call banner, patch to testpypi)
	bumpversion --allow-dirty patch
	python setup.py sdist bdist_wheel
	git push origin master --tags
	twine check dist/*
	twine upload --repository testpypi https://test.pypi.org/legacy/ dist/*

release: clean dist
	$(call banner, release to pypi)
	bumpversion release
	python setup.py sdist bdist_wheel
	git push origin master --tags
	twine check dist/*
	twine upload --repository testpypi https://test.pypi.org/legacy/ dist/*


upload:
	twine check dist/*
	twine upload dist/*

pip: patch
	pip install --index-url https://test.pypi.org/simple/ \
	    --extra-index-url https://pypi.org/simple cloudmesh-$(package)

log:
	$(call banner, log)
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push

# bump:
#	git checkout master
#	git pull
#	tox
#	python setup.py sdist bdist_wheel upload
#	bumpversion --no-tag patch
#	git push origin master --tags


# API_JSON=$(printf '{"tag_name": "v%s","target_commitish": "master","name": "v%s","body": "Release of version %s","draft": false,"prerelease": false}' $VERSION $VERSION $VERSION)
# curl --data "$API_JSON" https://api.github.com/repos/:owner/:repository/releases?access_token=:access_token
