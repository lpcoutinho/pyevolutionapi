"""
Pytest configuration for end-to-end tests.

E2E tests simulate complete user workflows and require a fully
functioning Evolution API with real WhatsApp connections.
"""

import os

import pytest


@pytest.fixture(scope="session")
def e2e_config():
    """Configuration for E2E tests."""
    return {
        "timeout": int(os.getenv("E2E_TIMEOUT", "600")),  # 10 minutes default
        "require_connection": os.getenv("E2E_REQUIRE_CONNECTION", "false").lower() == "true",
        "test_number": os.getenv("E2E_TEST_NUMBER"),  # WhatsApp number for testing
    }


@pytest.fixture
def require_test_number(e2e_config):
    """Skip test if no test WhatsApp number is configured."""
    if not e2e_config["test_number"]:
        pytest.skip("E2E_TEST_NUMBER not configured - skipping message tests")
    return e2e_config["test_number"]


def pytest_configure(config):
    """Configure E2E test markers."""
    config.addinivalue_line("markers", "e2e: End-to-end tests (require full Evolution API setup)")
    config.addinivalue_line(
        "markers", "requires_whatsapp: Tests that require actual WhatsApp connection"
    )
