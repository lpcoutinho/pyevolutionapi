"""
Pytest configuration for end-to-end tests.

E2E tests simulate complete user workflows and require a fully
functioning Evolution API with real WhatsApp connections.
"""

import os

import pytest

from pyevolutionapi import EvolutionClient


@pytest.fixture(scope="session")
def e2e_config():
    """Configuration for E2E tests."""
    return {
        "timeout": int(os.getenv("E2E_TIMEOUT", "600")),  # 10 minutes default
        "require_connection": os.getenv("E2E_REQUIRE_CONNECTION", "false").lower() == "true",
        "test_number": os.getenv("E2E_TEST_NUMBER"),  # WhatsApp number for testing
    }


@pytest.fixture(scope="session")
def api_config():
    """API configuration for E2E tests."""
    base_url = os.getenv("EVOLUTION_BASE_URL", "http://localhost:8080")
    api_key = os.getenv("EVOLUTION_API_KEY")

    if not api_key:
        pytest.skip("EVOLUTION_API_KEY not configured - skipping E2E tests")

    return {
        "base_url": base_url,
        "api_key": api_key,
        "timeout": 60.0,
    }


@pytest.fixture(scope="session")
def real_client(api_config):
    """Real Evolution API client for E2E tests."""
    client = EvolutionClient(
        base_url=api_config["base_url"],
        api_key=api_config["api_key"],
        timeout=api_config["timeout"],
        debug=True,
    )

    # Test if API is accessible
    try:
        health = client.health_check()
        if isinstance(health, dict):
            if not health.get("status") == "ok":
                pytest.skip("Evolution API not accessible")
        elif isinstance(health, bool):
            if not health:
                pytest.skip("Evolution API not accessible")
        else:
            pytest.skip("Evolution API returned unexpected response")
    except Exception as e:
        pytest.skip(f"Evolution API not accessible: {e}")

    yield client


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
    config.addinivalue_line("markers", "slow: Tests that take longer than usual to execute")
