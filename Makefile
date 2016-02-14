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
	@flake8 mattermost_bot --exclude=mattermost_bot/settings.py

.PHONY: release
# target: release - Release app into PyPi
release: clean
	@python setup.py register sdist upload --sign
	@python setup.py bdist_wheel upload --sign

sdist: clean
	@python setup.py sdist
	@ls -l dist

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile | sed -e 's/^# target: //g'
