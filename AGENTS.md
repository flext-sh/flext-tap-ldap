# AGENTS.md — flext-tap-ldap

> **Parent workspace law** lives in [`../AGENTS.md`](../AGENTS.md) — read it first.
> Universal engineering core: `~/.agents/UNIVERSAL_CORE.md`. Composition: global skills + parent/root `AGENTS.md` + this scope delta. Do not re-embed universal law.
>
> **Standalone / independent mode:** when `../AGENTS.md` does not resolve, pin the parent raw `AGENTS.md` URL to the same branch/release as this package (never `main`).

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
**Package:** `flext_tap_ldap` · deps: `flext-cli`, `flext-core`, `flext-ldap`, `flext-meltano`

## Overview

Singer **tap** (extractor) for LDAP directory services. Thin driver over `flext-meltano` (ADR-006), delegating extraction to `flext-ldap`.

## Structure

```text
src/flext_tap_ldap/
├── api.py            # FlextTapLdapService — builds a declarative meltano.Tap (TapSpec)
├── base.py cli.py    # imports the meltano service layer
├── services/         # FlextTapLdapExtractService (extraction)
├── constants.py typings.py protocols.py models.py utilities.py   # AUTO-GENERATED facets
└── _models/ _utilities/
```

## Code Map

| Symbol | Kind | Location | Role |
|--------|------|----------|------|
| `FlextTapLdapService` | class | `api.py` | declarative `meltano.Tap`; builds `TapSpec` |
| `FlextTapLdapExtractService` | class | `services/` | LDAP extraction (delegates to `flext-ldap`) |

Extends the `flext-meltano` tap base; Singer SDK plumbing is owned by the meltano facade.

## Anti-Patterns / Gotchas

- **`tap.py.bak` / `streams.py.bak` / `client.py.bak` are dead artifacts** — not active entrypoints, do not treat them as source.
- Acceptance = the tap's public CLI works end-to-end (Singer stream output).

## Commands

```bash
make check PROJECT=flext-tap-ldap
make test  PROJECT=flext-tap-ldap       # tests/{unit,e2e}
```
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->
