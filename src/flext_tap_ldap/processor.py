"""Backward-compat re-exports — canonical location is u.TapLdap.*.

All classes moved to FlextTapLdapUtilities.TapLdap namespace:
- FlextLdifDistinguishedName -> u.TapLdap.DistinguishedName
- FlextTapLdapEntry          -> u.TapLdap.Entry
- FlextTapLdapProcessor      -> u.TapLdap.Processor
- FlextTapLdapValidator      -> u.TapLdap.Validator
- FlextTapLdapTransformer    -> u.TapLdap.Transformer

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_ldap import FlextTapLdapUtilities

FlextLdifDistinguishedName = FlextTapLdapUtilities.TapLdap.DistinguishedName
FlextTapLdapEntry = FlextTapLdapUtilities.TapLdap.Entry
FlextTapLdapProcessor = FlextTapLdapUtilities.TapLdap.Processor
FlextTapLdapValidator = FlextTapLdapUtilities.TapLdap.Validator
FlextTapLdapTransformer = FlextTapLdapUtilities.TapLdap.Transformer

__all__ = [
    "FlextLdifDistinguishedName",
    "FlextTapLdapEntry",
    "FlextTapLdapProcessor",
    "FlextTapLdapTransformer",
    "FlextTapLdapValidator",
]
