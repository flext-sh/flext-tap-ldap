# 📤 Tap LDAP - Enterprise Directory Data Extraction

> **Function**: Production-grade Singer tap for LDAP/Active Directory data extraction with incremental sync | **Audience**: Directory Engineers, Identity Management Teams | **Status**: Production Ready

[![Singer](https://img.shields.io/badge/singer-tap-blue.svg)](https://www.singer.io/)
[![LDAP](https://img.shields.io/badge/ldap-v3-green.svg)](https://ldap.com/)
[![Meltano](https://img.shields.io/badge/meltano-compatible-green.svg)](https://meltano.com/)
[![Python](https://img.shields.io/badge/python-3.9%2B-orange.svg)](https://www.python.org/)

**Enterprise Singer tap for extracting user, group, and organizational data from LDAP directories with support for custom schemas and incremental synchronization**

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../README.md) → **📂 Current**: Tap LDAP

---

## 🎯 **Core Purpose**

This Singer tap provides enterprise-grade data extraction from LDAP directories including Active Directory, OpenLDAP, and Oracle Directory Server. It enables identity governance, user analytics, and directory synchronization with advanced features for large-scale deployments.

### **Key Capabilities**

- **User & Group Extraction**: Complete identity and membership data
- **Custom Schema Support**: Flexible attribute mapping
- **Incremental Sync**: Efficient change detection via modifyTimestamp
- **Large Directory Support**: Paged results for millions of entries
- **Multi-Domain Support**: Cross-domain and forest extraction

### **Production Features**

- **Secure Authentication**: LDAP/LDAPS with SASL support
- **Connection Pooling**: Efficient connection management
- **Schema Discovery**: Automatic attribute detection
- **Performance Optimized**: Parallel extraction capabilities

---

## 🚀 **Quick Start**

### **Installation**

```bash
# Install via pip (recommended for production)
pip install tap-ldap

# Install via Meltano
meltano add extractor tap-ldap

# Install from source
git clone https://github.com/datacosmos-br/tap-ldap
cd tap-ldap
poetry install
```

### **Basic Configuration**

```json
{
  "host": "ldap.company.com",
  "port": 389,
  "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=company,dc=com",
  "password": "secure_password",
  "base_dn": "dc=company,dc=com",
  "use_ssl": false,
  "timeout": 30,
  "page_size": 1000,
  "user_filter": "(objectClass=inetOrgPerson)",
  "group_filter": "(objectClass=groupOfNames)"
}
```

### **Running the Tap**

```bash
# Discover available streams
tap-ldap --config config.json --discover > catalog.json

# Run extraction
tap-ldap --config config.json --catalog catalog.json

# With state management for incremental sync
tap-ldap --config config.json --catalog catalog.json --state state.json

# Pipe to target
tap-ldap --config config.json | target-postgres --config target-config.json
```

---

## 🏗️ **Architecture**

### **Singer Specification Compliance**

```
┌─────────────────────────────────────────┐
│         LDAP Directory Server           │
│    (Active Directory, OpenLDAP, etc.)   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│          LDAP v3 Protocol               │
│       (LDAP/LDAPS Connection)           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│            Tap LDAP                     │
│       (Singer Data Extractor)           │
├─────────────────────────────────────────┤
│ • Schema Discovery Engine               │
│ • Stream Processors                     │
│ • Paged Result Handler                  │
│ • State Management                      │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Singer Protocol                  │
│      (JSON Lines Output)                │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       Target System (Any)               │
│    (Database, Data Lake, etc.)          │
└─────────────────────────────────────────┘
```

### **Component Structure**

```
tap-ldap/
├── src/tap_ldap/
│   ├── __init__.py          # Package initialization
│   ├── tap.py               # Main tap class
│   ├── client.py            # LDAP client
│   ├── streams.py           # Stream definitions
│   ├── ldif_processor.py    # LDIF processing
│   ├── ldif_stream.py       # LDIF streaming
│   ├── schemas/             # JSON schemas
│   │   ├── user.py          # User schema
│   │   ├── group.py         # Group schema
│   │   └── custom.py        # Custom schemas
│   └── utils/               # Utilities
├── tests/                   # Test suite
├── examples/                # Usage examples
└── meltano.yml             # Meltano config
```

---

## 🔧 **Core Features**

### **1. Stream Catalog**

#### **Default Streams**

| Stream                 | Description                  | Key Attributes                |
| ---------------------- | ---------------------------- | ----------------------------- |
| `users`                | User entries (inetOrgPerson) | uid, cn, mail, memberOf       |
| `groups`               | Group entries (groupOfNames) | cn, member, description       |
| `organizational_units` | OUs structure                | ou, description               |
| `schema`               | LDAP schema information      | attributeTypes, objectClasses |

#### **Custom Streams**

Define custom streams for specific LDAP queries:

```json
{
  "custom_streams": [
    {
      "name": "service_accounts",
      "search_filter": "(&(objectClass=account)(uid=svc-*))",
      "search_scope": "SUBTREE",
      "attributes": ["uid", "description", "pwdLastSet"],
      "primary_keys": ["dn"],
      "replication_key": "modifyTimestamp",
      "schema": {
        "properties": {
          "dn": { "type": "string" },
          "uid": { "type": "string" },
          "description": { "type": "string" },
          "pwdLastSet": { "type": "string" },
          "modifyTimestamp": { "type": "string", "format": "date-time" }
        }
      }
    }
  ]
}
```

### **2. Advanced Filtering**

Complex LDAP filter support:

```json
{
  "user_filter": "(&(objectClass=inetOrgPerson)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))",
  "group_filter": "(&(objectClass=group)(groupType:1.2.840.113556.1.4.803:=2147483648))",
  "custom_filters": {
    "active_users": "(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(lastLogonTimestamp>=132514816000000000))",
    "distribution_lists": "(&(objectClass=group)(groupType:1.2.840.113556.1.4.803:=8))"
  }
}
```

### **3. Incremental Synchronization**

Efficient change tracking:

```json
{
  "bookmarks": {
    "users": {
      "replication_key": "modifyTimestamp",
      "replication_key_value": "20240619103000.0Z"
    },
    "groups": {
      "replication_key": "whenChanged",
      "replication_key_value": "20240619094500.0Z"
    }
  }
}
```

### **4. Performance Optimization**

```json
{
  "performance": {
    "page_size": 1000,
    "connection_pool_size": 5,
    "search_timeout": 60,
    "network_timeout": 30,
    "parallel_searches": true,
    "cache_schema": true
  }
}
```

### **5. Security Configuration**

```json
{
  "security": {
    "use_ssl": true,
    "validate_certs": true,
    "ca_certs_file": "/path/to/ca-bundle.crt",
    "client_cert_file": "/path/to/client.crt",
    "client_key_file": "/path/to/client.key",
    "sasl_mechanism": "GSSAPI",
    "kerberos_keytab": "/path/to/user.keytab"
  }
}
```

---

## 📊 **Data Models**

### **User Model**

```json
{
  "dn": "uid=john.doe,ou=users,dc=company,dc=com",
  "uid": "john.doe",
  "cn": "John Doe",
  "givenName": "John",
  "sn": "Doe",
  "mail": "john.doe@company.com",
  "telephoneNumber": "+1-555-1234",
  "department": "Engineering",
  "title": "Senior Engineer",
  "manager": "uid=jane.smith,ou=users,dc=company,dc=com",
  "memberOf": [
    "cn=engineers,ou=groups,dc=company,dc=com",
    "cn=vpn-users,ou=groups,dc=company,dc=com"
  ],
  "modifyTimestamp": "20240619103000.0Z",
  "createTimestamp": "20230115120000.0Z"
}
```

### **Group Model**

```json
{
  "dn": "cn=engineers,ou=groups,dc=company,dc=com",
  "cn": "engineers",
  "description": "Engineering team members",
  "member": [
    "uid=john.doe,ou=users,dc=company,dc=com",
    "uid=jane.smith,ou=users,dc=company,dc=com"
  ],
  "owner": "uid=tech.lead,ou=users,dc=company,dc=com",
  "groupType": "Security",
  "modifyTimestamp": "20240619094500.0Z"
}
```

---

## 🔐 **Authentication**

### **Simple Bind**

```json
{
  "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=company,dc=com",
  "password": "secure_password"
}
```

### **SASL Authentication**

```json
{
  "sasl_mechanism": "GSSAPI",
  "sasl_credentials": {
    "authz_id": "u:john.doe",
    "keytab": "/path/to/user.keytab"
  }
}
```

### **Anonymous Bind**

```json
{
  "anonymous_bind": true,
  "bind_dn": "",
  "password": ""
}
```

---

## 🧪 **Testing**

### **Test Coverage**

- Unit Tests: 93%+ coverage
- Integration Tests: Mock LDAP server
- End-to-End Tests: Docker-based LDAP
- Performance Tests: Large dataset handling

### **Running Tests**

```bash
# Unit tests
poetry run pytest tests/unit

# Integration tests
poetry run pytest tests/integration

# E2E tests with Docker
poetry run pytest tests/e2e

# All tests with coverage
poetry run pytest --cov=tap_ldap
```

---

## 📚 **Usage Examples**

### **Active Directory Extraction**

```python
# examples/active_directory.py
config = {
    "host": "dc.company.com",
    "port": 636,
    "use_ssl": True,
    "bind_dn": "CN=svc-account,OU=Service Accounts,DC=company,DC=com",
    "password": "secure_password",
    "base_dn": "DC=company,DC=com",
    "user_filter": "(&(objectClass=user)(objectCategory=person))",
    "group_filter": "(&(objectClass=group))",
    "attributes": {
        "users": ["sAMAccountName", "displayName", "mail", "memberOf", "whenChanged"],
        "groups": ["cn", "member", "description", "whenChanged"]
    }
}
```

### **OpenLDAP Extraction**

```python
# examples/openldap.py
config = {
    "host": "ldap.company.com",
    "port": 389,
    "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=company,dc=com",
    "password": "REDACTED_LDAP_BIND_PASSWORD_password",
    "base_dn": "dc=company,dc=com",
    "user_filter": "(objectClass=inetOrgPerson)",
    "group_filter": "(objectClass=groupOfNames)",
    "page_size": 500
}
```

### **LDIF Processing**

```python
# examples/ldif_processing.py
from tap_ldap import TapLDAP

# Process LDIF file
tap = TapLDAP(config={
    "ldif_file": "/path/to/export.ldif",
    "process_mode": "offline"
})

tap.process_ldif()
```

### **Meltano Integration**

```yaml
# meltano.yml
project_id: identity_analytics
environments:
  - name: prod
    config:
      plugins:
        extractors:
          - name: tap-ldap
            variant: datacosmos
            pip_url: tap-ldap
            config:
              host: ${LDAP_HOST}
              port: ${LDAP_PORT}
              bind_dn: ${LDAP_BIND_DN}
              password: ${LDAP_PASSWORD}
              base_dn: ${LDAP_BASE_DN}
              use_ssl: true
            select:
              - users.*
              - groups.*
```

---

## 🔗 **Integration Ecosystem**

### **Compatible Targets**

| Target             | Purpose                   | Status    |
| ------------------ | ------------------------- | --------- |
| `target-postgres`  | PostgreSQL warehouse      | ✅ Tested |
| `target-snowflake` | Cloud data warehouse      | ✅ Tested |
| `target-ldap`      | Directory synchronization | ✅ Tested |
| `target-csv`       | File-based export         | ✅ Tested |

### **PyAuto Integration**

| Component                                | Integration     | Purpose                   |
| ---------------------------------------- | --------------- | ------------------------- |
| [ldap-core-shared](../ldap-core-shared/) | Shared models   | LDAP domain models        |
| [target-ldap](../target-ldap/)           | Round-trip sync | Directory synchronization |
| [flext-ldap](../flext-ldap/)             | Migration tools | Directory migration       |

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Connection Timeouts**

   - **Symptom**: Connection to LDAP server times out
   - **Solution**: Check firewall rules, increase timeout settings

2. **Large Result Sets**

   - **Symptom**: Memory issues with large directories
   - **Solution**: Reduce page_size, enable streaming mode

3. **Authentication Failures**
   - **Symptom**: Bind operation failed
   - **Solution**: Verify DN format and credentials

### **Debug Mode**

```bash
# Enable debug logging
export TAP_LDAP_LOG_LEVEL=DEBUG

# Enable LDAP protocol tracing
export LDAP_TRACE_LEVEL=2

# Run with verbose output
tap-ldap --config config.json -v
```

---

## 🛠️ **CLI Reference**

```bash
# Discovery
tap-ldap --config config.json --discover > catalog.json

# Full sync
tap-ldap --config config.json --catalog catalog.json

# Incremental sync
tap-ldap --config config.json --catalog catalog.json --state state.json

# Test connection
tap-ldap --config config.json --test

# Process LDIF file
tap-ldap --config config.json --ldif export.ldif

# Version info
tap-ldap --version
```

---

## 📖 **Configuration Reference**

### **Required Settings**

| Setting    | Type   | Description                | Example                    |
| ---------- | ------ | -------------------------- | -------------------------- |
| `host`     | string | LDAP server hostname       | ldap.company.com           |
| `bind_dn`  | string | Bind DN for authentication | cn=REDACTED_LDAP_BIND_PASSWORD,dc=company,dc=com |
| `password` | string | Bind password              | secure_password            |
| `base_dn`  | string | Base DN for searches       | dc=company,dc=com          |

### **Optional Settings**

| Setting        | Type    | Description                  | Default                     |
| -------------- | ------- | ---------------------------- | --------------------------- |
| `port`         | integer | LDAP server port             | 389                         |
| `use_ssl`      | boolean | Use LDAPS                    | false                       |
| `timeout`      | integer | Connection timeout (seconds) | 30                          |
| `page_size`    | integer | Paged results size           | 1000                        |
| `user_filter`  | string  | User search filter           | (objectClass=inetOrgPerson) |
| `group_filter` | string  | Group search filter          | (objectClass=groupOfNames)  |

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Singer Specification](https://hub.meltano.com/singer/spec) - Singer protocol specification
- [LDAP Protocol](https://ldap.com/ldapv3-wire-protocol-reference/) - LDAP v3 reference
- [RFC 4511](https://datatracker.ietf.org/doc/html/rfc4511) - LDAP protocol specification

### **Next Steps**

- [Directory Integration Guide](../docs/guides/ldap-integration.md) - Complete LDAP guide
- [Identity Pipeline Setup](../docs/guides/identity-pipeline.md) - Identity data pipeline
- [Production Deployment](../docs/deployment/ldap-deployment.md) - Production setup

### **Related Topics**

- [Singer Best Practices](../docs/patterns/singer.md) - Singer tap patterns
- [Identity Management](../docs/patterns/identity.md) - Identity patterns
- [Directory Synchronization](../docs/patterns/directory-sync.md) - Sync strategies

---

**📂 Component**: Tap LDAP | **🏠 Root**: [PyAuto Home](../README.md) | **Framework**: Singer SDK 0.39.0+ | **Updated**: 2025-06-19
