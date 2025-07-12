# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**flext-tap-ldap** is a production-ready Singer protocol tap for extracting data from LDAP directories (Active Directory, OpenLDAP, Oracle Directory). It's part of the FLEXT framework ecosystem and implements enterprise-grade directory data extraction with incremental synchronization capabilities.

- **Version**: 0.7.0
- **Python**: 3.13+ (strict requirement)
- **Architecture**: Hexagonal Architecture with Domain-Driven Design
- **Status**: Production/Stable with ongoing FLEXT framework migration

## Development Commands

### Environment Setup

```bash
# Use workspace virtual environment (REQUIRED)
source /home/marlonsc/flext/.venv/bin/activate
```

### Build & Development

```bash
make install      # Install dependencies
make dev          # Development mode setup
make build        # Build package
```

### Testing

```bash
make test         # Run all tests with coverage (90%+ required)
make test-unit    # Unit tests only
make test-integration  # Integration tests with mock LDAP
make test-e2e     # End-to-end tests with Docker LDAP server
```

### Code Quality

```bash
make lint         # Run strict linting (Ruff)
make format       # Format code
make type-check   # Strict MyPy type checking
make security     # Security analysis (Bandit)
```

### Singer Tap Operations

```bash
# Discovery
tap-ldap --config config.json --discover > catalog.json

# Extraction
tap-ldap --config config.json --catalog catalog.json

# Test connection
tap-ldap --config config.json --test

# LDIF processing
tap-ldap --config config.json --ldif export.ldif
```

## Code Architecture

### Core Components

- **`tap.py`**: Main `TapLDAP` class implementing Singer tap protocol
- **`client.py`**: Enterprise LDAP client with connection pooling and SSL support
- **`streams.py`**: Stream definitions for Users, Groups, OUs, and Schema
- **`config.py`**: Pydantic configuration with FLEXT core integration
- **`ldif_processor.py`**: LDIF file processing capabilities
- **`ldif_stream.py`**: LDIF streaming implementation

### FLEXT Framework Integration

The project uses FLEXT framework patterns:

- **Dependency Injection**: `@injectable()` decorator for service registration
- **Service Results**: `ServiceResult` types for error handling
- **Configuration**: Pydantic models extending `LDAPConnectionConfig`
- **Observability**: `flext-observability` for logging and monitoring
- **Domain-Driven Design**: Entities in `domain/` with business logic

### Data Streams

1. **Users Stream**: Extracts `inetOrgPerson`, `user` objects with incremental sync
2. **Groups Stream**: Extracts `groupOfNames`, `groupOfUniqueNames` objects
3. **Organizational Units**: Hierarchical `organizationalUnit` extraction
4. **Schema Stream**: LDAP schema metadata and attribute definitions
5. **Custom Streams**: Configurable LDAP queries via configuration

### Configuration System

Uses Pydantic models for type-safe configuration:

```python
class TapLDAPConfig(LDAPConnectionConfig, LDIFProcessingConfig):
    # Connection settings
    host: str
    port: int = 389
    bind_dn: str | None
    password: str | None
    base_dn: str
    use_ssl: bool = False

    # Performance tuning
    timeout: int = 30
    page_size: int = 1000

    # LDIF processing
    enable_ldif_streams: bool = False
    ldif_files: list[str] | None

    # Custom streams
    custom_streams: list[dict[str, Any]] | None
```

## Testing Infrastructure

### Test Organization

- **Unit Tests**: `tests/test_*.py` - Component testing with mocks
- **Integration Tests**: Tests with mock LDAP server
- **E2E Tests**: `tests/e2e/` - Docker-based OpenLDAP server testing
- **Test Data**: `tests/e2e/ldif/` - Sample LDIF files for testing

### Docker Test Environment

- OpenLDAP server with test data
- Automated setup via Docker Compose
- Configurable for different LDAP schemas

## Current Migration Status

The project is undergoing migration to FLEXT framework standards:

### Completed

- Pydantic configuration system
- FLEXT core integration
- Domain-driven design patterns
- Application service layer

### In Progress (Based on Git Status)

- **Logging Migration**: Moving from standard logging to `flext-observability`
- **Configuration Refactor**: New configuration files (not yet committed)
- **Service Layer**: New application services with dependency injection

Refer to `LOGGING_MIGRATION.md` for logging migration details.

## Enterprise Features

### Performance & Scalability

- **Connection Pooling**: Multiple concurrent LDAP connections
- **Paged Results**: Handles large directories (1000+ entries per page)
- **Incremental Sync**: Uses `modifyTimestamp` for change tracking
- **Memory Efficiency**: Streaming processing for large datasets

### Security

- **SSL/TLS Support**: LDAPS with certificate validation
- **SASL Authentication**: Advanced authentication mechanisms
- **Credential Management**: Secure handling of bind credentials

### Integration

- **Singer Protocol**: Full compliance with Singer specification
- **Meltano Compatible**: Can be used as Meltano extractor
- **FLEXT Ecosystem**: Integration with other FLEXT framework components

## Development Guidelines

### Code Quality Standards

- **Coverage**: 90%+ test coverage required
- **Type Checking**: Strict MyPy configuration
- **Linting**: Ruff with strict ruleset
- **Security**: Bandit security analysis

### Architecture Patterns

- Follow hexagonal architecture principles
- Use dependency injection for services
- Implement domain entities with business logic
- Use service result patterns for error handling

### LDAP-Specific Considerations

- Handle different LDAP server implementations (AD, OpenLDAP, Oracle)
- Manage connection timeouts and retries
- Process large directories efficiently
- Handle unicode and special characters properly

## Debugging & Troubleshooting

### LDAP Connection Issues

```bash
# Test LDAP connectivity directly
export TAP_LDAP_LOG_LEVEL=DEBUG
tap-ldap --config config.json --test

# Enable LDAP trace logging
export LDAP_TRACE_LEVEL=2
```

### Performance Optimization

- Adjust `page_size` for memory vs speed tradeoff
- Use connection pooling for concurrent extractions
- Monitor memory usage with large directories

### Common Issues

- **Connection Timeout**: Increase `timeout` in configuration
- **Memory Issues**: Reduce `page_size`, enable streaming
- **Authentication**: Verify bind DN format and credentials
- **Large Attributes**: Handle binary and large text attributes properly
