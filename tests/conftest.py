"""Configuração pytest para flext-tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_tests.docker import tk


@pytest.fixture(scope="session")
def shared_ldap_container(flext_docker: tk) -> str:
    """Managed LDAP container using centralized tk with docker-compose."""
    compose_file = Path("~/flext/docker/docker-compose.openldap.yml").expanduser()
    start_result = flext_docker.start_compose_stack(str(compose_file))
    if start_result.is_failure:
        pytest.skip(f"OpenLDAP container failed to start: {start_result.error}")
    return "flext-openldap-test"


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
