# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
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

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "TestConnectionTestedEvent": "tests.unit.test_models",
    "TestCustomStream": "tests.unit.test_streams",
    "TestCustomStreamParams": "tests.unit.test_streams",
    "TestFlextTapLdapTapUnit": "tests.unit.test_tap",
    "TestGroupsStream": "tests.unit.test_streams",
    "TestLDAPBaseStream": "tests.unit.test_streams",
    "TestLDAPBaseStreamDirectUsage": "tests.unit.test_streams",
    "TestLDAPClientCoverageBoost": "tests.unit.test_client",
    "TestLDAPClientQuick": "tests.unit.test_client_quick",
    "TestLDIFStreamBasic": "tests.unit.test_ldif_stream",
    "TestLdifProcessor": "tests.unit.test_ldif_processor",
    "TestOrganizationalUnitsStream": "tests.unit.test_streams",
    "TestRecordExtractedEvent": "tests.unit.test_models",
    "TestSchemaStream": "tests.unit.test_streams",
    "TestStreamDiscoveredEvent": "tests.unit.test_models",
    "TestStreamExceptionHandling": "tests.unit.test_streams",
    "TestStreamIntegration": "tests.unit.test_streams",
    "TestTapExecutionCompletedEvent": "tests.unit.test_models",
    "TestTapExecutionStartedEvent": "tests.unit.test_models",
    "TestUsersStream": "tests.unit.test_streams",
    "test_client": "tests.unit.test_client",
    "test_client_quick": "tests.unit.test_client_quick",
    "test_ldif_processor": "tests.unit.test_ldif_processor",
    "test_ldif_stream": "tests.unit.test_ldif_stream",
    "test_models": "tests.unit.test_models",
    "test_streams": "tests.unit.test_streams",
    "test_tap": "tests.unit.test_tap",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
