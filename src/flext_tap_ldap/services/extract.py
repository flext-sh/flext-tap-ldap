"""LDAP extract service — the record fetcher for the tap-ldap Singer streams.

Implements ``p.Meltano.RecordFetcher`` by resolving each stream's business rules
from ``config.TapLdap.streams`` and running the search through the injected
flext-ldap facade (``self.ldap``). Records are packed once into the typed
``m.Meltano.FetchResult`` transport.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence

from flext_tap_ldap import m, p, s, t, u


class FlextTapLdapExtractService(s):
    """Thin orchestrator: connect, search, and pack one stream's LDAP records."""

    def fetch(self, request: m.Meltano.FetchRequest) -> p.Result[m.Meltano.FetchResult]:
        """Return the records for ``request.stream_name`` as a typed result.

        Args:
            request: Fetch request naming the stream and carrying the tap config.

        Returns:
            The resulting ``p.Result[m.Meltano.FetchResult]``.

        """
        return (
            self.ldap
            .connect(u.TapLdap.connection(request.config))
            .flat_map(
                lambda _: u.TapLdap.stream_search(request.stream_name, request.config),
            )
            .flat_map(self._run_search)
            .map(lambda records: m.Meltano.FetchResult(records=tuple(records)))
        )

    def _run_search(
        self,
        options: m.Ldap.SearchOptions,
    ) -> p.Result[Sequence[t.JsonMapping]]:
        """Run the search and pack entries into Singer records.

        Args:
            options: Typed LDAP search options resolved for the stream.

        Returns:
            The resulting ``p.Result[Sequence[t.JsonMapping]]``.

        """
        return self.ldap.search(options).map(
            lambda result: u.TapLdap.pack_entries(result.entries),
        )


__all__: list[str] = ["FlextTapLdapExtractService"]
