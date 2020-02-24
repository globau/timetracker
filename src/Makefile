.PHONY: all clean test
SHELL=/bin/sh

black=../venv/bin/black
isort=../venv/bin/isort --multi-line 3 --trailing-comma --atomic --line-width 88
flake8=../venv/bin/flake8 --max-line-length=88 --ignore=E203,W503 --disable-noqa

all: ../venv/updated .format

clean:
	rm -rf .format ../venv/

../venv/updated: requirements.txt dev-requirements.txt
	[ -d "../venv" ] || python3 -m venv ../venv
	../venv/bin/pip install -U -r requirements.txt pip
	../venv/bin/pip install -U -r dev-requirements.txt
	touch ../venv/updated

test: ../venv/updated ../tt *.py **/*.py
	../venv/bin/black --check $^ 2>&1 | cat
	../venv/bin/isort --check-only $^ --multi-line 3 --trailing-comma --atomic --line-width 88
	../venv/bin/flake8 $^ --max-line-length=88 --ignore=E203,W503 --disable-noqa
	../venv/bin/pylint $^ --score=no --persistent=no --jobs=0 --disable=bad-continuation,consider-using-enumerate,fixme,import-error,import-outside-toplevel,import-self,invalid-name,missing-class-docstring,missing-function-docstring,missing-module-docstring,no-name-in-module,no-self-use,no-value-for-parameter,subprocess-run-check,too-few-public-methods,too-many-ancestors,too-many-arguments,too-many-boolean-expressions,too-many-branches,too-many-instance-attributes,too-many-lines,too-many-locals,too-many-return-statements,too-many-statements,wrong-import-order

.format: ../venv/updated ../tt *.py **/*.py
	../venv/bin/black $^ 2>&1 | cat
	../venv/bin/isort $^ --multi-line 3 --trailing-comma --atomic --line-width 88
	../venv/bin/flake8 $^ --max-line-length=88 --ignore=E203,W503 --disable-noqa
	../venv/bin/pylint $^ --score=no --persistent=no --jobs=0 --disable=bad-continuation,consider-using-enumerate,fixme,import-error,import-outside-toplevel,import-self,invalid-name,missing-class-docstring,missing-function-docstring,missing-module-docstring,no-name-in-module,no-self-use,no-value-for-parameter,subprocess-run-check,too-few-public-methods,too-many-ancestors,too-many-arguments,too-many-boolean-expressions,too-many-branches,too-many-instance-attributes,too-many-lines,too-many-locals,too-many-return-statements,too-many-statements,wrong-import-order
	touch $@
