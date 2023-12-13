package=sys
UNAME=$(shell uname)
VERSION=`head -1 VERSION`

.PHONY: conda

define banner
	@echo
	@echo "############################################################"
	@echo "# $(1) "
	@echo "############################################################"
endef

source:
	$(call banner, "Install cloudmesh-common")
	pip install -e . -U

flake8:
	cd ..; flake8 --max-line-length 124 --ignore=E722 cloudmesh-$(package)/cloudmesh
	cd ..; flake8 --max-line-length 124 --ignore=E722 cloudmesh-$(package)/tests

pylint:
	cd ..; pylint --rcfile=cloudmesh-$(package)/.pylintrc  cloudmesh-$(package)/cloudmesh
	cd ..; pylint --rcfile=cloudmesh-$(package)/.pylintrc  --disable=F0010 cloudmesh-$(package)/tests

requirements:
	echo "# cloudmesh-common requirements"> tmp.txt
	#echo "cloudmesh-common" > tmp.txt
	#echo "cloudmesh-cmd5" >> tmp.txt
	# pip-compile setup.py
	cat requirements.txt >> tmp.txt
	mv tmp.txt requirements.txt
	-git commit -m "update requirements" requirements.txt
	-git push

test:
	pytest -v --html=.report.html
	open .report.html

dtest:
	pytest -v --capture=no

clean:
	$(call banner, "CLEAN")
	rm -rf *.zip
	rm -rf *.egg-info
	rm -rf *.eggs
	rm -rf docs/build
	rm -rf build
	rm -rf dist
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
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

patch: clean twine
	$(call banner, "patch")
	cms bumpversion patch
	python setup.py sdist bdist_wheel
	git push origin main --tags
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
	python setup.py sdist bdist_wheel
	twine check dist/*
	twine upload --repository pypi dist/*
	$(call banner, "install")
	@cat VERSION
	@echo

upload:
	twine check dist/*
	twine upload dist/*

pip:
	pip install --index-url https://test.pypi.org/simple/ cloudmesh-$(package) -U

log:
	$(call banner, log)
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push
