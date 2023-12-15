test:
	pytest -v --html=.report.html
	open .report.html

dtest:
	pytest -v --capture=no
