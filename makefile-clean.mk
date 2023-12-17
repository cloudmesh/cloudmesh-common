clean:
	$(call banner, "CLEAN")
	rm -rf *.egg-info
	rm -rf *.eggs
	rm -rf docs/build
	rm -rf build
	rm -rf dist
	rm -rf .tox
	rm -rf .tmp
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
