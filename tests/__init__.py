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
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
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
    from tests.conftest import pytest_configure, shared_ldap_container, test_data_dir
    from tests.constants import (
        FlextTapLdapTestConstants,
        FlextTapLdapTestConstants as c,
    )
    from tests.e2e import (
        TestFlextTapLdapIntegration,
        catalog_file,
        ldap_connection,
        ldap_container,
        logger,
        project_root,
        sample_catalog,
        tap_config_file,
        test_integration,
    )
    from tests.models import FlextTapLdapTestModels, FlextTapLdapTestModels as m
    from tests.protocols import (
        FlextTapLdapTestProtocols,
        FlextTapLdapTestProtocols as p,
    )
    from tests.typings import FlextTapLdapTestTypes, FlextTapLdapTestTypes as t
    from tests.unit import (
        TestConnectionTestedEvent,
        TestCustomStream,
        TestCustomStreamParams,
        TestFlextTapLdapTapUnit,
        TestGroupsStream,
        TestLDAPBaseStream,
        TestLDAPBaseStreamDirectUsage,
        TestLDAPClientCoverageBoost,
        TestLDAPClientQuick,
        TestLdifProcessor,
        TestLDIFStreamBasic,
        TestOrganizationalUnitsStream,
        TestRecordExtractedEvent,
        TestSchemaStream,
        TestStreamDiscoveredEvent,
        TestStreamExceptionHandling,
        TestStreamIntegration,
        TestTapExecutionCompletedEvent,
        TestTapExecutionStartedEvent,
        TestUsersStream,
        test_client,
        test_client_quick,
        test_ldif_processor,
        test_ldif_stream,
        test_models,
        test_streams,
        test_tap,
    )
    from tests.utilities import (
        FlextTapLdapTestUtilities,
        FlextTapLdapTestUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
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
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "e2e": "tests.e2e",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("tests.models", "FlextTapLdapTestModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "FlextTapLdapTestProtocols"),
        "protocols": "tests.protocols",
        "pytest_configure": "tests.conftest",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "shared_ldap_container": "tests.conftest",
        "t": ("tests.typings", "FlextTapLdapTestTypes"),
        "test_data_dir": "tests.conftest",
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextTapLdapTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
