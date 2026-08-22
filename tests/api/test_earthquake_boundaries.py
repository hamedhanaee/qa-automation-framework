import pytest

from clients.usgs_earthquake_client import UsgsEarthquakeClient

BASE_QUERY = {
    "format": "geojson",
    "starttime": "2014-01-01T00:00:00",
    "endtime": "2014-01-02T00:00:00",
}


def test_documented_maximum_limit_is_accepted_for_small_result_set(
    earthquake_client: UsgsEarthquakeClient,
) -> None:
    response = earthquake_client.query(
        {**BASE_QUERY, "minmagnitude": 6, "limit": 20000}
    )

    assert response.status_code == 200
    assert len(response.json()["features"]) <= 20000


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        pytest.param(-90, 0, id="minimum-latitude"),
        pytest.param(90, 0, id="maximum-latitude"),
        pytest.param(0, -180, id="minimum-longitude"),
        pytest.param(0, 180, id="maximum-longitude"),
    ],
)
def test_circle_coordinate_boundaries_are_accepted(
    earthquake_client: UsgsEarthquakeClient,
    latitude: int,
    longitude: int,
) -> None:
    response = earthquake_client.query(
        {
            **BASE_QUERY,
            "latitude": latitude,
            "longitude": longitude,
            "maxradius": 1,
        }
    )

    assert response.status_code == 200
    assert response.json()["type"] == "FeatureCollection"


@pytest.mark.parametrize(
    ("starttime", "endtime"),
    [
        pytest.param("2014-01-01", "2014-01-01", id="equal-range"),
        pytest.param("2014-01-02", "2014-01-01", id="reversed-range"),
    ],
)
def test_empty_time_range_returns_empty_feature_collection(
    earthquake_client: UsgsEarthquakeClient,
    starttime: str,
    endtime: str,
) -> None:
    response = earthquake_client.query(
        {"format": "geojson", "starttime": starttime, "endtime": endtime}
    )

    assert response.status_code == 200

    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert body["metadata"]["count"] == 0
    assert body["features"] == []
