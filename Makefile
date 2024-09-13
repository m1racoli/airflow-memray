PYTHON_VERSION := 3.11
RUNTIME_UPDATES_URL := https://updates.astronomer.io/astronomer-runtime
VIRTUAL_ENV := .venv

PYTHON := python$(PYTHON_VERSION)
VIRTUAL_ENV_PYTHON := $(VIRTUAL_ENV)/bin/$(PYTHON)

RUNTIME_VERSION = $(shell grep -Em 1 '^FROM.*astro-runtime' Dockerfile | grep -Eo "[0-9]+\.[0-9]+\.[0-9]+")
AIRFLOW_VERSION = $(shell curl -fs $(RUNTIME_UPDATES_URL) | jq -r '.runtimeVersions["$(RUNTIME_VERSION)"].metadata.airflowVersion')

.PHONY: clean
clean: clean-requirements clean-tests clean-virtualenv

.PHONY: clean-requirements
clean-requirements:
	@rm -f requirements.txt

.PHONY: clean-tests
clean-tests:
	@rm -rf tests/memray

.PHONY: clean-virtualenv
clean-virtualenv:
	@rm -rf $(VIRTUAL_ENV)

.PHONY: release
release:
	towncrier build --yes --version $(shell cz bump --get-next --yes)
	cz bump --yes --no-verify

.PHONY: virtualenv
virtualenv: $(VIRTUAL_ENV_PYTHON) requirements.txt
	@uv pip install apache-airflow==$(AIRFLOW_VERSION) -r requirements.txt

.PHONY: version
version:
	@echo Apache Airflow Version: $(AIRFLOW_VERSION)
	@echo Astro Runtime Version: $(RUNTIME_VERSION)
	@astro version

%/bin/$(PYTHON):
	@uv venv -p $(PYTHON_VERSION) $*

requirements.txt: requirements.in
	@docker run -qit --rm --entrypoint python quay.io/astronomer/astro-runtime:$(RUNTIME_VERSION)-python-$(PYTHON_VERSION) -m pip freeze > requirements.txt
	@uv pip compile --no-emit-package apache-airflow --quiet --emit-index-url --python-version $(PYTHON_VERSION) requirements.in -o requirements.txt

# assert required commands

ifeq (, $(shell which jq))
$(error No jq found. Consider installing it: "https://jqlang.github.io/jq/download/")
endif

ifeq (, $(shell which $(PYTHON)))
$(error No $(PYTHON) found. Consider installing it with pyenv: "https://github.com/pyenv/pyenv")
endif

ifeq (, $(shell which astro))
$(error No astro CLI found. Consider installing it: "https://docs.astronomer.io/astro/cli/install-cli")
endif

ifeq (, $(shell which uv))
$(error No uv found. Consider installing it: "https://github.com/astral-sh/uv")
endif
