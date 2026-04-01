# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_tests import d, e, h, r, s, x

    from tests.conftest import *
    from tests.constants import *
    from tests.e2e import *
    from tests.models import *
    from tests.protocols import *
    from tests.typings import *
    from tests.unit import *
    from tests.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
    (
        "tests.e2e",
        "tests.unit",
    ),
    {
        "FlextTapLdapTestConstants": "tests.constants",
        "FlextTapLdapTestModels": "tests.models",
        "FlextTapLdapTestProtocols": "tests.protocols",
        "FlextTapLdapTestTypes": "tests.typings",
        "FlextTapLdapTestUtilities": "tests.utilities",
        "c": ("tests.constants", "FlextTapLdapTestConstants"),
        "conftest": "tests.conftest",
        "constants": "tests.constants",
        "d": "flext_tests",
        "e": "flext_tests",
        "e2e": "tests.e2e",
        "h": "flext_tests",
        "m": ("tests.models", "FlextTapLdapTestModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "FlextTapLdapTestProtocols"),
        "protocols": "tests.protocols",
        "pytest_configure": "tests.conftest",
        "r": "flext_tests",
        "s": "flext_tests",
        "shared_ldap_container": "tests.conftest",
        "t": ("tests.typings", "FlextTapLdapTestTypes"),
        "test_data_dir": "tests.conftest",
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextTapLdapTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": "flext_tests",
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
