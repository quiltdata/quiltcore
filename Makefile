sinclude .env # create from example.env
.PHONY: install lint test watch all clean check typecheck
PROJECT=quiltcore
TEST_README=--codeblocks
LOCAL_ONLY=False

ifeq ($(TEST_OS),windows-latest)
	TEST_README=''
endif

all: lock install update test

clean:
	rm -f *.log
	rm -rf .coverage* coverage* 
	rm -rf quiltplus/.pytest_cache .mypy_cache .quilt

lock:
	poetry lock

install:
	poetry install

update:
	poetry update

check:
	poetry check
	make typecheck
	make lint

test: clean check
	poetry run pytest $(TEST_README) --cov --cov-report xml:coverage.xml

test-readme:
	poetry run pytest $(TEST_README) 

test-local:
	export LOCAL_ONLY=True; poetry run pytest

lint:
	poetry run black $(PROJECT) tests
	poetry run flake8 $(PROJECT) tests

typecheck:
	poetry run mypy $(PROJECT) tests

coverage:
	poetry run pytest --cov --cov-report html:coverage_html
	open coverage_html/index.html

watch:
	poetry run ptw .

tag:
	git tag `poetry version | awk '{print $$2}'`
	git push --tags

pypi: clean tag clean-git
	poetry version
	poetry build
	poetry publish --dry-run

clean-git:
	git branch | grep -v '*' | grep -v 'main' | xargs git branch -D

which:
	which $(PROJECT)
	$(PROJECT) --version

pip-install:
	python3 -m pip install $(PROJECT)
	make which

pip-upgrade:
	python3 -m pip install --upgrade $(PROJECT)
	make which

pip-update:
	poetry self update
	python3 -m pip install --upgrade pip


