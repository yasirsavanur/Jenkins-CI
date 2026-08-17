.PHONY: install lint unit smoke regression mobile report check

PYTHON ?= python
PYTEST := $(PYTHON) -m pytest

install:
	$(PYTHON) -m pip install -e ".[test]"

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

unit:
	$(PYTEST) -m unit

smoke:
	$(PYTEST) -m smoke --target local --browser chrome

regression:
	$(PYTEST) -m regression --target local --browser chrome -n 2

mobile:
	$(PYTEST) -m mobile --target local --browser chrome

report:
	$(PYTEST) -m regression --target local --browser chrome -n 2 \
		--junitxml=reports/acceptance.xml \
		--html=reports/report.html \
		--self-contained-html

check: lint unit
