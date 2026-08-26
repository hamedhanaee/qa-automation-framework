# QA API Automation Framework

Python and Pytest tests against the public USGS Earthquake Catalog and World Bank
Indicators APIs. Coverage includes response contracts, deterministic historical
queries, filtering, pagination, boundaries, and invalid input behavior.

## Setup

Python 3.11 or newer is required.

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .
```

The clients use the public API endpoints and a 15-second timeout by default. Override
them with `USGS_EARTHQUAKE_BASE_URL`, `WORLD_BANK_INDICATORS_BASE_URL`, and
`API_REQUEST_TIMEOUT_SECONDS`.

Pytest captures each request's method, URL, response status, and elapsed time and
includes those details with test failures. Common sensitive query parameters are
redacted, and request or response headers and bodies are not logged.

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
