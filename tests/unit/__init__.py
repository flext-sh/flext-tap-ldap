# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

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
