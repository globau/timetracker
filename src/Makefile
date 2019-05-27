.PHONY: all clean test
SHELL=/bin/sh

black=../venv/bin/black
isort=../venv/bin/isort --multi-line 3 --trailing-comma --atomic --line-width 88
flake8=../venv/bin/flake8 --max-line-length=88 --ignore=E203,W503 --disable-noqa

all: ../venv/updated .format

clean:
	rm -rf .format ../venv/

../venv/updated: requirements.txt dev-requirements.txt
	[ -d "../venv" ] || virtualenv -p python3 ../venv
	../venv/bin/pip install -U -r requirements.txt pip
	../venv/bin/pip install -U -r dev-requirements.txt
	touch ../venv/updated

test: ../venv/updated ../tt *.py **/*.py
	$(black) --check $^
	$(isort) --check-only $^
	$(flake8) $^

.format: ../tt *.py **/*.py
	$(black) $^
	$(isort) $^
	$(flake8) $^
	touch $@
