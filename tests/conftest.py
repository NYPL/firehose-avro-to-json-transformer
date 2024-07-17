import json
import os
import pytest

# Sets OS vars for entire set of tests
TEST_ENV_VARS = {
    "ENVIRONMENT": "test",
    "NYPL_DATA_API_BASE_URL": "https://qa-platform.nypl.org/api/v0.1/",
    "SCHEMA_PATH": "current-schemas/",
}


@pytest.fixture
def test_data():
    test_data_directory = "tests/stubs"
    test_data = {}

    for file in os.listdir(test_data_directory):
        with open(f"{test_data_directory}/{file}", "r") as f:
            key = file.split(".")[0]
            test_data[key] = json.load(f)
    return test_data


@pytest.fixture(scope="session", autouse=True)
def tests_setup_and_teardown():
    # Will be executed before the first test
    os.environ.update(TEST_ENV_VARS)

    yield

    # Will execute after final test
    for os_config in TEST_ENV_VARS.keys():
        del os.environ[os_config]
