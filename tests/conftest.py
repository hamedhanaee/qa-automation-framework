import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from clients.usgs_earthquake_client import UsgsEarthquakeClient
from clients.world_bank_indicators_client import WorldBankIndicatorsClient

SCHEMA_DIRECTORY = Path(__file__).parent / "schemas"


@pytest.fixture(scope="session")
def earthquake_client() -> Iterator[UsgsEarthquakeClient]:
    client = UsgsEarthquakeClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def earthquake_feature_collection_schema() -> dict[str, Any]:
    schema_path = SCHEMA_DIRECTORY / "earthquake_feature_collection.json"
    with schema_path.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


@pytest.fixture(scope="session")
def world_bank_client() -> Iterator[WorldBankIndicatorsClient]:
    client = WorldBankIndicatorsClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def world_bank_indicator_schema() -> dict[str, Any]:
    schema_path = SCHEMA_DIRECTORY / "world_bank_indicator_response.json"
    with schema_path.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)
