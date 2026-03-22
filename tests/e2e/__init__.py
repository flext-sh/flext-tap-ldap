# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""E2E tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

    from .conftest import (
        catalog_file,
        ldap_connection,
        ldap_container,
        logger,
        project_root,
        sample_catalog,
        tap_config_file,
    )
    from .test_integration import TestFlextTapLdapIntegration

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestFlextTapLdapIntegration": (
        "tests.e2e.test_integration",
        "TestFlextTapLdapIntegration",
    ),
    "catalog_file": ("tests.e2e.conftest", "catalog_file"),
    "ldap_connection": ("tests.e2e.conftest", "ldap_connection"),
    "ldap_container": ("tests.e2e.conftest", "ldap_container"),
    "logger": ("tests.e2e.conftest", "logger"),
    "project_root": ("tests.e2e.conftest", "project_root"),
    "sample_catalog": ("tests.e2e.conftest", "sample_catalog"),
    "tap_config_file": ("tests.e2e.conftest", "tap_config_file"),
}

__all__ = [
    "TestFlextTapLdapIntegration",
    "catalog_file",
    "ldap_connection",
    "ldap_container",
    "logger",
    "project_root",
    "sample_catalog",
    "tap_config_file",
]


_LAZY_CACHE: dict[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
