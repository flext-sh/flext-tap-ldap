"""Test module for flext-tap-ldap.

This module provides test infrastructure for flext-tap-ldap using unified namespace patterns.
Test objects are accessed via m.TapLdap.Tests.*, u.TapLdap.*, etc.
Combines FlextTests* with project-specific functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

# Import test module aliases for unified test access
from .models import m
from .protocols import p
from .typings import t
from .utilities import u

__all__ = [
    "m",
    "p",
    "t",
    "u",
]
