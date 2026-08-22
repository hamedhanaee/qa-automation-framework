from datetime import UTC, datetime

import pytest
import requests

from clients.usgs_earthquake_client import UsgsEarthquakeClient

START_TIME = "2014-01-01T00:00:00"
END_TIME = "2014-01-02T00:00:00"
HISTORICAL_QUERY = {
    "format": "geojson",
    "starttime": START_TIME,
    "endtime": END_TIME,
    "minmagnitude": 6,
}


@pytest.fixture(scope="session")
def historical_earthquake_response(
    earthquake_client: UsgsEarthquakeClient,
) -> requests.Response:
    return earthquake_client.query(HISTORICAL_QUERY)


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


def test_historical_query_returns_expected_feature_structure(
    historical_earthquake_response: requests.Response,
) -> None:
    features = historical_earthquake_response.json()["features"]

    for feature in features:
        assert feature["type"] == "Feature"
        assert isinstance(feature["id"], str)
        assert isinstance(feature["properties"], dict)
        assert {
            "mag",
            "place",
            "time",
            "updated",
            "status",
            "tsunami",
            "sig",
            "net",
            "code",
            "type",
        } <= feature["properties"].keys()

        properties = feature["properties"]
        assert isinstance(properties["mag"], int | float)
        assert isinstance(properties["place"], str)
        assert isinstance(properties["time"], int)
        assert isinstance(properties["updated"], int)
        assert isinstance(properties["status"], str)
        assert isinstance(properties["tsunami"], int)
        assert isinstance(properties["sig"], int)
        assert isinstance(properties["net"], str)
        assert isinstance(properties["code"], str)
        assert isinstance(properties["type"], str)

        assert feature["geometry"]["type"] == "Point"
        coordinates = feature["geometry"]["coordinates"]
        assert len(coordinates) == 3
        assert all(isinstance(coordinate, int | float) for coordinate in coordinates)
        assert -180 <= coordinates[0] <= 180
        assert -90 <= coordinates[1] <= 90
