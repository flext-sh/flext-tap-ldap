"""Pytest fixtures for E2E tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import time
from collections.abc import Generator, Iterator
from pathlib import Path

import pytest
from flext_core import FlextLogger, FlextTypes as t
from flext_tests import FlextTestsDocker
from ldap3 import ALL, Connection, Server

logger = FlextLogger(__name__)


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def sample_catalog() -> dict[str, t.GeneralValueType]:
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
    """Start and manage LDAP test container using FlextTestsDocker."""
    compose_file = project_root / "docker-compose.yml"
    logger.info("Starting OpenLDAP container...")

    # Use FlextTestsDocker for unified Docker management
    docker_manager = FlextTestsDocker(workspace_root=project_root)

    # Start containers using FlextTestsDocker
    start_result = docker_manager.compose_up(compose_file=str(compose_file))

    if start_result.is_failure:
        logger.error(f"Failed to start OpenLDAP container: {start_result.error}")
        raise RuntimeError(f"Container startup failed: {start_result.error}")

    # Wait for LDAP to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            server = Server("localhost", port=10389, get_info=ALL)
            conn = Connection(
                server,
                user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
                password="REDACTED_LDAP_BIND_PASSWORD_password",
                auto_bind=True,
            )
            conn.unbind()
            logger.info("LDAP container is ready")
            break
        except (RuntimeError, ValueError, TypeError):
            if i == max_retries - 1:
                logger.exception("LDAP container failed to start")
                raise
            logger.info("Waiting for LDAP container to be ready...")
            time.sleep(2)
    yield
    # Cleanup
    logger.info("Stopping OpenLDAP container...")
    stop_result = docker_manager.compose_down(compose_file=str(compose_file))
    if stop_result.is_failure:
        logger.warning(f"Failed to stop container cleanly: {stop_result.error}")


@pytest.fixture
def ldap_connection(_ldap_container: None) -> Generator[Connection]:
    """Create LDAP connection for testing."""
    server = Server("localhost", port=10389, get_info=ALL)
    conn = Connection(
        server,
        user="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
        password="REDACTED_LDAP_BIND_PASSWORD_password",
        auto_bind=True,
    )
    yield conn
    conn.unbind()


@pytest.fixture
def tap_config_file(tmp_path: Path, _ldap_container: None) -> Path:
    """Create tap configuration file for testing."""
    config = {
        "ldap_host": "localhost",
        "ldap_port": 10389,
        "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
        "bind_password": "REDACTED_LDAP_BIND_PASSWORD_password",
        "base_dn": "dc=test,dc=com",
        "page_size": 1000,
    }
    config_file = tmp_path / "tap_config.json"
    config_file.write_text(json.dumps(config, indent=2))
    return config_file


@pytest.fixture
def catalog_file(tmp_path: Path, sample_catalog: dict[str, t.GeneralValueType]) -> Path:
    """Create catalog file for testing."""
    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(json.dumps(sample_catalog, indent=2))
    return catalog_file
