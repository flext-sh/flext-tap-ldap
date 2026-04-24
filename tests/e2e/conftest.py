"""Pytest fixtures for E2E tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Generator,
    Iterator,
)
from pathlib import Path

import pytest
from flext_tests import tk

from tests import c, d, p, t, u

logger = u.fetch_logger(__name__)


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def sample_catalog() -> t.JsonMapping:
    """Create a sample Singer catalog for testing."""
    return {
        "streams": [
            {
                "tap_stream_id": "users",
                "schema": {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "uid": {"type": "string"},
                        "cn": {"type": "string"},
                    },
                },
                "metadata": [],
            },
        ],
    }


@pytest.fixture(scope="session")
def ldap_container(project_root: Path) -> Iterator[None]:
    """Start and manage LDAP test container using tk."""
    compose_file = project_root / "docker-compose.yml"
    docker = tk()
    logger.info("Starting OpenLDAP container...")
    start_result = docker.compose_up(compose_file=str(compose_file))
    if start_result.failure:
        logger.error(f"Failed to start OpenLDAP container: {start_result.error}")
        raise RuntimeError(f"Container startup failed: {start_result.error}")

    dc = c.Ldap.Tests

    @d.retry(max_attempts=30, delay_seconds=2.0, backoff_strategy="linear")
    def _check_ldap_ready() -> None:
        admin_dn, admin_password = u.Ldap.Tests.admin_credentials()
        server = u.Ldap.create_server(host="localhost", port=dc.PORT, get_info="ALL")
        conn = u.Ldap.create_connection(
            server,
            user=admin_dn,
            password=admin_password,
            auto_bind=True,
        )
        conn.unbind()

    _check_ldap_ready()
    logger.info("LDAP container is ready")
    yield
    logger.info("Stopping OpenLDAP container...")
    stop_result = docker.compose_down(compose_file=str(compose_file))
    if stop_result.failure:
        logger.warning(f"Failed to stop container cleanly: {stop_result.error}")


@pytest.fixture
def ldap_connection(_ldap_container: None) -> Generator[p.Ldap.Ldap3Connection]:
    """Create LDAP connection for testing."""
    dc = c.Ldap.Tests
    admin_dn, admin_password = u.Ldap.Tests.admin_credentials()
    server = u.Ldap.create_server(host="localhost", port=dc.PORT, get_info="ALL")
    conn = u.Ldap.create_connection(
        server,
        user=admin_dn,
        password=admin_password,
        auto_bind=True,
    )
    yield conn
    conn.unbind()


@pytest.fixture
def tap_config_file(tmp_path: Path, _ldap_container: None) -> Path:
    """Create tap configuration file for testing."""
    dc = c.Ldap.Tests
    admin_dn, admin_password = u.Ldap.Tests.admin_credentials()
    settings = {
        "ldap_host": "localhost",
        "ldap_port": dc.PORT,
        "bind_dn": admin_dn,
        "bind_password": admin_password,
        "base_dn": dc.BASE_DN,
        "page_size": 1000,
    }
    config_file = tmp_path / "tap_config.json"
    u.Cli.json_write(config_file, settings)
    return config_file


@pytest.fixture
def catalog_file(tmp_path: Path, sample_catalog: t.JsonMapping) -> Path:
    """Create catalog file for testing."""
    catalog_file = tmp_path / "catalog.json"
    u.Cli.json_write(catalog_file, sample_catalog)
    return catalog_file
