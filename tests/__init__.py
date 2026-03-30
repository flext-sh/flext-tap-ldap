# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import *

    from tests import (
        conftest,
        constants,
        e2e,
        models,
        protocols,
        typings,
        unit,
        utilities,
    )
    from tests.conftest import *
    from tests.constants import *
    from tests.e2e import test_integration
    from tests.e2e.conftest import *
    from tests.e2e.test_integration import *
    from tests.models import *
    from tests.protocols import *
    from tests.typings import *
    from tests.unit import (
        test_client,
        test_client_quick,
        test_ldif_processor,
        test_ldif_stream,
        test_models,
        test_streams,
        test_tap,
    )
    from tests.unit.test_client import *
    from tests.unit.test_client_quick import *
    from tests.unit.test_ldif_processor import *
    from tests.unit.test_ldif_stream import *
    from tests.unit.test_models import *
    from tests.unit.test_streams import *
    from tests.unit.test_tap import *
    from tests.utilities import *

from tests.e2e import _LAZY_IMPORTS as _E2E_LAZY
from tests.unit import _LAZY_IMPORTS as _UNIT_LAZY

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    **_E2E_LAZY,
    **_UNIT_LAZY,
    "FlextTapLdapTestConstants": "tests.constants",
    "FlextTapLdapTestModels": "tests.models",
    "FlextTapLdapTestProtocols": "tests.protocols",
    "FlextTapLdapTestTypes": "tests.typings",
    "FlextTapLdapTestUtilities": "tests.utilities",
    "c": ["tests.constants", "FlextTapLdapTestConstants"],
    "conftest": "tests.conftest",
    "constants": "tests.constants",
    "d": "flext_tests",
    "e": "flext_tests",
    "e2e": "tests.e2e",
    "h": "flext_tests",
    "m": ["tests.models", "FlextTapLdapTestModels"],
    "models": "tests.models",
    "p": ["tests.protocols", "FlextTapLdapTestProtocols"],
    "protocols": "tests.protocols",
    "pytest_configure": "tests.conftest",
    "r": "flext_tests",
    "s": "flext_tests",
    "shared_ldap_container": "tests.conftest",
    "t": ["tests.typings", "FlextTapLdapTestTypes"],
    "test_data_dir": "tests.conftest",
    "typings": "tests.typings",
    "u": ["tests.utilities", "FlextTapLdapTestUtilities"],
    "unit": "tests.unit",
    "utilities": "tests.utilities",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
