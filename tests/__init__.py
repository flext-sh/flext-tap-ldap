# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.constants import (
        TestsFlextTapLdapConstants,
        TestsFlextTapLdapConstants as c,
    )
    from tests.models import TestsFlextTapLdapModels, TestsFlextTapLdapModels as m
    from tests.protocols import (
        TestsFlextTapLdapProtocols,
        TestsFlextTapLdapProtocols as p,
    )
    from tests.typings import TestsFlextTapLdapTypes, TestsFlextTapLdapTypes as t
    from tests.utilities import (
        TestsFlextTapLdapUtilities,
        TestsFlextTapLdapUtilities as u,
    )
_LAZY_IMPORTS = {
    "TestsFlextTapLdapConstants": ("tests.constants", "TestsFlextTapLdapConstants"),
    "TestsFlextTapLdapModels": ("tests.models", "TestsFlextTapLdapModels"),
    "TestsFlextTapLdapProtocols": ("tests.protocols", "TestsFlextTapLdapProtocols"),
    "TestsFlextTapLdapTypes": ("tests.typings", "TestsFlextTapLdapTypes"),
    "TestsFlextTapLdapUtilities": ("tests.utilities", "TestsFlextTapLdapUtilities"),
    "c": ("tests.constants", "TestsFlextTapLdapConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("tests.models", "TestsFlextTapLdapModels"),
    "p": ("tests.protocols", "TestsFlextTapLdapProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("tests.typings", "TestsFlextTapLdapTypes"),
    "u": ("tests.utilities", "TestsFlextTapLdapUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestsFlextTapLdapConstants",
    "TestsFlextTapLdapModels",
    "TestsFlextTapLdapProtocols",
    "TestsFlextTapLdapTypes",
    "TestsFlextTapLdapUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
