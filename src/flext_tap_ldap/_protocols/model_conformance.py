# AUTO-GENERATED FILE — Regenerate with: make gen
"""Static instance-to-protocol evidence required by candidate admission.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_tap_ldap/_protocols/model_conformance
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_tap_ldap import FlextTapLdapModels, FlextTapLdapProtocols

    def model_protocol_1(
        value: (FlextTapLdapModels.TapLdap.ConfigNamespace),
    ) -> FlextTapLdapProtocols.TapLdap.ConfigNamespace:
        return value

    def model_protocol_2(
        value: (FlextTapLdapModels.TapLdap.Root),
    ) -> FlextTapLdapProtocols.TapLdap.Root:
        return value

    def model_protocol_3(
        value: (FlextTapLdapModels.TapLdap.TapLdap),
    ) -> FlextTapLdapProtocols.TapLdap.TapLdap:
        return value

    def model_protocol_4(
        value: (FlextTapLdapModels.TapLdap.TapLdap.StreamRule),
    ) -> FlextTapLdapProtocols.TapLdap.TapLdapStreamRule:
        return value
