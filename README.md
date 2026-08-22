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

To create a self-contained HTML report:

```bash
pytest --html=reports/report.html --self-contained-html
```
