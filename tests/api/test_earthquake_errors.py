import pytest

from clients.usgs_earthquake_client import UsgsEarthquakeClient

BASE_QUERY = {
    "format": "geojson",
    "starttime": "2014-01-01T00:00:00",
    "endtime": "2014-01-02T00:00:00",
}


@pytest.mark.parametrize(
    ("parameter", "invalid_value", "expected_error"),
    [
        pytest.param(
            "limit",
            20001,
            'Bad limit value "20001". Valid values are 0 <= limit <= 20000',
            id="limit-above-maximum",
        ),
        pytest.param(
            "orderby",
            "unsupported",
            'Bad orderby value "unsupported". Valid values are:',
            id="unsupported-orderby",
        ),
        pytest.param(
            "latitude",
            91,
            'Bad latitude value "91". Valid values are -90 <= latitude <= 90',
            id="latitude-above-maximum",
        ),
        pytest.param(
            "longitude",
            181,
            'Bad longitude value "181". Valid values are -180 <= longitude <= 180',
            id="longitude-above-maximum",
        ),
        pytest.param(
            "starttime",
            "not-a-date",
            'Bad starttime value "not-a-date". Valid values are ISO-8601 timestamps',
            id="malformed-date",
        ),
        pytest.param(
            "minmagnitude",
            "invalid",
            'Bad minmagnitude value "invalid". Valid values are numeric',
            id="invalid-minimum-magnitude",
        ),
        pytest.param(
            "maxmagnitude",
            "invalid",
            'Bad maxmagnitude value "invalid". Valid values are numeric',
            id="invalid-maximum-magnitude",
        ),
    ],
)
def test_invalid_query_value_returns_descriptive_bad_request(
    earthquake_client: UsgsEarthquakeClient,
    parameter: str,
    invalid_value: object,
    expected_error: str,
) -> None:
    response = earthquake_client.query({**BASE_QUERY, parameter: invalid_value})

    assert response.status_code == 400
    assert response.headers["Content-Type"].startswith("text/plain")
    assert expected_error in response.text
