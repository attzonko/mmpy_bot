.PHONY: clean
# target: clean - Clean temporary files
clean: clean-build clean-pyc

clear: clean
	@true

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

.PHONY: pep8
# target: pep8 - Check code for pep8 rules
pep8:
	@flake8 mmpy_bot --exclude=mmpy_bot/settings.py

.PHONY: release
# target: release - Release app into PyPi
release: clean
	@python setup.py sdist bdist_wheel
	@twine upload dist/*

.PHONY: run
# target: run - Run bot
run:
	mmpy_bot

.PHONY: sphinx
# target: sphinx - Make app docs
sphinx:
	@rm -rf ./docs/.build/html/
	@cd docs && sphinx-build -b html -d .build/doctrees . .build/html
	@xdg-open docs/.build/html/index.html >& /dev/null || open docs/.build/html/index.html >& /dev/null || true

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile | sed -e 's/^# target: //g'
