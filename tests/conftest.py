"""Configuração pytest para flext-tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

# PYTHON_VERSION_GUARD — Do not remove. Managed by scripts/maintenance/enforce_python_version.py
import sys as _sys

if _sys.version_info[:2] != (3, 13):
    _v = (
        f"{_sys.version_info.major}.{_sys.version_info.minor}.{_sys.version_info.micro}"
    )
    raise RuntimeError(
        f"\n{'=' * 72}\n"
        f"FATAL: Python {_v} detected — this project requires Python 3.13.\n"
        f"\n"
        f"The virtual environment was created with the WRONG Python interpreter.\n"
        f"\n"
        f"Fix:\n"
        f"  1. rm -rf .venv\n"
        f"  2. poetry env use python3.13\n"
        f"  3. poetry install\n"
        f"\n"
        f"Or use the workspace Makefile:\n"
        f"  make setup PROJECT=<project-name>\n"
        f"{'=' * 72}\n"
    )
del _sys
# PYTHON_VERSION_GUARD_END

from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock

import pytest
from flext_tests import FlextTestsDocker


@pytest.fixture(scope="session")
def shared_ldap_container(flext_docker: "FlextTestsDocker") -> Generator[str]:
    """Managed LDAP container using centralized FlextTestsDocker with docker-compose."""
    # Use centralized docker-compose file for OpenLDAP
    compose_file = Path("~/flext/docker/docker-compose.openldap.yml").expanduser()

    # Start OpenLDAP stack using docker-compose
    start_result = flext_docker.start_compose_stack(compose_file)
    if start_result.is_failure:
        pytest.skip(f"OpenLDAP container failed to start: {start_result.error}")

    return "flext-openldap-test"

    # Cleanup handled by FlextTestsDocker automatically


def pytest_configure(config: pytest.Config) -> None:
    """Configura pytest com marcadores customizados."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")


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
    """Mock fixture for get_running_loop."""
    with pytest.MonkeyPatch().context() as m:
        mock_loop = Mock()
        m.setattr("get_running_loop", mock_loop)
        yield mock_loop


@pytest.fixture
def _mock_set_loop() -> Generator[Mock]:
    """Mock fixture for set_event_loop."""
    with pytest.MonkeyPatch().context() as m:
        mock_set_loop = Mock()
        m.setattr("set_event_loop", mock_set_loop)
        yield mock_set_loop
