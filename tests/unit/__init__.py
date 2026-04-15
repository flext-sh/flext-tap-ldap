# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_client": ("test_client",),
        ".test_client_quick": ("test_client_quick",),
        ".test_ldif_processor": ("test_ldif_processor",),
        ".test_ldif_stream": ("test_ldif_stream",),
        ".test_models": ("test_models",),
        ".test_streams": ("test_streams",),
        ".test_tap": ("test_tap",),
        "flext_tap_ldap": (
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
        ),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
