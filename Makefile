PYTHON = python

# In not in a virtualenv, add --user options for install commands.
INSTALL_OPTS = `$(PYTHON) -c "import sys; print('' if hasattr(sys, 'real_prefix') else '--user')"`
# List of development third party libs.
PY_DEPS = \
	docx2txt \
	python-pptx \
	pytesseract \
	xlrd \
	flake8 \



test:  ## Run tests.
	$(PYTHON) tests.py

check:  ## Run linters.
	@git ls-files | grep \\.py$ | xargs $(PYTHON) -m flake8

lint: check

install:  ## Install this package as current user in "edit" mode.
	PYTHONWARNINGS=all $(PYTHON) setup.py develop $(INSTALL_OPTS)

pydeps:  ## Install third party python libs.
	$(PYTHON) -m pip install $(INSTALL_OPTS) --upgrade $(PY_DEPS)

sysdeps:  ## Install system deps.
	sudo apt-get install -y unrtf antiword poppler-utils libjpeg-dev tesseract-ocr abiword

publish:  ## Upload package on PYPI.
	$(PYTHON) setup.py register
	$(PYTHON) setup.py sdist upload

clean:  ## Remove all build files.
	rm -rf `find . -type d -name __pycache__ \
		-o -type f -name \*.bak \
		-o -type f -name \*.orig \
		-o -type f -name \*.pyc \
		-o -type f -name \*.pyd \
		-o -type f -name \*.pyo \
		-o -type f -name \*.rej \
		-o -type f -name \*.so \
		-o -type f -name \*.~ \
		-o -type f -name \*\$testfn`
	rm -rf \
		*.core \
		*.egg-info \
		*\$testfn* \
		.coverage \
		.tox \
		build/ \
		dist/ \
		docs/_build/ \
		htmlcov/ \
		tmp/

help: ## Display callable targets.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
