# telebotties [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Running the pre-commit script

You can run the **tests**
([tox](https://tox.wiki/en/latest/index.html),
[pytest](https://docs.pytest.org)), **formatting**
([black](https://black.readthedocs.io/en/stable/),
[isort](https://pycqa.github.io/isort/)) and **linting**
([pflake8](https://github.com/csachs/pyproject-flake8),
[pep8-naming](https://github.com/PyCQA/pep8-naming),
[codespell](https://github.com/codespell-project/codespell),
[markdownlint](https://github.com/markdownlint/markdownlint)) simply by
executing:

```text
./pre-commit
```

Now if you want to automatically run these when you call `git commit`, copy
the script into `.git/hooks/` directory:

```text
cp pre-commit .git/hooks
```

> **NOTE**: this process does not run `markdownlint` by default as it
requires [Ruby](https://www.ruby-lang.org/en/) to be installed. If you want
to run `markdownlint` locally as well,
[install Ruby](https://www.ruby-lang.org/en/documentation/installation/)
and install markdown lint with `gem install mdl -v 0.11.0`. Then from
`pre-commit` change `RUN_MDL=false` to `RUN_MDL=true`. (You need to copy the
file again into `.git/hooks/` if you did that earlier)
