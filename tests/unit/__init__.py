# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
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
    from flext_tap_ldap import (
        test_client,
        test_client_quick,
        test_ldif_processor,
        test_ldif_stream,
        test_models,
        test_streams,
        test_tap,
    )
    from flext_tap_ldap.test_client import TestLDAPClientCoverageBoost
    from flext_tap_ldap.test_client_quick import TestLDAPClientQuick
    from flext_tap_ldap.test_ldif_processor import TestLdifProcessor
    from flext_tap_ldap.test_ldif_stream import TestLDIFStreamBasic
    from flext_tap_ldap.test_models import TestTapExecutionStartedEvent
    from flext_tap_ldap.test_streams import TestLDAPBaseStream
    from flext_tap_ldap.test_tap import (
        TestFlextTapLdapTapUnit,
        connection_config,
        raw_entries,
        result,
        source_type,
        source_version,
        stream_config,
        stream_entries,
        stream_names,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "TestFlextTapLdapTapUnit": "flext_tap_ldap.test_tap",
    "TestLDAPBaseStream": "flext_tap_ldap.test_streams",
    "TestLDAPClientCoverageBoost": "flext_tap_ldap.test_client",
    "TestLDAPClientQuick": "flext_tap_ldap.test_client_quick",
    "TestLDIFStreamBasic": "flext_tap_ldap.test_ldif_stream",
    "TestLdifProcessor": "flext_tap_ldap.test_ldif_processor",
    "TestTapExecutionStartedEvent": "flext_tap_ldap.test_models",
    "c": ("flext_core.constants", "FlextConstants"),
    "connection_config": "flext_tap_ldap.test_tap",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "raw_entries": "flext_tap_ldap.test_tap",
    "result": "flext_tap_ldap.test_tap",
    "s": ("flext_core.service", "FlextService"),
    "source_type": "flext_tap_ldap.test_tap",
    "source_version": "flext_tap_ldap.test_tap",
    "stream_config": "flext_tap_ldap.test_tap",
    "stream_entries": "flext_tap_ldap.test_tap",
    "stream_names": "flext_tap_ldap.test_tap",
    "t": ("flext_core.typings", "FlextTypes"),
    "test_client": "flext_tap_ldap.test_client",
    "test_client_quick": "flext_tap_ldap.test_client_quick",
    "test_ldif_processor": "flext_tap_ldap.test_ldif_processor",
    "test_ldif_stream": "flext_tap_ldap.test_ldif_stream",
    "test_models": "flext_tap_ldap.test_models",
    "test_streams": "flext_tap_ldap.test_streams",
    "test_tap": "flext_tap_ldap.test_tap",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
