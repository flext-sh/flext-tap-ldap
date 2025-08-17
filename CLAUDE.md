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

- **flext-core**: Foundation library with FlextResult, logging, DI container, and FlextModel patterns
- **flext-ldap**: LDAP connectivity infrastructure (local path dependency)
- **flext-ldif**: LDIF file processing and validation (local path dependency)
- **flext-observability**: Monitoring and metrics (local path dependency)
- **pydantic**: Data validation and settings with strict typing
- **python-ldap**: Core LDAP library (test dependency)

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
# Start test LDAP server (Docker Compose setup available)
docker-compose up -d openldap

# Access LDAP REDACTED_LDAP_BIND_PASSWORD interface
# http://localhost:10080 (phpLDAPREDACTED_LDAP_BIND_PASSWORD)

# Test LDAP connectivity
make ldap-test

# Manual tap testing with test server
poetry run tap-ldap --config config.json --discover
```

### Debug Commands

```bash
# Run specific test categories
pytest -m unit -v                    # Unit tests only
pytest -m integration -v             # Integration tests only
pytest -m slow -v                    # Performance tests
pytest -m "not slow" -v              # Fast tests for quick feedback

# Test debugging
pytest tests/test_tap.py -vvs --pdb  # Debug specific test with pdb
pytest --lf -v                       # Run last failed tests

# Run single test file with coverage
pytest tests/test_streams.py --cov=src/flext_tap_ldap --cov-report=term-missing -v
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
├── conftest.py                      # Pytest fixtures and configuration
├── e2e/
│   ├── conftest.py                  # E2E test configuration
│   └── ldif/                        # Sample LDIF files for testing
│       ├── 01-base.ldif            # Base LDAP structure
│       ├── 02-users.ldif           # User entries
│       └── 03-groups.ldif          # Group entries
├── test_application_services.py    # Application service layer tests
├── test_client.py                   # LDAP client tests
├── test_client_coverage_boost.py   # Additional client coverage
├── test_client_quick.py             # Quick client tests
├── test_domain_entities.py         # Domain entity tests
├── test_exceptions.py               # Exception handling tests
├── test_integration.py              # Integration tests
├── test_ldif_processor.py           # LDIF processing tests
├── test_ldif_stream.py              # LDIF stream tests
├── test_models.py                   # Model validation tests
├── test_models_simple.py            # Simple model tests
├── test_streams.py                  # Singer stream tests
└── test_tap.py                      # Main tap functionality tests
```

### Test Markers and Coverage

The project uses pytest markers for test categorization:
- `unit`: Unit tests (fast, isolated)
- `integration`: Integration tests (require external dependencies)
- `slow`: Performance tests (longer running)
- `smoke`: Basic functionality tests
- `e2e`: End-to-end tests

Coverage is enforced at 90% minimum with branch coverage enabled.

## Configuration

### Standard LDAP Configuration

```json
{
  "host": "localhost",
  "port": 389,
  "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
  "password": "REDACTED_LDAP_BIND_PASSWORD_password",
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
          "department": { "type": "string" },
          "employeeNumber": { "type": "string" }
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
- **Pydantic**: Strict data validation and configuration with FlextModel base classes
- **Type Hints**: Complete type annotations throughout (strict MyPy configuration)
- **Error Handling**: FlextResult pattern for all service operations (railway-oriented programming)
- **Clean Architecture**: Domain, application, and infrastructure layer separation
- **Local Dependencies**: Uses local path dependencies to flext-core, flext-ldap, flext-ldif, and flext-observability

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

1. Create stream class inheriting from `Stream` (from flext-meltano)
2. Define schema using `singer_typing` from flext-meltano
3. Implement `get_records()` method with proper error handling
4. Add to `discover_streams()` in `FlextTapLDAP`
5. Add comprehensive tests with appropriate markers

### Extending Configuration

1. Update configuration classes in `config.py` using FlextModel patterns
2. Add Pydantic field with proper validation and FlextResult business rules
3. Update JSON schema in `tap.py` using `singer_typing` helpers
4. Update tests and ensure 90% coverage maintained

### Working with LDIF Files

1. Add LDIF files to `tests/e2e/ldif/` for testing
2. Use `LDIFStream` and `LDIFAnalysisStream` for processing
3. Configure LDIF processing options in tap config
4. Test with `enable_ldif_streams: true` in configuration

### Domain Logic Development

1. Create or update entities in `domain/entities.py` with business validation
2. Add business logic to `application/services.py` using FlextResult pattern
3. Use dependency injection patterns from flext-core
4. Follow Clean Architecture principles with clear layer separation

## Docker Integration

The project includes a complete Docker Compose setup for testing:

- **OpenLDAP Server**: Test LDAP directory on port 10389
- **phpLDAPREDACTED_LDAP_BIND_PASSWORD**: Web interface on port 10080
- **Sample LDIF Data**: Pre-loaded test data in `tests/e2e/ldif/`

## Architecture Integration

### FLEXT Ecosystem Integration

This tap is part of the larger FLEXT enterprise data integration platform:

- **flext-core**: Provides FlextResult, FlextModel, logging, and dependency injection patterns
- **flext-ldap**: LDAP connectivity and operations (local dependency)
- **flext-ldif**: LDIF file processing and validation (local dependency)
- **flext-observability**: Monitoring and metrics (local dependency)

### Related Singer Projects

- **flext-target-ldap**: Corresponding Singer target for loading data to LDAP
- **flext-dbt-ldap**: DBT models for LDAP data transformation

### Key Architecture Patterns

- **Clean Architecture**: Domain-driven design with clear layer boundaries
- **FlextResult Pattern**: Railway-oriented programming for error handling
- **FlextModel**: Extended Pydantic models with business rule validation
- **Singer Protocol**: Standard data extraction protocol compliance

## Build and Packaging

The project uses Poetry for dependency management with strict version pinning:

```bash
# Build distribution packages
make build

# Check dependencies
make deps-show
make deps-audit

# Update dependencies
make deps-update
```

All dependencies are managed through `pyproject.toml` with separate groups for development, testing, typing, and security tools.
