# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext tap ldap package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_tap_ldap.__version__ import *

if _t.TYPE_CHECKING:
    import flext_tap_ldap._utilities as _flext_tap_ldap__utilities

    _utilities = _flext_tap_ldap__utilities
    import flext_tap_ldap.api as _flext_tap_ldap_api
    from flext_tap_ldap._utilities import FlextTapLdapUtilitiesProcessorMixin

    api = _flext_tap_ldap_api
    import flext_tap_ldap.client as _flext_tap_ldap_client
    from flext_tap_ldap.api import FlextTapLdapService, FlextTapLdapService as s

    client = _flext_tap_ldap_client
    import flext_tap_ldap.constants as _flext_tap_ldap_constants
    from flext_tap_ldap.client import FlextTapLdapClient

    constants = _flext_tap_ldap_constants
    import flext_tap_ldap.ldif_streams as _flext_tap_ldap_ldif_streams
    from flext_tap_ldap.constants import (
        FlextTapLdapConstants,
        FlextTapLdapConstants as c,
    )

    ldif_streams = _flext_tap_ldap_ldif_streams
    import flext_tap_ldap.models as _flext_tap_ldap_models
    from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams

    models = _flext_tap_ldap_models
    import flext_tap_ldap.processor as _flext_tap_ldap_processor
    from flext_tap_ldap.models import FlextTapLdapModels, FlextTapLdapModels as m

    processor = _flext_tap_ldap_processor
    import flext_tap_ldap.protocols as _flext_tap_ldap_protocols
    from flext_tap_ldap.processor import (
        FlextLdifDistinguishedName,
        FlextTapLdapEntry,
        FlextTapLdapProcessor,
        FlextTapLdapTransformer,
        FlextTapLdapValidator,
    )

    protocols = _flext_tap_ldap_protocols
    import flext_tap_ldap.services as _flext_tap_ldap_services
    from flext_tap_ldap.protocols import (
        FlextTapLdapProtocols,
        FlextTapLdapProtocols as p,
    )

    services = _flext_tap_ldap_services
    import flext_tap_ldap.settings as _flext_tap_ldap_settings
    from flext_tap_ldap.services import FlextTapLdapServices

    settings = _flext_tap_ldap_settings
    import flext_tap_ldap.streams as _flext_tap_ldap_streams
    from flext_tap_ldap.settings import FlextTapLdapSettings

    streams = _flext_tap_ldap_streams
    import flext_tap_ldap.tap as _flext_tap_ldap_tap
    from flext_tap_ldap.streams import FlextTapLdapStreams

    tap = _flext_tap_ldap_tap
    import flext_tap_ldap.typings as _flext_tap_ldap_typings
    from flext_tap_ldap.tap import CLI_COMMAND, FlextTapLdapTap, logger, main

    typings = _flext_tap_ldap_typings
    import flext_tap_ldap.utilities as _flext_tap_ldap_utilities
    from flext_tap_ldap.typings import FlextTapLdapTypes, FlextTapLdapTypes as t

    utilities = _flext_tap_ldap_utilities
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_tap_ldap.utilities import (
        FlextTapLdapUtilities,
        FlextTapLdapUtilities as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    ("flext_tap_ldap._utilities",),
    {
        "CLI_COMMAND": "flext_tap_ldap.tap",
        "FlextLdifDistinguishedName": "flext_tap_ldap.processor",
        "FlextTapLdapClient": "flext_tap_ldap.client",
        "FlextTapLdapConstants": "flext_tap_ldap.constants",
        "FlextTapLdapEntry": "flext_tap_ldap.processor",
        "FlextTapLdapLdifStreams": "flext_tap_ldap.ldif_streams",
        "FlextTapLdapModels": "flext_tap_ldap.models",
        "FlextTapLdapProcessor": "flext_tap_ldap.processor",
        "FlextTapLdapProtocols": "flext_tap_ldap.protocols",
        "FlextTapLdapService": "flext_tap_ldap.api",
        "FlextTapLdapServices": "flext_tap_ldap.services",
        "FlextTapLdapSettings": "flext_tap_ldap.settings",
        "FlextTapLdapStreams": "flext_tap_ldap.streams",
        "FlextTapLdapTap": "flext_tap_ldap.tap",
        "FlextTapLdapTransformer": "flext_tap_ldap.processor",
        "FlextTapLdapTypes": "flext_tap_ldap.typings",
        "FlextTapLdapUtilities": "flext_tap_ldap.utilities",
        "FlextTapLdapValidator": "flext_tap_ldap.processor",
        "__author__": "flext_tap_ldap.__version__",
        "__author_email__": "flext_tap_ldap.__version__",
        "__description__": "flext_tap_ldap.__version__",
        "__license__": "flext_tap_ldap.__version__",
        "__title__": "flext_tap_ldap.__version__",
        "__url__": "flext_tap_ldap.__version__",
        "__version__": "flext_tap_ldap.__version__",
        "__version_info__": "flext_tap_ldap.__version__",
        "_utilities": "flext_tap_ldap._utilities",
        "api": "flext_tap_ldap.api",
        "c": ("flext_tap_ldap.constants", "FlextTapLdapConstants"),
        "client": "flext_tap_ldap.client",
        "constants": "flext_tap_ldap.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "ldif_streams": "flext_tap_ldap.ldif_streams",
        "logger": "flext_tap_ldap.tap",
        "m": ("flext_tap_ldap.models", "FlextTapLdapModels"),
        "main": "flext_tap_ldap.tap",
        "models": "flext_tap_ldap.models",
        "p": ("flext_tap_ldap.protocols", "FlextTapLdapProtocols"),
        "processor": "flext_tap_ldap.processor",
        "protocols": "flext_tap_ldap.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_tap_ldap.api", "FlextTapLdapService"),
        "services": "flext_tap_ldap.services",
        "settings": "flext_tap_ldap.settings",
        "streams": "flext_tap_ldap.streams",
        "t": ("flext_tap_ldap.typings", "FlextTapLdapTypes"),
        "tap": "flext_tap_ldap.tap",
        "typings": "flext_tap_ldap.typings",
        "u": ("flext_tap_ldap.utilities", "FlextTapLdapUtilities"),
        "utilities": "flext_tap_ldap.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

__all__ = [
    "CLI_COMMAND",
    "FlextLdifDistinguishedName",
    "FlextTapLdapClient",
    "FlextTapLdapConstants",
    "FlextTapLdapEntry",
    "FlextTapLdapLdifStreams",
    "FlextTapLdapModels",
    "FlextTapLdapProcessor",
    "FlextTapLdapProtocols",
    "FlextTapLdapService",
    "FlextTapLdapServices",
    "FlextTapLdapSettings",
    "FlextTapLdapStreams",
    "FlextTapLdapTap",
    "FlextTapLdapTransformer",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
    "FlextTapLdapUtilitiesProcessorMixin",
    "FlextTapLdapValidator",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "_utilities",
    "api",
    "c",
    "client",
    "constants",
    "d",
    "e",
    "h",
    "ldif_streams",
    "logger",
    "m",
    "main",
    "models",
    "p",
    "processor",
    "protocols",
    "r",
    "s",
    "services",
    "settings",
    "streams",
    "t",
    "tap",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
