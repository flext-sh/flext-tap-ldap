"""Pytest fixtures for E2E tests."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
import structlog
from ldap3 import ALL, Connection, Server

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator
logger = structlog.get_logger()


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def sample_catalog() -> dict[str, object]:
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
    compose_file = project_root / "docker-compose.yml"
    # Start containers
    logger.info("Starting OpenLDAP container...")
    subprocess.run(
        ["docker-compose", "-f", str(compose_file), "up", "-d"],
        check=True,
        cwd=str(project_root),
    )
    # Wait for LDAP to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            server = Server("localhost", port=10389, get_info=ALL)
            conn = Connection(
                server,
                user="cn=admin,dc=test,dc=com",
                password="admin_password",
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
    subprocess.run(
        ["docker-compose", "-f", str(compose_file), "down", "-v"],
        check=True,
        cwd=str(project_root),
    )


@pytest.fixture
def ldap_connection(ldap_container: Any) -> Generator[Connection]:
    server = Server("localhost", port=10389, get_info=ALL)
    conn = Connection(
        server,
        user="cn=admin,dc=test,dc=com",
        password="admin_password",
        auto_bind=True,
    )
    yield conn
    conn.unbind()


@pytest.fixture
def tap_config_file(tmp_path: Path, ldap_container: Any) -> Path:
    config = {
        "host": "localhost",
        "port": 10389,
        "bind_dn": "cn=admin,dc=test,dc=com",
        "password": "admin_password",
        "base_dn": "dc=test,dc=com",
        "timeout": 30,
        "page_size": 1000,
    }
    config_file = tmp_path / "tap_config.json"
    config_file.write_text(json.dumps(config, indent=2))
    return config_file


@pytest.fixture
def catalog_file(tmp_path: Path, sample_catalog: dict[str, object]) -> Path:
    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(json.dumps(sample_catalog, indent=2))
    return catalog_file
