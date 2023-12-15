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
