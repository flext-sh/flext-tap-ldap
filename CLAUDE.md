# CLAUDE.md - FLEXT Tap LDAP Quality Refactoring Guide

**Project**: FLEXT Tap LDAP - Enterprise LDAP Data Extraction  
**Status**: Quality Refactoring Required | **Architecture**: Clean Architecture + DDD  
**Dependencies**: Python 3.13+, flext-core, flext-ldap, flext-meltano, singer-sdk  
**Coverage Target**: 90% | **Current Type Status**: Requires Assessment  
**Authority**: FLEXT-TAP-LDAP | **Last Updated**: 2025-01-08

---

## 🎯 PROJECT MISSION STATEMENT

Transform FLEXT Tap LDAP into a **production-ready, enterprise-grade LDAP/LDIF data extraction tap** implementing Singer protocol with zero tolerance quality standards. This tap provides comprehensive LDAP directory and LDIF file processing capabilities with Clean Architecture, Domain-Driven Design, and integration with the broader FLEXT ecosystem.

### 🏆 SUCCESS CRITERIA (EVIDENCE-BASED VALIDATION)

- **✅ 90% Test Coverage**: Real functional tests, not mock-heavy (measured via `pytest --cov=src --cov-report=term`)
- **✅ Zero Tolerance Quality**: MyPy strict + Ruff ALL rules + Bandit security (measured via `make validate`)  
- **✅ Singer Protocol Compliance**: Full catalog discovery + data extraction working (verified via `make discover && make run`)
- **✅ LDAP Integration**: Real LDAP connectivity + LDIF processing (verified via `make ldap-test`)
- **✅ Performance**: Handles enterprise-scale LDAP directories efficiently (measured via performance tests)

---

## 🚫 PROJECT PROHIBITIONS (ZERO TOLERANCE ENFORCEMENT)

### ⛔ ABSOLUTELY FORBIDDEN ACTIONS:

1. **Quality Degradation**:
   - NEVER reduce test coverage below 90%
   - NEVER suppress MyPy/Ruff errors without proper resolution
   - NEVER disable security scanning (Bandit/pip-audit)
   - NEVER compromise Singer protocol compliance

2. **Architectural Violations**:
   - NEVER bypass Clean Architecture layer boundaries
   - NEVER create circular dependencies between layers
   - NEVER duplicate functionality available in flext-core/flext-ldap/flext-ldif
   - NEVER ignore FlextResult pattern for error handling

3. **LDAP/LDIF Specific Violations**:
   - NEVER hardcode LDAP connection parameters
   - NEVER process LDIF files without proper error handling
   - NEVER ignore LDAP schema validation
   - NEVER create insecure authentication mechanisms

4. **Singer Protocol Violations**:
   - NEVER return data without proper Singer RECORD messages
   - NEVER skip catalog discovery implementation
   - NEVER ignore incremental replication keys
   - NEVER create non-compliant stream schemas

---

## 🏗️ PROJECT ARCHITECTURE (CURRENT STATE ANALYSIS REQUIRED)

### Core Architecture Layers

```python
# FLEXT Tap LDAP follows Clean Architecture + DDD
src/flext_tap_ldap/
   domain/                    # Core business logic (NEVER depend on external layers)
      entities.py             # Domain entities: LDAPConnection, LDAPStream, TapExecution
   application/               # Application services (orchestrate domain logic)
      services.py             # Business logic with FlextResult pattern
   infrastructure/            # External integrations (LDAP, LDIF, file system)
   tap.py                     # Main TapLDAP class (Singer SDK implementation)
   streams.py                 # Singer stream implementations
   config.py                  # Pydantic configuration models
   client.py                  # LDAP client wrapper (infrastructure)
   ldif_stream.py             # LDIF file processing streams
   ldif_processor.py          # LDIF parsing utilities
   exceptions.py              # Domain-specific exception hierarchy
```

### Service Architecture Pattern (MANDATORY)

```python
class FlextTapLdapService(FlextDomainService):
    """Single unified service class following flext-core patterns.
    
    This class consolidates all LDAP/LDIF tap-related operations,
    following the single responsibility principle while
    maintaining a unified interface for data extraction.
    """
    
    def __init__(self, **data) -> None:
        """Initialize service with proper dependency injection."""
        super().__init__(**data)
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)
    
    def extract_ldap_data(self, connection_config: dict, search_filter: str) -> FlextResult[list[dict]]:
        """Extract data from LDAP directory with comprehensive error handling."""
        if not connection_config or not search_filter:
            return FlextResult[list[dict]].fail("Connection config and search filter are required")
        
        try:
            # Use flext-ldap for connection management
            ldap_client = self._container.get(LdapClient)
            connection_result = ldap_client.connect(connection_config)
            if connection_result.is_failure:
                return FlextResult[list[dict]].fail(f"LDAP connection failed: {connection_result.error}")
            
            # Perform search with pagination
            search_result = ldap_client.search_with_paging(
                search_filter=search_filter,
                page_size=connection_config.get("page_size", 1000)
            )
            
            if search_result.is_success:
                return FlextResult[list[dict]].ok(search_result.value)
            else:
                return FlextResult[list[dict]].fail(f"LDAP search failed: {search_result.error}")
                
        except Exception as e:
            self._logger.error(f"LDAP data extraction error: {e}")
            return FlextResult[list[dict]].fail(f"LDAP extraction error: {str(e)}")
    
    def process_ldif_file(self, file_path: str, batch_size: int = 1000) -> FlextResult[list[dict]]:
        """Process LDIF file with comprehensive error handling."""
        if not file_path:
            return FlextResult[list[dict]].fail("File path is required")
        
        try:
            # Use flext-ldif for file processing
            ldif_processor = self._container.get(LdifProcessor)
            processing_result = ldif_processor.process_file(
                file_path=file_path,
                batch_size=batch_size,
                validate_schema=True
            )
            
            if processing_result.is_success:
                return FlextResult[list[dict]].ok(processing_result.value)
            else:
                return FlextResult[list[dict]].fail(f"LDIF processing failed: {processing_result.error}")
                
        except Exception as e:
            self._logger.error(f"LDIF processing error: {e}")
            return FlextResult[list[dict]].fail(f"LDIF processing error: {str(e)}")
    
    def validate_configuration(self, config: dict) -> FlextResult[bool]:
        """Validate tap configuration with business rules."""
        # Implementation with comprehensive validation
        return FlextResult[bool].ok(True)
```

---

## ⚡ IMPLEMENTATION STRATEGY (PRIORITY-BASED EXECUTION)

### Phase 1: Foundation Assessment & Repair (MANDATORY FIRST)

#### 1.1 Current State Discovery (INVESTIGATE FIRST)
```bash
# MANDATORY: Complete ecosystem understanding
find flext-core/src -name "*.py" -exec grep -l "FlextDomainService\|FlextResult\|FlextContainer" {} \;
# Read EVERY file that shows up - understand what's available

# Map current LDAP/LDIF dependencies  
grep -r "from flext_" src/ --include="*.py" | cut -d: -f2 | sort | uniq
# Understand dependency relationships before refactoring

# Check current Singer SDK integration
python -c "from flext_tap_ldap import FlextTapLDAP; help(FlextTapLDAP.discover_streams)"
# Verify current API compatibility

# Count current test coverage
pytest --cov=src --cov-report=term | grep "TOTAL"
# Get baseline coverage before improvements

# Map current failure patterns
pytest --tb=no -q | tail -1 | grep -oE "[0-9]+ failed"
# Understand current test landscape
```

#### 1.2 Quality Gate Assessment
```bash
# Type checking status
mypy src/ --strict --show-error-codes 2>&1 | wc -l
# Count current type errors (target: 0)

# Linting status  
ruff check src/ --statistics | grep "errors"
# Count current linting errors (target: 0)

# Security scan
bandit -r src/ -f json 2>/dev/null | jq '.metrics._totals' || echo "Security scan needed"
# Assess security status

# Singer protocol compliance
make discover 2>&1 | grep -E "ERROR|FAILED" | wc -l
# Test current Singer compliance
```

### Phase 2: Core Service Unification (ARCHITECTURE FOCUS)

#### 2.1 Single Service Class Creation
```python
# Create src/flext_tap_ldap/services/tap_service.py
class FlextTapLdapService(FlextDomainService):
    """Unified LDAP/LDIF tap service with comprehensive functionality."""
    # Implementation following the pattern above
```

#### 2.2 Legacy Pattern Migration
- **FlextResult Adoption**: Replace all exception-based error handling with FlextResult pattern
- **Dependency Injection**: Move to flext-core DI container usage
- **Service Consolidation**: Migrate distributed functionality to unified service class

### Phase 3: Singer Protocol Excellence (PROTOCOL COMPLIANCE)

#### 3.1 Stream Implementation Standardization
```python
class LdapUsersStream(Stream):
    """LDAP Users stream with flext-core integration."""
    
    def get_records(self, context: dict | None) -> Iterable[dict[str, Any]]:
        """Extract user records with comprehensive error handling."""
        service = self._container.get(FlextTapLdapService)
        result = service.extract_ldap_data(
            connection_config=self.config,
            search_filter="(objectClass=inetOrgPerson)"
        )
        
        if result.is_success:
            for record in result.value:
                yield record
        else:
            self.logger.error(f"User extraction failed: {result.error}")
            raise RuntimeError(f"User stream error: {result.error}")
```

#### 3.2 Schema Discovery Enhancement
- **Dynamic Schema Detection**: Implement LDAP schema introspection
- **LDIF Schema Analysis**: Automatic schema discovery from LDIF files
- **Configuration-Based Schema**: Support custom schema definitions

### Phase 4: Integration Testing Excellence (REAL TESTING)

#### 4.1 Docker Test Environment
```bash
# Enhanced Docker Compose for comprehensive testing
docker-compose up -d openldap
# Provides real LDAP server for integration tests

# Real LDIF processing tests
tests/e2e/ldif/
├── 01-base.ldif              # Base LDAP structure
├── 02-users.ldif             # User entries for testing  
├── 03-groups.ldif            # Group entries for testing
└── 04-complex-schema.ldif    # Complex schema for edge cases
```

#### 4.2 Performance Testing Implementation
```python
@pytest.mark.slow
def test_large_ldap_directory_extraction():
    """Test tap performance with enterprise-scale LDAP directory."""
    # Test with 10,000+ entries, measure extraction time
    # Verify memory usage stays reasonable
    # Validate pagination performance
```

---

## 🔧 ESSENTIAL COMMANDS (DAILY DEVELOPMENT)

### Quality Gates (MANDATORY BEFORE ANY COMMIT)
```bash
# NEVER SKIP: Complete validation pipeline
make validate                # lint + type + security + test (90% coverage)

# Quick validation during development  
make check                   # lint + type-check + test

# Individual quality components
make lint                    # Ruff linting (ALL rules enabled)
make type-check              # MyPy strict mode validation
make security                # Bandit + pip-audit security scanning
make format                  # Auto-format code with Ruff
```

### Singer Tap Operations
```bash
# Essential Singer protocol operations
make discover                # Generate catalog.json schema (test Singer compliance)
make run                     # Run data extraction (validate full pipeline)
make validate-config         # Validate tap configuration JSON

# LDAP-specific testing
make ldap-test               # Test LDAP connectivity with Docker environment
make ldif-validate           # Validate LDIF file format and processing
```

### Testing Strategy (90% COVERAGE TARGET)
```bash
# Comprehensive testing approach
make test                    # All tests with 90% coverage requirement
make test-unit               # Unit tests only (-m "not integration")
make test-integration        # Integration tests with real LDAP/LDIF
make test-singer             # Singer protocol compliance tests
make coverage-html           # Generate HTML coverage report for analysis

# Performance and slow tests
pytest -m slow               # Performance tests (enterprise-scale testing)
pytest -m "not slow"         # Fast tests for quick feedback loop
```

### LDAP Development Environment
```bash
# Docker-based development environment
docker-compose up -d openldap        # Start test LDAP server (port 10389)
# Access phpLDAPREDACTED_LDAP_BIND_PASSWORD: http://localhost:10080

# Manual testing with real environment
poetry run tap-ldap --config config.json --discover > catalog.json
poetry run tap-ldap --config config.json --catalog catalog.json --state state.json
```

---

## 📊 SUCCESS METRICS (EVIDENCE-BASED MEASUREMENT)

### Code Quality Metrics (AUTOMATED VALIDATION)
```bash
# Coverage measurement (TARGET: 90%)
pytest --cov=src --cov-report=term | grep "TOTAL" | awk '{print $4}'

# Type safety assessment (TARGET: 0 errors)
mypy src/ --strict --show-error-codes 2>&1 | wc -l

# Linting compliance (TARGET: 0 errors)  
ruff check src/ --statistics | grep -o "[0-9]\+ errors"

# Security assessment (TARGET: 0 critical vulnerabilities)
bandit -r src/ -f json 2>/dev/null | jq '.metrics._totals.SEVERITY_RISK_HIGH' || echo 0
```

### Singer Protocol Compliance (FUNCTIONAL VALIDATION)
```bash
# Catalog discovery success
make discover >/dev/null 2>&1 && echo "✅ Discovery OK" || echo "❌ Discovery FAILED"

# Data extraction success
make run >/dev/null 2>&1 && echo "✅ Extraction OK" || echo "❌ Extraction FAILED"

# Schema validation
singer-check-tap --catalog catalog.json < /dev/null && echo "✅ Schema OK" || echo "❌ Schema FAILED"
```

### LDAP/LDIF Functionality (DOMAIN-SPECIFIC VALIDATION)
```bash
# LDAP connectivity test
make ldap-test >/dev/null 2>&1 && echo "✅ LDAP OK" || echo "❌ LDAP FAILED"

# LDIF processing test
make ldif-validate >/dev/null 2>&1 && echo "✅ LDIF OK" || echo "❌ LDIF FAILED"

# Stream extraction test
python -c "
from flext_tap_ldap import FlextTapLDAP
tap = FlextTapLDAP()
streams = list(tap.discover_streams())
print(f'✅ {len(streams)} streams discovered')
" && echo "Stream discovery OK"
```

---

## 🔍 PROJECT-SPECIFIC CONTEXT (LDAP/LDIF DOMAIN EXPERTISE)

### LDAP Directory Integration Patterns

#### Enterprise LDAP Support
- **Directory Servers**: Active Directory, OpenLDAP, Oracle Directory Server Enterprise Edition
- **Authentication**: Simple bind, SASL, StartTLS, SSL/TLS  
- **Schema Support**: inetOrgPerson, groupOfNames, organizationalUnit, custom schemas
- **Operations**: Search, pagination, referral following, attribute mapping

#### LDIF File Processing Excellence
- **Format Support**: LDIF v1, change records, base64 encoding
- **Validation**: Schema compliance, referential integrity, attribute validation
- **Performance**: Streaming processing, memory-efficient parsing, batch processing
- **Error Handling**: Parse error recovery, malformed entry handling, encoding issues

### Singer Protocol Implementation Details

#### Stream Types and Configuration
```python
# Stream implementations aligned with LDAP structure
SUPPORTED_STREAMS = {
    "users": "(&(objectClass=inetOrgPerson)(!(objectClass=computer)))",
    "groups": "(objectClass=groupOfNames)",
    "computers": "(&(objectClass=computer)(objectClass=organizationalPerson))",
    "organizational_units": "(objectClass=organizationalUnit)",
    "schema": "(objectClass=subSchema)",
    "custom": "user-defined-filter"
}

# Incremental replication support
REPLICATION_KEYS = {
    "users": "modifyTimestamp",
    "groups": "modifyTimestamp", 
    "computers": "modifyTimestamp",
    "organizational_units": "modifyTimestamp"
}
```

#### Configuration Schema Excellence
```python
class FlextTapLdapConfig(FlextModel):
    """Comprehensive LDAP tap configuration with validation."""
    
    # LDAP Connection (required)
    host: str = Field(..., description="LDAP server hostname")
    port: int = Field(default=389, ge=1, le=65535)
    bind_dn: str = Field(..., description="Bind DN for authentication")
    password: SecretStr = Field(..., description="Password for bind DN")
    base_dn: str = Field(..., description="Base DN for searches")
    
    # SSL/TLS Configuration
    use_ssl: bool = Field(default=False)
    use_tls: bool = Field(default=False) 
    ca_cert_file: Optional[str] = None
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    
    # Performance Settings
    timeout: int = Field(default=30, ge=1, le=300)
    page_size: int = Field(default=1000, ge=1, le=10000)
    connection_pool_size: int = Field(default=5, ge=1, le=20)
    
    # LDIF Processing
    enable_ldif_streams: bool = Field(default=False)
    ldif_files: list[str] = Field(default_factory=list)
    ldif_directory: Optional[str] = None
    ldif_ignore_errors: bool = Field(default=True)
    ldif_max_errors: int = Field(default=100, ge=0, le=10000)
    
    # Custom Streams
    custom_streams: list[dict] = Field(default_factory=list)
    
    # Migration Support
    migration_batch: Optional[str] = None
```

### Integration with FLEXT Ecosystem

#### Dependency Architecture
```python
# FLEXT ecosystem integration (MANDATORY patterns)
from flext_core import FlextDomainService, FlextResult, FlextContainer, FlextLogger
from flext_ldap import LdapClient, LdapConnectionConfig  # Local dependency
from flext_ldif import LdifProcessor, LdifValidator    # Local dependency
from flext_meltano import Tap, Stream, singer_typing   # Singer SDK integration
from flext_observability import FlextMetrics, FlextHealthCheck  # Monitoring
```

#### Service Discovery Pattern
```python
def setup_dependencies() -> None:
    """Configure dependency injection for LDAP tap."""
    container = FlextContainer.get_global()
    
    # Register LDAP services
    container.register(LdapClient, singleton=True)
    container.register(LdifProcessor, singleton=True)
    container.register(FlextTapLdapService, singleton=True)
    
    # Register Singer services
    container.register(Tap, factory=lambda: FlextTapLDAP)
    
    # Register monitoring services
    container.register(FlextMetrics, singleton=True)
    container.register(FlextHealthCheck, singleton=True)
```

---

## 🎯 QUALITY ACHIEVEMENT ROADMAP (PHASE-BY-PHASE SUCCESS)

### Week 1: Foundation Stability (PREREQUISITE SUCCESS)
- [ ] **Quality Gate Repair**: Achieve `make validate` success (0 errors)
- [ ] **Test Coverage Assessment**: Document current coverage and gaps
- [ ] **Dependency Analysis**: Map all flext-* dependencies and integration points
- [ ] **Singer Compliance**: Ensure basic discover/extract functionality works

### Week 2: Service Architecture (UNIFICATION SUCCESS) 
- [ ] **Unified Service**: Implement `FlextTapLdapService` with all functionality
- [ ] **FlextResult Migration**: Replace all exception handling with FlextResult pattern
- [ ] **Container Integration**: Migrate to flext-core dependency injection
- [ ] **Layer Validation**: Ensure Clean Architecture compliance

### Week 3: Protocol Excellence (SINGER COMPLIANCE)
- [ ] **Stream Standardization**: Implement all LDAP stream types with error handling
- [ ] **Schema Discovery**: Dynamic schema detection from LDAP/LDIF sources
- [ ] **Incremental Replication**: Implement timestamp-based incremental extraction
- [ ] **Configuration Validation**: Comprehensive config validation with business rules

### Week 4: Testing Excellence (90% COVERAGE TARGET)
- [ ] **Integration Tests**: Real LDAP/LDIF processing tests with Docker environment
- [ ] **Performance Tests**: Enterprise-scale testing with large datasets
- [ ] **Error Scenario Tests**: Network failures, malformed data, authentication issues
- [ ] **Coverage Validation**: Achieve and maintain 90% test coverage

### Success Validation (EVIDENCE-BASED CONFIRMATION)
```bash
# Final success confirmation (ALL must pass)
make validate                    # ✅ Zero errors
pytest --cov=src --cov-report=term | grep "90%"  # ✅ Coverage target
make discover && make run        # ✅ Singer compliance
docker-compose up -d && make ldap-test  # ✅ LDAP integration
```

---

**PROJECT AUTHORITY**: FLEXT-TAP-LDAP  
**REFACTORING AUTHORITY**: Evidence-based validation required for all success claims  
**QUALITY AUTHORITY**: Zero tolerance - 90% coverage, zero type errors, full Singer compliance  
**INTEGRATION AUTHORITY**: Must integrate seamlessly with FLEXT ecosystem (flext-core, flext-ldap, flext-ldif)