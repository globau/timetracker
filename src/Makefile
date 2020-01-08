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
	../venv/bin/pylint $^ --disable=all --enable=R0205,W1201,R1714,R1705,R1710,W0612 --score=no --persistent=no --jobs=0

.format: ../venv/updated ../tt *.py **/*.py
	../venv/bin/black $^ 2>&1 | cat
	../venv/bin/isort $^ --multi-line 3 --trailing-comma --atomic --line-width 88
	../venv/bin/flake8 $^ --max-line-length=88 --ignore=E203,W503 --disable-noqa
	../venv/bin/pylint $^ --disable=all --enable=R0205,W1201,R1714,R1705,R1710,W0612 --score=no --persistent=no --jobs=0
	touch $@
