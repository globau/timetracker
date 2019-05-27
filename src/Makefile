.PHONY: all clean

all: ../venv/updated .format

clean:
	@rm -rf .format ../venv/

../venv/updated: requirements.txt dev-requirements.txt
	@[[ -d "../venv" ]] || virtualenv -p python3 ../venv
	@../venv/bin/pip install -U -r requirements.txt pip
	@../venv/bin/pip install -U -r dev-requirements.txt
	@touch ../venv/updated

.format: ../tt *.py **/*.py
	@../venv/bin/black $^
	@../venv/bin/isort --multi-line 3 --trailing-comma --atomic --line-width 88 $^
	@../venv/bin/flake8 --max-line-length=88 --ignore=E203,W503 --disable-noqa $^
	@touch $@
