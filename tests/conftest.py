from collections.abc import Iterator

import pytest

from clients.usgs_earthquake_client import UsgsEarthquakeClient


@pytest.fixture(scope="session")
def earthquake_client() -> Iterator[UsgsEarthquakeClient]:
    client = UsgsEarthquakeClient()
    yield client
    client.close()
