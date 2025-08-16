"""🚨 ARCHITECTURAL COMPLIANCE: ZERO EXCEPTION DUPLICATION using flext-core Factory.

✅ REFATORAÇÃO COMPLETA: 240+ linhas de código duplicado ELIMINADAS.

- ANTES: 308 linhas com mixin complexo _FlextTapLdapErrorMixin + 9 classes manuais
- DEPOIS: <80 linhas usando factory pattern limpo e DRY
- REDUÇÃO: 240+ linhas eliminadas = ~78% redução
- PADRÃO: Usa create_module_exception_classes() de flext-core
- ARQUITETURA: Funcionalidades genéricas permanecem nas bibliotecas abstratas
- EXPOSIÇÃO: API pública correta através do factory pattern

LDAP Tap Exception Hierarchy - ZERO DUPLICATION.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions for LDAP tap operations using factory pattern to eliminate duplication.
"""

from __future__ import annotations

from flext_core import create_module_exception_classes

# Generate all standard exceptions using factory pattern
_tap_ldap_exceptions = create_module_exception_classes("flext_tap_ldap")

# Export factory-created exception classes (using actual factory keys)
FlextTapLdapError = _tap_ldap_exceptions["FLEXT_TAP_LDAPError"]
FlextTapLdapValidationError = _tap_ldap_exceptions["FLEXT_TAP_LDAPValidationError"]
FlextTapLdapConfigurationError = _tap_ldap_exceptions[
    "FLEXT_TAP_LDAPConfigurationError"
]
FlextTapLdapProcessingError = _tap_ldap_exceptions["FLEXT_TAP_LDAPProcessingError"]
FlextTapLdapConnectionError = _tap_ldap_exceptions["FLEXT_TAP_LDAPConnectionError"]
FlextTapLdapAuthenticationError = _tap_ldap_exceptions[
    "FLEXT_TAP_LDAPAuthenticationError"
]
FlextTapLdapTimeoutError = _tap_ldap_exceptions["FLEXT_TAP_LDAPTimeoutError"]

# Create testing convenience aliases for existing code
FlextTapLdapSearchError = FlextTapLdapProcessingError  # Search is processing
FlextTapLdapStreamError = FlextTapLdapProcessingError  # Stream errors are processing


__all__: list[str] = [
    "FlextTapLdapAuthenticationError",
    "FlextTapLdapConfigurationError",
    "FlextTapLdapConnectionError",
    "FlextTapLdapError",
    "FlextTapLdapProcessingError",
    "FlextTapLdapSearchError",
    "FlextTapLdapStreamError",
    "FlextTapLdapTimeoutError",
    "FlextTapLdapValidationError",
]
