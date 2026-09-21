"""FlextTapLdapConfig — frozen config singleton for flext-tap-ldap.

Business-rule SSOT: the stream contracts (name, LDAP filter, attributes, Singer
schema, primary keys) live in ``config/tap-ldap.yaml`` at the project root under
the ``TapLdap`` key and are exposed through the open ``config.tap_ldap`` namespace.
Config holds the business rules; ``settings`` holds the adjustable runtime
parameters (``.env`` / env vars / local settings / CLI).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from functools import cached_property
from typing import ClassVar, Self

from flext_meltano import FlextMeltanoConfig

from flext_core import FlextSettings

from ._models.config import FlextTapLdapConfigModels


class FlextTapLdapConfig(FlextSettings, FlextMeltanoConfig):
    """TapLdap config auto-loaded from the project-root ``config/*.yaml``.

    ``CONFIG_DIR`` is reset to the relative default so the loader anchors to this
    project's own root ``config/`` instead of inheriting an ancestor's absolute
    override. The model-less YAML slice is validated once into the typed config
    models and exposed as ``config.tap_ldap``.

    MRO carries ``FlextSettings`` FIRST (ENFORCE-042); the class stays a frozen,
    YAML-validated config singleton.
    """

    # ENFORCE-042 namespace-holder contract: ``FlextSettings`` contributes
    # namespacing only — instance machinery stays plain object semantics so the
    # settings singleton ``__new__`` cannot leak into the config singleton.
    # Unlike never-instantiated namespace holders, ``__init__`` delegates to
    # ``super()`` so the frozen, YAML-validated pydantic construction still
    # runs, and the inherited pydantic ``__setattr__`` keeps the frozen guard.
    def __new__(cls, *args: object, **kwargs: object) -> Self:
        _ = args, kwargs
        return object.__new__(cls)

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

    __eq__ = object.__eq__

    __hash__ = object.__hash__

    CONFIG_DIR: ClassVar[str] = "config"

    @cached_property
    def tap_ldap(self) -> FlextTapLdapConfigModels.TapLdap:
        """Validated TapLdap business-rule config (streams and their contracts)."""
        payload: dict[str, object] = dict(self.model_extra or {})
        root = FlextTapLdapConfigModels.Root.model_validate(payload)
        tap_ldap: FlextTapLdapConfigModels.TapLdap = root.TapLdap
        return tap_ldap


config: FlextTapLdapConfig = FlextTapLdapConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_tap_ldap import config``."""

__all__: list[str] = ["FlextTapLdapConfig", "config"]
