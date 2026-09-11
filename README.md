# QA Automation Framework

[![Automated tests](https://github.com/hamedhanaee/qa-automation-framework/actions/workflows/api-tests.yml/badge.svg)](https://github.com/hamedhanaee/qa-automation-framework/actions/workflows/api-tests.yml)

Python and Pytest tests against the public USGS Earthquake Catalog and World Bank
Indicators APIs. Coverage includes response contracts, deterministic historical
queries, filtering, pagination, boundaries, and invalid input behavior.
Playwright UI tests cover core login, checkout, error, and sorting behavior in the
public Sauce Labs sample application.

## Setup

Python 3.11 or newer is required.

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .
python -m playwright install chromium
```

The clients use the public API endpoints and a 15-second timeout by default. Override
them with `USGS_EARTHQUAKE_BASE_URL`, `WORLD_BANK_INDICATORS_BASE_URL`, and
`API_REQUEST_TIMEOUT_SECONDS`. Override the UI target with `SAUCEDEMO_BASE_URL`.

Pytest captures each request's method, URL, response status, and elapsed time and
includes those details with test failures. Common sensitive query parameters are
redacted, and request or response headers and bodies are not logged.

## Running Tests

Run API tests, UI tests in headless Chromium, or the full suite:

```bash
pytest tests/api tests/unit -v
pytest tests/ui -v --browser chromium
pytest -v
```

Run fast availability and core-workflow checks, or complete regression coverage:

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

GitHub Actions runs formatting, linting, API tests, and UI tests in headless Chromium
on pull requests, pushes to `main`, and manual dispatches. HTML and JUnit reports,
screenshots, and traces from UI failures are uploaded from every run.
