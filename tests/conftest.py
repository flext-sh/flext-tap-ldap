"""Configuração pytest para flext-tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock

import pytest


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
