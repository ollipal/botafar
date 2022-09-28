# Development

Currently hard to understand... Will be improved at some point.

## Use pre-commit hooks

To enable local hooks:
`pip install tox==3.24.4 flake8==4.0.1 pyproject-flake8==0.0.1a2 pep8-naming==0.12.1`

Then run `pip install pre-commit` and then `pre-commit install`

> **NOTE**: this process does not run `markdownlint` by default as it
requires [Ruby](https://www.ruby-lang.org/en/) to be installed. If you want
to run `markdownlint` locally as well,
[install Ruby](https://www.ruby-lang.org/en/documentation/installation/)
and install markdown lint with `gem install mdl -v 0.11.0` and
uncomment lines from `.pre-commit-config.yaml`

## Install in virtual env

sudo apt-get install python3-dev python3-pip python3-venv

python3 -m venv env

source env/bin/activate

python -m pip install flit

python -m flit install --symlink

pre-commit install

rm -rf docs/build/ && sphinx-autobuild ./docs/source/ ./docs/build/html/

deactivate