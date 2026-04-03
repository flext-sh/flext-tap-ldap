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
    from flext_tap_ldap import (
        conftest,
        constants,
        e2e,
        models,
        protocols,
        test_client,
        test_client_quick,
        test_integration,
        test_ldif_processor,
        test_ldif_stream,
        test_models,
        test_streams,
        test_tap,
        typings,
        unit,
        utilities,
    )
    from flext_tap_ldap.conftest import shared_ldap_container, test_data_dir
    from flext_tap_ldap.constants import (
        FlextTapLdapTestConstants,
        FlextTapLdapTestConstants as c,
    )
    from flext_tap_ldap.e2e import (
        catalog_file,
        ldap_connection,
        ldap_container,
        logger,
        project_root,
        sample_catalog,
        tap_config_file,
    )
    from flext_tap_ldap.models import (
        FlextTapLdapTestModels,
        FlextTapLdapTestModels as m,
    )
    from flext_tap_ldap.protocols import (
        FlextTapLdapTestProtocols,
        FlextTapLdapTestProtocols as p,
    )
    from flext_tap_ldap.typings import FlextTapLdapTestTypes, FlextTapLdapTestTypes as t
    from flext_tap_ldap.unit import (
        TestFlextTapLdapTapUnit,
        TestLDAPBaseStream,
        TestLDAPClientCoverageBoost,
        TestLDAPClientQuick,
        TestLdifProcessor,
        TestLDIFStreamBasic,
        TestTapExecutionStartedEvent,
        connection_config,
        raw_entries,
        result,
        source_type,
        source_version,
        stream_config,
        stream_entries,
        stream_names,
    )
    from flext_tap_ldap.utilities import (
        FlextTapLdapTestUtilities,
        FlextTapLdapTestUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
    (
        "flext_tap_ldap.e2e",
        "flext_tap_ldap.unit",
    ),
    {
        "FlextTapLdapTestConstants": "flext_tap_ldap.constants",
        "FlextTapLdapTestModels": "flext_tap_ldap.models",
        "FlextTapLdapTestProtocols": "flext_tap_ldap.protocols",
        "FlextTapLdapTestTypes": "flext_tap_ldap.typings",
        "FlextTapLdapTestUtilities": "flext_tap_ldap.utilities",
        "c": ("flext_tap_ldap.constants", "FlextTapLdapTestConstants"),
        "conftest": "flext_tap_ldap.conftest",
        "constants": "flext_tap_ldap.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "e2e": "flext_tap_ldap.e2e",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("flext_tap_ldap.models", "FlextTapLdapTestModels"),
        "models": "flext_tap_ldap.models",
        "p": ("flext_tap_ldap.protocols", "FlextTapLdapTestProtocols"),
        "protocols": "flext_tap_ldap.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "shared_ldap_container": "flext_tap_ldap.conftest",
        "t": ("flext_tap_ldap.typings", "FlextTapLdapTestTypes"),
        "test_client": "flext_tap_ldap.test_client",
        "test_client_quick": "flext_tap_ldap.test_client_quick",
        "test_data_dir": "flext_tap_ldap.conftest",
        "test_integration": "flext_tap_ldap.test_integration",
        "test_ldif_processor": "flext_tap_ldap.test_ldif_processor",
        "test_ldif_stream": "flext_tap_ldap.test_ldif_stream",
        "test_models": "flext_tap_ldap.test_models",
        "test_streams": "flext_tap_ldap.test_streams",
        "test_tap": "flext_tap_ldap.test_tap",
        "typings": "flext_tap_ldap.typings",
        "u": ("flext_tap_ldap.utilities", "FlextTapLdapTestUtilities"),
        "unit": "flext_tap_ldap.unit",
        "utilities": "flext_tap_ldap.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
