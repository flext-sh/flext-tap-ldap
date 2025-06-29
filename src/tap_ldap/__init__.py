"""tap-ldap: Singer tap for LDAP data extraction.

This module implements a Singer tap for extracting data from LDAP directories
using the Singer SDK framework. It provides streams for users, groups, organizational
units, and schema information.

Architecture: Hexagonal Architecture - Port
Pattern: ETL Pipeline - Extract
Dependencies: singer-sdk, ldap3
"""

from tap_ldap.__version__ import __version__
from tap_ldap.tap import TapLDAP

__all__ = ["TapLDAP", "__version__"]
