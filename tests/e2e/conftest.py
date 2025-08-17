"""Pytest fixtures for E2E tests."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Generator, Iterator
from pathlib import Path

import pytest
import structlog
from ldap3 import ALL, Connection, Server

logger = structlog.get_logger()


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def sample_catalog() -> dict[str, object]:
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
    """Start and manage LDAP test container."""
    compose_file = project_root / "docker-compose.yml"
    # Start containers
    logger.info("Starting OpenLDAP container...")

    async def _run(
      cmd_list: list[str],
      cwd: str | None = None,
      timeout_seconds: int = 120,
    ) -> int:
      process = await asyncio.create_subprocess_exec(
          *cmd_list,
          cwd=cwd,
          stdout=asyncio.subprocess.PIPE,
          stderr=asyncio.subprocess.PIPE,
      )
      try:
          async with asyncio.timeout(timeout_seconds):
              await process.communicate()
      except TimeoutError:
          process.kill()
          await process.communicate()
          raise
      return process.returncode

    asyncio.run(
      _run(
          ["/usr/bin/env", "docker-compose", "-f", str(compose_file), "up", "-d"],
          cwd=str(project_root),
      ),
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
    asyncio.run(
      _run(
          ["/usr/bin/env", "docker-compose", "-f", str(compose_file), "down", "-v"],
          cwd=str(project_root),
      ),
    )


@pytest.fixture
def ldap_connection(ldap_container: None) -> Generator[Connection]:  # noqa: ARG001
    """Create LDAP connection for testing."""
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
def tap_config_file(tmp_path: Path, ldap_container: None) -> Path:  # noqa: ARG001
    """Create tap configuration file for testing."""
    config = {
      "ldap_host": "localhost",
      "ldap_port": 10389,
      "bind_dn": "cn=admin,dc=test,dc=com",
      "bind_password": "admin_password",
      "base_dn": "dc=test,dc=com",
      "page_size": 1000,
    }
    config_file = tmp_path / "tap_config.json"
    config_file.write_text(json.dumps(config, indent=2))
    return config_file


@pytest.fixture
def catalog_file(tmp_path: Path, sample_catalog: dict[str, object]) -> Path:
    """Create catalog file for testing."""
    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(json.dumps(sample_catalog, indent=2))
    return catalog_file
