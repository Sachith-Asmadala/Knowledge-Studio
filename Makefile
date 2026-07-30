SHELL := /bin/sh

PYTHON ?= python3.11
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
PIP := $(VENV_PYTHON) -m pip
STREAMLIT := $(VENV_PYTHON) -m streamlit

.DEFAULT_GOAL := help

.PHONY: help setup install run compile test check clean

help: ## Show the available commands
	@awk 'BEGIN {FS = ":.*## "; printf "Knowledge Studio commands:\n\n"} /^[a-zA-Z_-]+:.*## / {printf "  %-10s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Create the virtual environment and install dependencies
	@$(PYTHON) -c 'import sys; assert (3, 11) <= sys.version_info[:2] <= (3, 12), "Python 3.11 or 3.12 is required"'
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@printf '\nSetup complete. Add GROQ_API_KEY to .env, then run: make run\n'

install: ## Install or update dependencies in an existing environment
	@test -x "$(VENV_PYTHON)" || { echo "Missing $(VENV). Run 'make setup' first."; exit 1; }
	$(PIP) install -r requirements.txt

run: ## Start the Streamlit application
	@test -x "$(VENV_PYTHON)" || { echo "Missing $(VENV). Run 'make setup' first."; exit 1; }
	$(STREAMLIT) run app.py

compile: ## Compile Python sources to catch syntax errors
	@test -x "$(VENV_PYTHON)" || { echo "Missing $(VENV). Run 'make setup' first."; exit 1; }
	$(VENV_PYTHON) -m compileall -q app.py src tests

test: ## Run the unit test suite
	@test -x "$(VENV_PYTHON)" || { echo "Missing $(VENV). Run 'make setup' first."; exit 1; }
	$(VENV_PYTHON) -m unittest discover -s tests -v

check: compile test ## Run all local verification checks

clean: ## Remove generated Python and test caches (keeps documents and indexes)
	find . -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
