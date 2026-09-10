import csv
from pathlib import Path

import pytest

from clients.request_diagnostics import _safe_request_url
from clients.world_bank_indicators_client import WorldBankIndicatorsClient

pytestmark = pytest.mark.performance

RESULT_PATH = Path("performance-results/world_bank_response_times.csv")
SCENARIOS = [
    ("single-year", "2010"),
    ("five-years", "2010:2014"),
    ("ten-years", "2010:2019"),
]
CSV_FIELDS = [
    "scenario",
    "method",
    "request_url",
    "status_code",
    "response_time_ms",
    "record_count",
    "requested_date_range",
]


def test_world_bank_historical_range_response_times(
    world_bank_client: WorldBankIndicatorsClient,
) -> None:
    measurements: list[dict[str, object]] = []

    for scenario, date_range in SCENARIOS:
        response = world_bank_client.get_indicator(
            "USA",
            "SP.POP.TOTL",
            {"date": date_range, "per_page": 100},
        )

        assert response.status_code == 200

        metadata, results = response.json()
        assert results is not None
        assert metadata["total"] == len(results)

        measurements.append(
            {
                "scenario": scenario,
                "method": response.request.method,
                "request_url": _safe_request_url(response.request.url),
                "status_code": response.status_code,
                "response_time_ms": round(
                    response.elapsed.total_seconds() * 1000,
                    1,
                ),
                "record_count": len(results),
                "requested_date_range": date_range,
            }
        )

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULT_PATH.open("w", newline="", encoding="utf-8") as result_file:
        writer = csv.DictWriter(result_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(measurements)
