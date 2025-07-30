# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FLEXT-TAP-LDAP is a Singer-compliant tap for extracting data from LDAP directories and LDIF files. It's part of the FLEXT enterprise data integration platform, implementing Clean Architecture, Domain-Driven Design (DDD), and zero-tolerance quality standards.

## Key Architecture

### Design Patterns
- **Clean Architecture**: Clear separation between domain, application, and infrastructure layers
- **Domain-Driven Design**: Domain entities and services model the LDAP extraction business logic
- **Singer SDK**: Standard data extraction protocol for ETL pipelines
- **FlextResult Pattern**: Railway-oriented programming for error handling from flext-core
- **Dependency Injection**: Uses flext-core DI container for service management

### Core Components
- **Domain Layer** (`src/flext_tap_ldap/domain/`): Entities like `LDAPConnection`, `LDAPStream`, `TapExecution`, `LDAPRecord`
- **Application Services** (`src/flext_tap_ldap/application/`): Business logic services using FlextResult pattern
- **Stream Classes** (`src/flext_tap_ldap/streams.py`): Singer streams for Users, Groups, OUs, Schema, and Custom queries
- **Configuration** (`src/flext_tap_ldap/config.py`): Pydantic-based config with LDAP connection and LDIF processing settings
- **LDIF Processing** (`src/flext_tap_ldap/ldif_stream.py`): Specialized streams for LDIF file processing

### Dependencies
- **flext-core**: Foundation library with FlextResult, logging, DI container
- **flext-meltano**: Centralized Singer SDK and common patterns
- **flext-ldap**: LDAP connectivity infrastructure
- **flext-observability**: Monitoring and metrics

## Development Commands

### Essential Commands
```bash
# Complete project setup
make setup                    # Install dependencies and pre-commit hooks

# Quality gates (run before committing)
make validate                 # Complete validation (lint + type + security + test)
make check                    # Quick health check (lint + type)

# Testing
make test                     # Run all tests with 90% coverage requirement
make test-unit                # Unit tests only
make test-integration         # Integration tests only
pytest -m "not slow"          # Fast tests for quick feedback

# Code quality
make lint                     # Ruff linting with ALL rules enabled
make format                   # Auto-format with Ruff
make type-check               # MyPy strict type checking
make security                 # Bandit security scanning + pip-audit

# Singer tap operations
make discover                 # Generate catalog.json schema
make run                      # Run data extraction
make validate-config          # Validate tap configuration JSON
```

### Development Workflow
```bash
# Single test file
pytest tests/test_streams.py -v

# Run specific test markers
pytest -m unit                # Unit tests
pytest -m integration         # Integration tests
pytest -m slow                # Performance tests

# Debug failing tests
pytest tests/test_tap.py -vvs --pdb

# Coverage analysis
make coverage-html            # Generate HTML coverage report
```

### LDAP Testing Environment
```bash
# Start test LDAP server
docker-compose up -d openldap

## TODO: GAPS DE ARQUITETURA IDENTIFICADOS - PRIORIDADE ALTA

### 🚨 GAP 1: LDAP Library Integration Incomplete
**Status**: ALTO - Tap não integra completamente com flext-ldap
**Problema**:
- Dependency em flext-ldap mas integration patterns não claros
- LDAP connection management pode ser duplicado
- Schema discovery não reutiliza flext-ldap capabilities

**TODO**:
- [ ] Integrar completamente com flext-ldap para connection management
- [ ] Reutilizar flext-ldap schema discovery capabilities
- [ ] Documentar LDAP library integration patterns
- [ ] Eliminar duplicação de LDAP connection code

### 🚨 GAP 2: LDIF Processing Integration Gap
**Status**: ALTO - LDIF streams não integram com flext-ldif
**Problema**:
- LDIF processing implementado localmente em ldif_stream.py
- Não reutiliza flext-ldif para parsing e validation
- Duplicação de LDIF processing logic

**TODO**:
- [ ] Migrar LDIF processing para usar flext-ldif library
- [ ] Integrar LDIF validation com flext-ldif patterns
- [ ] Refatorar ldif_stream.py para use flext-ldif
- [ ] Documentar LDIF integration patterns

### 🚨 GAP 3: Meltano Integration Superficial
**Status**: ALTO - Integration com flext-meltano não completa
**Problema**:
- Dependency em flext-meltano mas patterns não fully utilized
- Singer SDK integration via flext-meltano não clear
- Plugin registration não automatic via Meltano

**TODO**:
- [ ] Integrar completamente com flext-meltano Singer patterns
- [ ] Implement automatic plugin registration via Meltano
- [ ] Use flext-meltano common patterns consistently
- [ ] Document Meltano integration workflow

# Access LDAP admin interface
# http://localhost:10080 (phpLDAPadmin)

# Test LDAP connectivity
make ldap-test

# Manual tap testing with test server
poetry run tap-ldap --config config.json --discover
```

## Project Structure

### Source Organization
```
src/flext_tap_ldap/
├── domain/
│   └── entities.py           # Domain entities with business logic
├── application/
│   └── services.py           # Application services using FlextResult
├── infrastructure/           # External integrations (currently empty)
├── tap.py                    # Main FlextTapLDAP class
├── streams.py                # Singer stream implementations
├── config.py                 # Pydantic configuration models  
├── client.py                 # LDAP client wrapper
├── ldif_stream.py            # LDIF file processing streams
├── ldif_processor.py         # LDIF parsing utilities
└── exceptions.py             # Domain-specific exceptions
```

### Test Structure
```
tests/
├── e2e/
│   └── ldif/                 # Sample LDIF files for testing
├── test_client.py            # LDAP client tests
├── test_streams.py           # Stream implementation tests
├── test_tap.py               # Main tap functionality tests
├── test_integration.py       # Integration tests
└── conftest.py               # Pytest fixtures and configuration
```

## Configuration

### Standard LDAP Configuration
```json
{
  "host": "localhost",
  "port": 389,
  "bind_dn": "cn=admin,dc=test,dc=com", 
  "password": "admin_password",
  "base_dn": "dc=test,dc=com",
  "use_ssl": false,
  "timeout": 30,
  "page_size": 1000
}
```

### LDIF Processing Configuration
```json
{
  "enable_ldif_streams": true,
  "ldif_files": ["/path/to/export.ldif"],
  "ldif_directory": "/path/to/ldif/files",
  "ldif_ignore_errors": true,
  "ldif_max_errors": 100,
  "migration_batch": "batch_001"
}
```

### Custom Streams
Define custom LDAP queries as streams:
```json
{
  "custom_streams": [
    {
      "name": "custom_users",
      "search_filter": "(&(objectClass=person)(department=IT))",
      "primary_keys": ["dn"],
      "replication_key": "modifyTimestamp",
      "schema": {
        "properties": {
          "department": {"type": "string"},
          "employeeNumber": {"type": "string"}
        }
      }
    }
  ]
}
```

## Quality Standards

### Zero Tolerance Quality Gates
- **Test Coverage**: Minimum 90% (enforced by pytest-cov)
- **Type Safety**: Strict MyPy with no untyped code
- **Linting**: Ruff with ALL rules enabled, minimal ignored rules
- **Security**: Bandit scanning + pip-audit for vulnerabilities
- **Pre-commit**: Automated quality checks on every commit

### Code Standards
- **Python 3.13**: Latest Python with modern typing features
- **Pydantic**: Strict data validation and configuration
- **Async/Await**: Async patterns where beneficial
- **Type Hints**: Complete type annotations throughout
- **Error Handling**: FlextResult pattern for all service operations

## Singer Protocol Implementation

### Stream Types
- **UsersStream**: Extract user accounts (`objectClass=inetOrgPerson`)
- **GroupsStream**: Extract groups (`objectClass=groupOfNames`)
- **OrganizationalUnitsStream**: Extract organizational units
- **SchemaStream**: Extract LDAP schema information
- **CustomStream**: User-defined LDAP queries
- **LDIFStream**: Process LDIF files
- **LDIFAnalysisStream**: Analyze LDIF structure and content

### Replication Methods
- **FULL_TABLE**: Complete data extraction (default)
- **INCREMENTAL**: Based on `modifyTimestamp` where available

### Record Format
All streams produce Singer RECORD messages with:
- `dn`: Distinguished Name (primary key)
- `objectClass`: Array of LDAP object classes
- LDAP attributes as individual fields
- `modifyTimestamp`: For incremental replication

## Common Development Tasks

### Adding a New Stream
1. Create stream class inheriting from `LDAPBaseStream`
2. Define schema using `singer_typing` from flext-meltano
3. Implement `get_records()` method
4. Add to `discover_streams()` in `FlextTapLDAP`
5. Add comprehensive tests

### Extending Configuration
1. Update `TapLDAPConfig` in `config.py`
2. Add Pydantic field with validation
3. Update JSON schema in `tap.py`
4. Update tests and documentation

### Adding Domain Logic
1. Create or update entities in `domain/entities.py`
2. Add business logic to application services
3. Use FlextResult pattern for error handling
4. Add domain events for important state changes

## Docker Integration

The project includes a complete Docker Compose setup for testing:
- **OpenLDAP Server**: Test LDAP directory on port 10389
- **phpLDAPadmin**: Web interface on port 10080
- **Sample LDIF Data**: Pre-loaded test data in `tests/e2e/ldif/`

## Related Projects

This tap integrates with the broader FLEXT ecosystem:
- **flext-target-ldap**: Corresponding Singer target for loading data to LDAP
- **flext-dbt-ldap**: DBT models for LDAP data transformation
- **flext-meltano**: Orchestration and common Singer patterns
- **flext-core**: Foundation patterns and utilities