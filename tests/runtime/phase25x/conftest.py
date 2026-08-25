import os
import pytest
import boto3
from botocore.exceptions import ClientError

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "real_aws: mark test to only run when API_GUARDIAN_REAL_AWS=1"
    )

def pytest_collection_modifyitems(config, items):
    if os.environ.get("API_GUARDIAN_REAL_AWS") != "1":
        skip_aws = pytest.mark.skip(reason="REAL_AWS_TESTS = NOT_ENABLED (missing API_GUARDIAN_REAL_AWS=1)")
        for item in items:
            if "real_aws" in item.keywords or "phase25x" in str(item.fspath):
                item.add_marker(skip_aws)
