# FLEXT-Tap-LDAP Project Guidelines

**Reference**: See [../CLAUDE.md](../CLAUDE.md) for FLEXT ecosystem standards and general rules.

---

## Project Overview

**FLEXT-Tap-LDAP** is the Singer tap for LDAP directory extraction in the FLEXT ecosystem.

**Version**: 1.0.0  
**Status**: Production-ready  
**Python**: 3.13+

**CRITICAL INTEGRATION DEPENDENCIES**:
- **flext-meltano**: MANDATORY for ALL Singer operations (ZERO TOLERANCE for direct singer-sdk without flext-meltano)
- **flext-ldap**: MANDATORY for ALL LDAP operations (ZERO TOLERANCE for direct ldap3 imports)
- **flext-core**: Foundation patterns (FlextResult, FlextService, FlextContainer)
- **flext-cli**: MANDATORY for ALL CLI operations (ZERO TOLERANCE for direct click/rich imports)

---

## Essential Commands

```bash
# Setup and validation
make setup                    # Complete development environment setup
make validate                 # Complete validation (lint + type + security + test)
make check                    # Quick check (lint + type)

# Quality gates
make lint                     # Ruff linting
make type-check               # Pyrefly type checking
make security                 # Bandit security scan
make test                     # Run tests
```

---

## Key Patterns

### Singer Tap Implementation

```python
from flext_core import FlextResult
from flext_tap_ldap import FlextTapLdap

tap = FlextTapLdap()

# Discover catalog
result = tap.discover()
if result.is_success:
    catalog = result.unwrap()
```

---

## Critical Development Rules

### ZERO TOLERANCE Policies

**ABSOLUTELY FORBIDDEN**:
- ❌ Direct singer-sdk imports (use flext-meltano)
- ❌ Direct ldap3 imports (use flext-ldap)
- ❌ Direct click/rich imports (use flext-cli)
- ❌ Exception-based error handling (use FlextResult)
- ❌ Type ignores or `Any` types

**MANDATORY**:
- ✅ Use `FlextResult[T]` for all operations
- ✅ Use flext-meltano for Singer operations
- ✅ Use flext-ldap for LDAP operations
- ✅ Use flext-cli for CLI operations
- ✅ Complete type annotations
- ✅ Zero Ruff violations

---

**Additional Resources**: [../CLAUDE.md](../CLAUDE.md) (workspace), [README.md](README.md) (overview)
