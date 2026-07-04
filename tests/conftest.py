"""Configuração pytest para flext-tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.constants import c
from tests.models import m

if TYPE_CHECKING:
    from tests.typings import t


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
        },
    ]
