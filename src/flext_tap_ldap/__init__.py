"""tap-ldap: Singer tap for LDAP data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.

This module implements a Singer tap for extracting data from LDAP directories
using the Singer SDK framework. It provides streams for users, groups, organizational
units, and schema information.

Architecture:
            Hexagonal Architecture - Port
Pattern: ETL Pipeline - Extract
Dependencies: singer-sdk, ldap3
"""

from __future__ import annotations

import importlib.metadata

try:
    __version__ = importlib.metadata.version("flext-tap-ldap")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# Import main classes using flext-core patterns
from flext_tap_ldap.tap import TapLDAP

__all__ = ["TapLDAP", "__version__", "__version_info__"]
