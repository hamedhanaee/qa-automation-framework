# QA API Automation Framework

Python and Pytest API tests against the public USGS Earthquake Catalog API. The
current coverage validates a fixed historical query, its GeoJSON response contract,
event timestamps, feature structure, and documented invalid parameters.

## Setup

Python 3.11 or newer is required.

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .
```

The client uses the public USGS endpoint and a 15-second timeout by default. These
can be overridden with `USGS_EARTHQUAKE_BASE_URL` and
`API_REQUEST_TIMEOUT_SECONDS`.

## Running Tests

```bash
pytest
```

Run the fast API and response-contract checks, or the complete regression suite:

```bash
pytest -m smoke
pytest -m regression
```

Run formatting and lint checks:

```bash
ruff format --check .
ruff check .
```

To create a self-contained HTML report:

```bash
pytest --html=reports/report.html --self-contained-html
```

## CI

GitHub Actions runs formatting, linting, and the complete test suite on pull
requests, pushes to `main`, and manual dispatches. HTML and JUnit reports are
uploaded from every test run, including failed runs.
