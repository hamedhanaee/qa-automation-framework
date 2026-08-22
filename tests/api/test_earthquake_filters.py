from datetime import UTC, datetime

import pytest

from clients.usgs_earthquake_client import UsgsEarthquakeClient

START_TIME = "2014-01-01T00:00:00"
END_TIME = "2014-01-03T00:00:00"
BASE_QUERY = {
    "format": "geojson",
    "starttime": START_TIME,
    "endtime": END_TIME,
}


@pytest.mark.parametrize(
    ("parameter", "value", "comparison"),
    [
        pytest.param("minmagnitude", 5, "minimum", id="minimum-magnitude"),
        pytest.param("maxmagnitude", 2, "maximum", id="maximum-magnitude"),
    ],
)
def test_magnitude_filter_returns_only_matching_events(
    earthquake_client: UsgsEarthquakeClient,
    parameter: str,
    value: int,
    comparison: str,
) -> None:
    response = earthquake_client.query({**BASE_QUERY, parameter: value})

    assert response.status_code == 200

    features = response.json()["features"]
    assert features
    magnitudes = [feature["properties"]["mag"] for feature in features]
    if comparison == "minimum":
        assert all(magnitude >= value for magnitude in magnitudes)
    else:
        assert all(magnitude <= value for magnitude in magnitudes)


@pytest.mark.parametrize(
    "limit",
    [
        pytest.param(1, id="minimum-limit"),
        pytest.param(5, id="small-limit"),
    ],
)
def test_limit_caps_number_of_returned_events(
    earthquake_client: UsgsEarthquakeClient,
    limit: int,
) -> None:
    response = earthquake_client.query(
        {**BASE_QUERY, "minmagnitude": 4, "limit": limit}
    )

    assert response.status_code == 200
    assert len(response.json()["features"]) == limit


@pytest.mark.parametrize(
    ("orderby", "property_name", "reverse"),
    [
        pytest.param("time", "time", True, id="time-descending"),
        pytest.param("time-asc", "time", False, id="time-ascending"),
        pytest.param("magnitude", "mag", True, id="magnitude-descending"),
        pytest.param("magnitude-asc", "mag", False, id="magnitude-ascending"),
    ],
)
def test_orderby_returns_events_in_requested_order(
    earthquake_client: UsgsEarthquakeClient,
    orderby: str,
    property_name: str,
    reverse: bool,
) -> None:
    response = earthquake_client.query(
        {**BASE_QUERY, "minmagnitude": 4, "orderby": orderby}
    )

    assert response.status_code == 200

    values = [
        feature["properties"][property_name] for feature in response.json()["features"]
    ]
    assert len(values) > 1
    assert values == sorted(values, reverse=reverse)


def test_time_filter_returns_only_events_in_requested_range(
    earthquake_client: UsgsEarthquakeClient,
) -> None:
    response = earthquake_client.query({**BASE_QUERY, "minmagnitude": 5})

    assert response.status_code == 200

    features = response.json()["features"]
    assert features
    start_timestamp_ms = int(
        datetime.fromisoformat(START_TIME).replace(tzinfo=UTC).timestamp() * 1000
    )
    end_timestamp_ms = int(
        datetime.fromisoformat(END_TIME).replace(tzinfo=UTC).timestamp() * 1000
    )
    assert all(
        start_timestamp_ms <= feature["properties"]["time"] <= end_timestamp_ms
        for feature in features
    )


def test_combined_filters_are_all_respected(
    earthquake_client: UsgsEarthquakeClient,
) -> None:
    response = earthquake_client.query(
        {
            **BASE_QUERY,
            "minmagnitude": 4,
            "maxmagnitude": 5,
            "limit": 10,
            "orderby": "magnitude-asc",
        }
    )

    assert response.status_code == 200

    features = response.json()["features"]
    assert len(features) == 10
    magnitudes = [feature["properties"]["mag"] for feature in features]
    assert all(4 <= magnitude <= 5 for magnitude in magnitudes)
    assert magnitudes == sorted(magnitudes)
