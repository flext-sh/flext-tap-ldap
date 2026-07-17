"""CLI entrypoint for flext-tap-ldap — canonical ``cli:main`` bridge.

Dispatches the flat Singer CLI (``--config`` / ``--discover`` / ``--catalog`` /
``--state``) through the declarative service's ``cli_main`` provided by
``meltano.Tap``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_ldap import t
from flext_tap_ldap.api import FlextTapLdapService


def main(args: t.StrSequence | None = None) -> int:
    """Run the canonical tap-ldap Singer CLI."""
    return FlextTapLdapService().cli_main(args)


__all__: list[str] = ["main"]
