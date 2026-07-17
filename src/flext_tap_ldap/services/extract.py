"""LDAP extract service — the record fetcher for the tap-ldap Singer streams.

Implements ``p.Meltano.RecordFetcher`` by resolving each stream's business rules
from ``config.TapLdap.streams`` and running the search through the injected
flext-ldap facade (``self.ldap``). Records are packed once into the typed
``m.Meltano.FetchResult`` transport.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_ldap import p, t, u
from flext_tap_ldap.base import s


class FlextTapLdapExtractService(s):
    """Thin orchestrator: connect, search, and pack one stream's LDAP records."""

    def fetch(
        self,
        request: p.Meltano.FetchRequest,
    ) -> p.Result[p.Meltano.FetchResult]:
        """Return the records for ``request.stream_name`` as a typed result."""
        return (
            self.ldap
            .connect(u.TapLdap.connection(request.config))
            .flat_map(
                lambda _: u.TapLdap.stream_search(request.stream_name, request.config),
            )
            .flat_map(self._run_search)
            .map(lambda records: p.Meltano.FetchResult(records=records))
        )

    def _run_search(
        self,
        options: p.Ldap.SearchOptions,
    ) -> p.Result[t.SequenceOf[t.JsonMapping]]:
        """Run the search and pack entries into Singer records."""
        return self.ldap.search(options).map(
            lambda result: u.TapLdap.pack_entries(result.entries),
        )


__all__: list[str] = ["FlextTapLdapExtractService"]
