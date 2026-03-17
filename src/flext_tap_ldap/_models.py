"""Auto-generated centralized models."""

from __future__ import annotations

from pydantic import ConfigDict, RootModel


class FlextAutoConstants:
    pass


class FlextAutoTypes:
    pass


class FlextAutoProtocols:
    pass


class FlextAutoUtilities:
    pass


class FlextAutoModels:
    pass


c = FlextAutoConstants
t = FlextAutoTypes
p = FlextAutoProtocols
u = FlextAutoUtilities
m = FlextAutoModels


class _CONFIG_MAP_ADAPTER(
    RootModel[TypeAdapter(dict[str, t.ContainerValue], config=ConfigDict(strict=False))]
):
    pass
