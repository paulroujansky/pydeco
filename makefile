# Makefile for the 'pydeco' package.
#
# Author: Paul Roujansky <paul@roujansky.eu>
# Last Change: June 28, 2019
# URL: https://github.com/paulroujansky/pydeco

PACKAGE_NAME = pydeco
WORKON_HOME ?= $(HOME)/.virtualenvs
VIRTUAL_ENV ?= $(WORKON_HOME)/$(PACKAGE_NAME)
PATH := $(VIRTUAL_ENV)/bin:$(PATH)
MAKE := $(MAKE) --no-print-directory
CODESPELL_SKIPS ?= "*.html,*.fif,*.eve,*.gz,*.tgz,*.zip,*.mat,*.stc,*.label,*.w,*.bz2,*.annot,*.sulc,*.log,*.local-copy,*.orig_avg,*.inflated_avg,*.gii,*.pyc,*.doctree,*.pickle,*.inv,*.png,*.edf,*.touch,*.thickness,*.nofix,*.volume,*.defect_borders,*.mgh,lh.*,rh.*,COR-*,FreeSurferColorLUT.txt,*.examples,.xdebug_mris_calc,bad.segments,BadChannels,*.hist,empty_file,*.orig,*.js,*.map,*.ipynb,searchindex.dat,*.c"
CODESPELL_DIRS ?= pydeco/ doc/
SHELL = bash

default:
	@echo "Makefile for $(PACKAGE_NAME)"
	@echo
	@echo 'Usage:'
	@echo
	@echo '    make install    install the package in a virtual environment'
	@echo '    make reset      recreate the virtual environment'
	@echo '    make check      check coding style (PEP-8, PEP-257)'
	@echo '    make test       run the test suite, report coverage'
	@echo '    make tox        run the tests on all Python versions'
	@echo '    make readme     update usage in readme'
	@echo '    make docs       update documentation using Sphinx'
	@echo '    make publish    publish changes to GitHub/PyPI'
	@echo '    make clean      cleanup all temporary files'
	@echo

install:
	@test -d "$(VIRTUAL_ENV)" || mkdir -p "$(VIRTUAL_ENV)"
	@test -x "$(VIRTUAL_ENV)/bin/python" || virtualenv --quiet "$(VIRTUAL_ENV)"
	@test -x "$(VIRTUAL_ENV)/bin/pip" || easy_install pip
	@pip uninstall --yes $(PACKAGE_NAME) &>/dev/null || true
	@pip install --quiet --no-deps --ignore-installed .

reset:
	$(MAKE) clean
	rm -Rf "$(VIRTUAL_ENV)"
	$(MAKE) install

check: install
	@pip install --quiet --constraint=constraints.txt --requirement=requirements-checks.txt
	@flake8

test: install
	@pip install --quiet --constraint=constraints.txt --requirement=requirements-tests.txt
	@py.test --cov
	@coverage combine || true
	@coverage html

tox: install
	@pip install --quiet tox
	@tox

readme: install
	@pip install --quiet cogapp
	@cog.py -r README.rst

docs: readme
	@pip install --quiet sphinx
	@cd docs && sphinx-build -nb html -d build/doctrees . build/html

publish: install
	git push origin && git push --tags origin
	$(MAKE) clean
	pip install --quiet twine wheel
	python setup.py sdist bdist_wheel
	twine upload dist/*
	$(MAKE) clean

clean:
	@rm -Rf *.egg .cache .coverage .tox build dist docs/build htmlcov
	@find -depth -type d -name __pycache__ -exec rm -Rf {} \;
	@find -type f -name '*.pyc' -delete

.PHONY: default install reset check test tox readme docs publish clean

# Style
# =============================================================================
codespell:  # running manually
	@codespell -w -i 3 -q 3 -S $(CODESPELL_SKIPS) $(CODESPELL_DIRS)

codespell-error:  # running on travis
	@codespell -i 0 -q 7 -S $(CODESPELL_SKIPS) $(CODESPELL_DIRS)

pydocstyle:
	@echo "Running pydocstyle"
	@pydocstyle

pep:
	@$(MAKE) -k flake pydocstyle codespell-error

flake:
	@if command -v flake8 > /dev/null; then \
		echo "Running flake8"; \
		flake8 --count blocks examples; \
	else \
		echo "flake8 not found, please install it!"; \
		exit 1; \
	fi;
	@echo "flake8 passed"