# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import tests.conftest as _tests_conftest

    conftest = _tests_conftest
    import tests.constants as _tests_constants
    from tests.conftest import (
        pytest_configure,
        pytest_plugins,
        shared_ldap_container,
        tap_ldap_settings,
        test_data_dir,
    )

    constants = _tests_constants
    import tests.e2e as _tests_e2e
    from tests.constants import (
        FlextTapLdapTestConstants,
        FlextTapLdapTestConstants as c,
    )

    e2e = _tests_e2e
    import tests.models as _tests_models
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
    import tests.unit as _tests_unit
    from tests.typings import FlextTapLdapTestTypes, FlextTapLdapTestTypes as t

    unit = _tests_unit
    import tests.utilities as _tests_utilities
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
_LAZY_IMPORTS = merge_lazy_imports(
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
        "pytest_plugins": "tests.conftest",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "shared_ldap_container": "tests.conftest",
        "t": ("tests.typings", "FlextTapLdapTestTypes"),
        "tap_ldap_settings": "tests.conftest",
        "test_data_dir": "tests.conftest",
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextTapLdapTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

__all__ = [
    "FlextTapLdapTestConstants",
    "FlextTapLdapTestModels",
    "FlextTapLdapTestProtocols",
    "FlextTapLdapTestTypes",
    "FlextTapLdapTestUtilities",
    "TestConnectionTestedEvent",
    "TestCustomStream",
    "TestCustomStreamParams",
    "TestFlextTapLdapIntegration",
    "TestFlextTapLdapTapUnit",
    "TestGroupsStream",
    "TestLDAPBaseStream",
    "TestLDAPBaseStreamDirectUsage",
    "TestLDAPClientCoverageBoost",
    "TestLDAPClientQuick",
    "TestLDIFStreamBasic",
    "TestLdifProcessor",
    "TestOrganizationalUnitsStream",
    "TestRecordExtractedEvent",
    "TestSchemaStream",
    "TestStreamDiscoveredEvent",
    "TestStreamExceptionHandling",
    "TestStreamIntegration",
    "TestTapExecutionCompletedEvent",
    "TestTapExecutionStartedEvent",
    "TestUsersStream",
    "c",
    "catalog_file",
    "conftest",
    "constants",
    "d",
    "e",
    "e2e",
    "h",
    "ldap_connection",
    "ldap_container",
    "logger",
    "m",
    "models",
    "p",
    "project_root",
    "protocols",
    "pytest_configure",
    "pytest_plugins",
    "r",
    "s",
    "sample_catalog",
    "shared_ldap_container",
    "t",
    "tap_config_file",
    "tap_ldap_settings",
    "test_client",
    "test_client_quick",
    "test_data_dir",
    "test_integration",
    "test_ldif_processor",
    "test_ldif_stream",
    "test_models",
    "test_streams",
    "test_tap",
    "typings",
    "u",
    "unit",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
