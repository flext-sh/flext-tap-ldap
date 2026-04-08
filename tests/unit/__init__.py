# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.unit.test_client as _tests_unit_test_client

    test_client = _tests_unit_test_client
    import tests.unit.test_client_quick as _tests_unit_test_client_quick

    test_client_quick = _tests_unit_test_client_quick
    import tests.unit.test_ldif_processor as _tests_unit_test_ldif_processor

    test_ldif_processor = _tests_unit_test_ldif_processor
    import tests.unit.test_ldif_stream as _tests_unit_test_ldif_stream

    test_ldif_stream = _tests_unit_test_ldif_stream
    import tests.unit.test_models as _tests_unit_test_models

    test_models = _tests_unit_test_models
    import tests.unit.test_streams as _tests_unit_test_streams

    test_streams = _tests_unit_test_streams
    import tests.unit.test_tap as _tests_unit_test_tap

    test_tap = _tests_unit_test_tap
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
_LAZY_IMPORTS = {
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "test_client": "tests.unit.test_client",
    "test_client_quick": "tests.unit.test_client_quick",
    "test_ldif_processor": "tests.unit.test_ldif_processor",
    "test_ldif_stream": "tests.unit.test_ldif_stream",
    "test_models": "tests.unit.test_models",
    "test_streams": "tests.unit.test_streams",
    "test_tap": "tests.unit.test_tap",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "test_client",
    "test_client_quick",
    "test_ldif_processor",
    "test_ldif_stream",
    "test_models",
    "test_streams",
    "test_tap",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
