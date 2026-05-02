"""Configuração pytest para flext-tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_tests import tk

from flext_tap_ldap import FlextTapLdapSettings
from tests import c, m, t


@pytest.fixture
def tap_ldap_settings() -> FlextTapLdapSettings:
    """Provide clean FlextTapLdapSettings for tap-ldap tests."""
    return FlextTapLdapSettings(debug=True)


@pytest.fixture(scope="session")
def shared_ldap_container() -> str:
    """Managed LDAP container using centralized tk with docker-compose."""
    compose_file = Path("~/flext/docker/docker-compose.openldap.yml").expanduser()
    docker = tk.stack(
        compose_file,
        container_name="flext-openldap-test",
        service="openldap",
        host=c.Ldap.Tests.HOST,
        port=c.Ldap.Tests.PORT,
        workspace_root=compose_file.parent.parent,
    )
    start_result = docker.execute()
    if start_result.failure:
        pytest.skip(f"OpenLDAP container failed to start: {start_result.error}")
    return "flext-openldap-test"


@pytest.fixture
def ldap_connection_config() -> dict[str, object]:
    return {
        "host": c.Ldap.Tests.HOST,
        "port": c.Ldap.Tests.PORT,
        "base_dn": c.Ldap.Tests.BASE_DN,
        "bind_dn": c.Ldap.Tests.BIND_DN,
        "bind_password": c.Ldap.Tests.BIND_PASSWORD,
        "use_ssl": c.Ldap.Tests.USE_TLS,
        "timeout_seconds": c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
        "page_size": c.Ldap.Tests.PAGE_SIZE,
    }


@pytest.fixture
def ldap_source_config(
    ldap_connection_config: dict[str, t.JsonValue],
) -> m.Meltano.DataSourceConfig:
    return m.Meltano.DataSourceConfig(
        source_type="ldap",
        connection_config=ldap_connection_config,
        stream_config={},
        source_version="latest",
    )


@pytest.fixture
def ldap_record_entries() -> list[dict[str, object]]:
    return [
        {
            "dn": "uid=jdoe,ou=users,dc=test,dc=com",
            "uid": "jdoe",
            "cn": "John Doe",
            "mail": "jdoe@test.com",
            "objectClass": ["inetOrgPerson", "person"],
        }
    ]


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
