"""Configuração pytest para flext-tap-ldap - Now using shared container.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock

import pytest

from flext_tests import FlextTestDocker

# Import shared LDAP fixtures from docker directory


# Docker container management with FlextTestDocker
@pytest.fixture(scope="session")
def docker_control() -> FlextTestDocker:
    """Provide Docker control instance for tests."""
    return FlextTestDocker()


@pytest.fixture(scope="session")
def shared_ldap_container(
    docker_control: FlextTestDocker,
) -> Generator[FlextTestDocker]:
    """Managed LDAP container using FlextTestDocker with auto-start."""
    result = docker_control.start_container("flext-openldap-test")
    if result.is_failure:
        pytest.skip(f"Failed to start LDAP container: {result.error}")

    yield docker_control

    docker_control.stop_container("flext-openldap-test", remove=False)


def pytest_configure(config: pytest.Config) -> None:
    """Configura pytest com marcadores customizados."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")


# Shared LDAP container fixture (auto-use existing container)
@pytest.fixture(scope="session", autouse=True)
def ensure_shared_docker_container(shared_ldap_container: object) -> None:
    """Ensure shared Docker container is started for the test session.

    This fixture automatically starts the shared LDAP container if not running,
    and ensures it's available for all tests in the session.
    """
    # Suppress unused parameter warning - fixture is used for side effects
    _ = shared_ldap_container
    # The shared_ldap_container fixture will be invoked automatically
    # and will start/stop the container for the entire test session


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Obtém o diretório raiz do projeto."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root: Path) -> Path:
    """Obtém o diretório de dados de teste."""
    return project_root / "tests" / "data"


@pytest.fixture
def _mock_get_loop() -> Generator[Mock]:
    """Mock fixture for asyncio.get_running_loop."""
    with pytest.MonkeyPatch().context() as m:
        mock_loop = Mock()
        m.setattr("asyncio.get_running_loop", mock_loop)
        yield mock_loop


@pytest.fixture
def _mock_set_loop() -> Generator[Mock]:
    """Mock fixture for asyncio.set_event_loop."""
    with pytest.MonkeyPatch().context() as m:
        mock_set_loop = Mock()
        m.setattr("asyncio.set_event_loop", mock_set_loop)
        yield mock_set_loop
