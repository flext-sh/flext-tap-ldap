# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""E2e package."""

from __future__ import annotations

import typing as _t

from flext_core.constants import FlextConstants as c
from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports
from flext_core.mixins import FlextMixins as x
from flext_core.models import FlextModels as m
from flext_core.protocols import FlextProtocols as p
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from flext_core.typings import FlextTypes as t
from flext_core.utilities import FlextUtilities as u
from tests.e2e.conftest import (
    catalog_file,
    ldap_connection,
    ldap_container,
    logger,
    project_root,
    sample_catalog,
    tap_config_file,
)
from tests.e2e.test_integration import TestFlextTapLdapIntegration

if _t.TYPE_CHECKING:
    import tests.e2e.conftest as _tests_e2e_conftest

    conftest = _tests_e2e_conftest
    import tests.e2e.test_integration as _tests_e2e_test_integration

    test_integration = _tests_e2e_test_integration

    _ = (
        TestFlextTapLdapIntegration,
        c,
        catalog_file,
        conftest,
        d,
        e,
        h,
        ldap_connection,
        ldap_container,
        logger,
        m,
        p,
        project_root,
        r,
        s,
        sample_catalog,
        t,
        tap_config_file,
        test_integration,
        u,
        x,
    )
_LAZY_IMPORTS = {
    "TestFlextTapLdapIntegration": "tests.e2e.test_integration",
    "c": ("flext_core.constants", "FlextConstants"),
    "catalog_file": "tests.e2e.conftest",
    "conftest": "tests.e2e.conftest",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "ldap_connection": "tests.e2e.conftest",
    "ldap_container": "tests.e2e.conftest",
    "logger": "tests.e2e.conftest",
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "project_root": "tests.e2e.conftest",
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "sample_catalog": "tests.e2e.conftest",
    "t": ("flext_core.typings", "FlextTypes"),
    "tap_config_file": "tests.e2e.conftest",
    "test_integration": "tests.e2e.test_integration",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestFlextTapLdapIntegration",
    "c",
    "catalog_file",
    "conftest",
    "d",
    "e",
    "h",
    "ldap_connection",
    "ldap_container",
    "logger",
    "m",
    "p",
    "project_root",
    "r",
    "s",
    "sample_catalog",
    "t",
    "tap_config_file",
    "test_integration",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
