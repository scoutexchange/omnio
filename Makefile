.PHONY: all check clean flake8 integration test

all:
	@echo 'black            apply black code formatter'
	@echo 'black-check      check compliance with black code formatting'
	@echo 'check            make sure you are ready to commit'
	@echo 'clean            clean up the source tree'
	@echo 'flake8           check flake8 compliance'
	@echo 'test             run the unit tests'

black:
	@black --skip-string-normalization omnio tests

black-check:
	@black --skip-string-normalization --check omnio tests || exit 1

check: clean black-check flake8 test
	@coverage report |grep ^TOTAL |grep 100% >/dev/null || { echo 'Unit test coverage is incomplete.'; exit 1; }

clean:
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete
	@rm -rf build dist .coverage MANIFEST

flake8:
	@flake8 --max-line-length 88 omnio tests

test: clean
	@PYTHONPATH=. py.test --cov omnio tests/test_*.py
