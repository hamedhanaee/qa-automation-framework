import pytest
import requests
from jsonschema import validate

from clients.world_bank_indicators_client import WorldBankIndicatorsClient

COUNTRY_CODE = "USA"
INDICATOR_CODE = "SP.POP.TOTL"
START_YEAR = 2010
END_YEAR = 2012
HISTORICAL_QUERY = {
    "date": f"{START_YEAR}:{END_YEAR}",
    "per_page": 100,
}

pytestmark = pytest.mark.regression


@pytest.fixture(scope="session")
def historical_population_response(
    world_bank_client: WorldBankIndicatorsClient,
) -> requests.Response:
    return world_bank_client.get_indicator(
        COUNTRY_CODE,
        INDICATOR_CODE,
        HISTORICAL_QUERY,
    )


@pytest.mark.smoke
def test_indicator_query_returns_json_response(
    historical_population_response: requests.Response,
) -> None:
    assert historical_population_response.status_code == 200
    assert historical_population_response.headers["Content-Type"].startswith(
        "application/json"
    )


@pytest.mark.smoke
def test_indicator_query_matches_response_contract(
    historical_population_response: requests.Response,
    world_bank_indicator_schema: dict[str, object],
) -> None:
    body = historical_population_response.json()
    validate(instance=body, schema=world_bank_indicator_schema)

    metadata, results = body
    assert metadata["page"] == 1
    assert metadata["pages"] == 1
    assert metadata["total"] == len(results)


@pytest.mark.parametrize(
    ("country_code", "expected_iso3_code"),
    [
        pytest.param("USA", "USA", id="united-states"),
        pytest.param("CAN", "CAN", id="canada"),
    ],
)
def test_country_filter_returns_only_requested_country(
    world_bank_client: WorldBankIndicatorsClient,
    country_code: str,
    expected_iso3_code: str,
) -> None:
    response = world_bank_client.get_indicator(
        country_code,
        INDICATOR_CODE,
        {"date": "2010"},
    )

    assert response.status_code == 200

    _, results = response.json()
    assert results
    assert {result["countryiso3code"] for result in results} == {expected_iso3_code}


@pytest.mark.parametrize(
    "indicator_code",
    [
        pytest.param("SP.POP.TOTL", id="population"),
        pytest.param("NY.GDP.MKTP.CD", id="gdp"),
    ],
)
def test_indicator_filter_returns_only_requested_indicator(
    world_bank_client: WorldBankIndicatorsClient,
    indicator_code: str,
) -> None:
    response = world_bank_client.get_indicator(
        COUNTRY_CODE,
        indicator_code,
        {"date": "2010"},
    )

    assert response.status_code == 200

    _, results = response.json()
    assert results
    assert {result["indicator"]["id"] for result in results} == {indicator_code}


def test_date_range_returns_only_requested_years(
    historical_population_response: requests.Response,
) -> None:
    _, results = historical_population_response.json()

    assert {int(result["date"]) for result in results} == set(
        range(START_YEAR, END_YEAR + 1)
    )


def test_page_selects_requested_result_slice(
    world_bank_client: WorldBankIndicatorsClient,
) -> None:
    params = {"date": "2010:2014", "per_page": 2}
    first_response = world_bank_client.get_indicator(
        COUNTRY_CODE,
        INDICATOR_CODE,
        {**params, "page": 1},
    )
    second_response = world_bank_client.get_indicator(
        COUNTRY_CODE,
        INDICATOR_CODE,
        {**params, "page": 2},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_metadata, first_results = first_response.json()
    second_metadata, second_results = second_response.json()
    assert first_metadata["page"] == 1
    assert second_metadata["page"] == 2
    assert first_metadata["pages"] == second_metadata["pages"] == 3
    assert first_metadata["total"] == second_metadata["total"] == 5
    assert len(first_results) == len(second_results) == 2
    assert {result["date"] for result in first_results}.isdisjoint(
        result["date"] for result in second_results
    )


@pytest.mark.parametrize(
    "per_page",
    [
        pytest.param(1, id="one-result"),
        pytest.param(2, id="two-results"),
    ],
)
def test_per_page_controls_result_count(
    world_bank_client: WorldBankIndicatorsClient,
    per_page: int,
) -> None:
    response = world_bank_client.get_indicator(
        COUNTRY_CODE,
        INDICATOR_CODE,
        {"date": "2010:2012", "per_page": per_page},
    )

    assert response.status_code == 200

    metadata, results = response.json()
    assert metadata["per_page"] == per_page
    assert metadata["total"] == 3
    assert len(results) == per_page


def test_multiple_countries_returns_each_requested_country(
    world_bank_client: WorldBankIndicatorsClient,
) -> None:
    response = world_bank_client.get_indicator(
        "USA;CAN",
        INDICATOR_CODE,
        {"date": "2010:2011", "per_page": 100},
    )

    assert response.status_code == 200

    metadata, results = response.json()
    assert metadata["total"] == 4
    assert {result["countryiso3code"] for result in results} == {"USA", "CAN"}
    assert {result["date"] for result in results} == {"2010", "2011"}


@pytest.mark.parametrize(
    ("country_code", "indicator_code"),
    [
        pytest.param("ZZZZ", INDICATOR_CODE, id="invalid-country"),
        pytest.param(COUNTRY_CODE, "NOT.A.REAL.INDICATOR", id="invalid-indicator"),
    ],
)
def test_invalid_identifier_returns_invalid_value_message(
    world_bank_client: WorldBankIndicatorsClient,
    country_code: str,
    indicator_code: str,
) -> None:
    response = world_bank_client.get_indicator(
        country_code,
        indicator_code,
        {"date": "2010"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "message": [
                {
                    "id": "120",
                    "key": "Invalid value",
                    "value": "The provided parameter value is not valid",
                }
            ]
        }
    ]


@pytest.mark.parametrize(
    ("parameter", "value"),
    [
        pytest.param("date", "not-a-date", id="malformed-date"),
        pytest.param("page", "not-a-page", id="malformed-page"),
    ],
)
def test_malformed_parameter_returns_invalid_value_message(
    world_bank_client: WorldBankIndicatorsClient,
    parameter: str,
    value: str,
) -> None:
    response = world_bank_client.get_indicator(
        COUNTRY_CODE,
        INDICATOR_CODE,
        {"date": "2010", parameter: value},
    )

    assert response.status_code == 200

    message = response.json()[0]["message"][0]
    assert message["id"] == "120"
    assert message["key"] == "Invalid value"
    assert message["value"] == "The provided parameter value is not valid"


def test_year_without_results_returns_empty_metadata_and_null_results(
    world_bank_client: WorldBankIndicatorsClient,
) -> None:
    response = world_bank_client.get_indicator(
        COUNTRY_CODE,
        INDICATOR_CODE,
        {"date": "1900"},
    )

    assert response.status_code == 200

    metadata, results = response.json()
    assert metadata["page"] == 0
    assert metadata["pages"] == 0
    assert metadata["per_page"] == 0
    assert metadata["total"] == 0
    assert metadata["sourceid"] is None
    assert metadata["lastupdated"] is None
    assert results is None
