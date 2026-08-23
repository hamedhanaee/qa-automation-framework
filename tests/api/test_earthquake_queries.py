from datetime import UTC, datetime

import pytest
import requests
from jsonschema import validate

from clients.usgs_earthquake_client import UsgsEarthquakeClient

START_TIME = "2014-01-01T00:00:00"
END_TIME = "2014-01-02T00:00:00"
HISTORICAL_QUERY = {
    "format": "geojson",
    "starttime": START_TIME,
    "endtime": END_TIME,
    "minmagnitude": 6,
}

pytestmark = pytest.mark.regression


@pytest.fixture(scope="session")
def historical_earthquake_response(
    earthquake_client: UsgsEarthquakeClient,
) -> requests.Response:
    return earthquake_client.query(HISTORICAL_QUERY)


@pytest.mark.smoke
def test_historical_query_returns_geojson_response(
    historical_earthquake_response: requests.Response,
) -> None:
    assert historical_earthquake_response.status_code == 200
    assert historical_earthquake_response.headers["Content-Type"].startswith(
        "application/json"
    )


def test_historical_query_returns_required_top_level_structure(
    historical_earthquake_response: requests.Response,
) -> None:
    body = historical_earthquake_response.json()

    assert body["type"] == "FeatureCollection"
    assert isinstance(body["metadata"], dict)
    assert isinstance(body["features"], list)
    assert body["metadata"]["count"] == len(body["features"])
    assert body["features"]


def test_historical_query_returns_events_within_requested_range(
    historical_earthquake_response: requests.Response,
) -> None:
    features = historical_earthquake_response.json()["features"]
    start_timestamp_ms = int(
        datetime.fromisoformat(START_TIME).replace(tzinfo=UTC).timestamp() * 1000
    )
    end_timestamp_ms = int(
        datetime.fromisoformat(END_TIME).replace(tzinfo=UTC).timestamp() * 1000
    )

    for feature in features:
        event_timestamp_ms = feature["properties"]["time"]
        assert start_timestamp_ms <= event_timestamp_ms <= end_timestamp_ms


@pytest.mark.smoke
def test_historical_query_matches_geojson_contract(
    historical_earthquake_response: requests.Response,
    earthquake_feature_collection_schema: dict[str, object],
) -> None:
    body = historical_earthquake_response.json()
    validate(instance=body, schema=earthquake_feature_collection_schema)

    for feature in body["features"]:
        coordinates = feature["geometry"]["coordinates"]
        assert len(coordinates) == 3
        assert -180 <= coordinates[0] <= 180
        assert -90 <= coordinates[1] <= 90
