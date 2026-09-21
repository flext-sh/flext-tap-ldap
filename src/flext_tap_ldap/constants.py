"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_ldap import c
from flext_meltano import c as meltano_c

from ._constants import FlextTapLdapConstantsConfig as _PrivateFlextTapLdapConstants


class FlextTapLdapConstants(_PrivateFlextTapLdapConstants, c, meltano_c):
    """LDAP tap extraction-specific constants following FLEXT unified pattern.

    Inherits from FlextMeltanoConstants for universal constants, defines only
    LDAP tap-specific constants using nested namespace classes.

    Composes with FlextLdapConstants to avoid duplication and ensure consistency.
    """

    class TapLdap(_PrivateFlextTapLdapConstants.TapLdap):
        """Tap LDAP namespace for cross-project access.

        LDAP-generic constants are inherited from c.Ldap via MRO:
        - c.Ldap.PORT (389)
        - c.Ldap.TIMEOUT (30)

        Meltano-generic constants are inherited from c.Meltano via MRO:
        - c.DEFAULT_BATCH_SIZE (page size)
        """


c = FlextTapLdapConstants
__all__: list[str] = ["FlextTapLdapConstants", "c"]
