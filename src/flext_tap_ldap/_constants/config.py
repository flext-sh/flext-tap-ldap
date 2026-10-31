"""LDAP tap constants - configuration constants.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, Final

from flext_ldap import FlextLdapConstants

from flext_tap_ldap._constants import FlextTapLdapConstantsBase


class FlextTapLdapConstantsConfig(FlextTapLdapConstantsBase):
    """LDAP tap configuration constants."""

    # ClassVar, not Final: this plain mixin is composed into the
    # frozen pydantic config singleton, and pydantic 2.11 deprecates
    # final-annotated attributes with defaults collected as fields —
    # fatal under the fresh-import probe's -W error.
    CONFIG_DIR: ClassVar[str] = "config"

    DEFAULT_SEARCH_TIMEOUT: Final[int] = FlextLdapConstants.Ldap.TIMEOUT
    TAP_NAME: Final[str] = "tap-ldap"


# One declared module owner: the constants facade class. The config-values
# contract nests under it so the class-nesting contract sees a single owner.
__all__: list[str] = ["FlextTapLdapConstantsConfig"]
