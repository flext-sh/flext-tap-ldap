"""tap-ldap: Singer tap for LDAP data extraction.

This module implements a Singer tap for extracting data from LDAP directories
using the Singer SDK framework. It provides streams for users, groups, organizational
units, and schema information.

Architecture: Hexagonal Architecture - Port
Pattern: ETL Pipeline - Extract
Dependencies: singer-sdk, ldap3
"""

__version__ = "0.5.0"

# Import principais classes se existirem
try:
    from flext_tap_ldap.tap import TapLDAP
except ImportError:
    TapLDAP = None

__all__ = ["TapLDAP", "__version__"]
