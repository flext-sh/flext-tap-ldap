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

__version__ = "0.7.0"

# Import main classes using flext-core patterns
from flext_tap_ldap.tap import TapLDAP

__all__ = ["TapLDAP", "__version__"]
