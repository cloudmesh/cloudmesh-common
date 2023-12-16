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

ndist:
	pip install -q build
	python -m build

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
