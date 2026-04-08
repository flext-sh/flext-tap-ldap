# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.conftest as _tests_conftest

    conftest = _tests_conftest
    import tests.constants as _tests_constants
    from tests.conftest import pytest_configure, pytest_plugins

    constants = _tests_constants
    import tests.models as _tests_models
    from tests.constants import (
        FlextTapLdapTestConstants,
        FlextTapLdapTestConstants as c,
    )
    from tests.e2e.conftest import logger

    models = _tests_models
    import tests.protocols as _tests_protocols
    from tests.models import FlextTapLdapTestModels, FlextTapLdapTestModels as m

    protocols = _tests_protocols
    import tests.typings as _tests_typings
    from tests.protocols import (
        FlextTapLdapTestProtocols,
        FlextTapLdapTestProtocols as p,
    )

    typings = _tests_typings
    import tests.utilities as _tests_utilities
    from tests.typings import FlextTapLdapTestTypes, FlextTapLdapTestTypes as t
    from tests.unit.test_tap import config

    utilities = _tests_utilities
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.utilities import (
        FlextTapLdapTestUtilities,
        FlextTapLdapTestUtilities as u,
    )
_LAZY_IMPORTS = {
    "FlextTapLdapTestConstants": ("tests.constants", "FlextTapLdapTestConstants"),
    "FlextTapLdapTestModels": ("tests.models", "FlextTapLdapTestModels"),
    "FlextTapLdapTestProtocols": ("tests.protocols", "FlextTapLdapTestProtocols"),
    "FlextTapLdapTestTypes": ("tests.typings", "FlextTapLdapTestTypes"),
    "FlextTapLdapTestUtilities": ("tests.utilities", "FlextTapLdapTestUtilities"),
    "c": ("tests.constants", "FlextTapLdapTestConstants"),
    "config": ("tests.unit.test_tap", "config"),
    "conftest": "tests.conftest",
    "constants": "tests.constants",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "logger": ("tests.e2e.conftest", "logger"),
    "m": ("tests.models", "FlextTapLdapTestModels"),
    "models": "tests.models",
    "p": ("tests.protocols", "FlextTapLdapTestProtocols"),
    "protocols": "tests.protocols",
    "pytest_configure": ("tests.conftest", "pytest_configure"),
    "pytest_plugins": ("tests.conftest", "pytest_plugins"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("tests.typings", "FlextTapLdapTestTypes"),
    "typings": "tests.typings",
    "u": ("tests.utilities", "FlextTapLdapTestUtilities"),
    "utilities": "tests.utilities",
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "FlextTapLdapTestConstants",
    "FlextTapLdapTestModels",
    "FlextTapLdapTestProtocols",
    "FlextTapLdapTestTypes",
    "FlextTapLdapTestUtilities",
    "c",
    "config",
    "conftest",
    "constants",
    "d",
    "e",
    "h",
    "logger",
    "m",
    "models",
    "p",
    "protocols",
    "pytest_configure",
    "pytest_plugins",
    "r",
    "s",
    "t",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
