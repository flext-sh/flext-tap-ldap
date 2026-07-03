# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_ldap.tests.unit.test_client import (
        TestsFlextTapLdapClient as TestsFlextTapLdapClient,
    )
    from flext_tap_ldap.tests.unit.test_client_quick import (
        TestsFlextTapLdapClientQuick as TestsFlextTapLdapClientQuick,
    )
    from flext_tap_ldap.tests.unit.test_ldif_processor import (
        TestsFlextTapLdapLdifProcessor as TestsFlextTapLdapLdifProcessor,
    )
    from flext_tap_ldap.tests.unit.test_ldif_stream import (
        TestsFlextTapLdapLdifStream as TestsFlextTapLdapLdifStream,
    )
    from flext_tap_ldap.tests.unit.test_models import (
        TestsFlextTapLdapModelsUnit as TestsFlextTapLdapModelsUnit,
    )
    from flext_tap_ldap.tests.unit.test_tap import (
        TestsFlextTapLdapTap as TestsFlextTapLdapTap,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_client": ("TestsFlextTapLdapClient",),
        ".test_client_quick": ("TestsFlextTapLdapClientQuick",),
        ".test_ldif_processor": ("TestsFlextTapLdapLdifProcessor",),
        ".test_ldif_stream": ("TestsFlextTapLdapLdifStream",),
        ".test_models": ("TestsFlextTapLdapModelsUnit",),
        ".test_tap": ("TestsFlextTapLdapTap",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
