# CLAUDE.local.md - TAP-LDAP PROJECT SPECIFICS

**Hierarquia**: **PROJECT-SPECIFIC**  
**Projeto**: Tap LDAP - Enterprise Directory Data Extraction  
**Status**: PRODUCTION READY - Active production use  
**Framework**: Singer Protocol + LDAP v3 + Meltano Compatible  
**Última Atualização**: 2025-06-26

**Referência Global**: `/home/marlonsc/CLAUDE.md` → Universal principles  
**Referência Workspace**: `../CLAUDE.md` → PyAuto workspace patterns  
**Referência Cross-Workspace**: `/home/marlonsc/CLAUDE.local.md` → Cross-workspace issues

---

## 🎯 PROJECT-SPECIFIC CONFIGURATION

### Virtual Environment Usage

```bash
# MANDATORY: Use workspace venv
source /home/marlonsc/pyauto/.venv/bin/activate
# NOT project-specific venv
```

### Agent Coordination

```bash
# Read workspace coordination first
cat /home/marlonsc/pyauto/.token | tail -5
# Use project .token only for project-specific coordination
```

### Project-Specific Environment Variables

```bash
# Tap LDAP specific configurations
export TAP_LDAP_HOST=ldap.company.com
export TAP_LDAP_PORT=636
export TAP_LDAP_BIND_DN="cn=service-account,ou=service accounts,dc=company,dc=com"
export TAP_LDAP_PASSWORD=secure_ldap_password
export TAP_LDAP_BASE_DN="dc=company,dc=com"
export TAP_LDAP_USE_SSL=true
export TAP_LDAP_LOG_LEVEL=DEBUG
export TAP_LDAP_PAGE_SIZE=1000
export TAP_LDAP_TIMEOUT=30
```

---

## 🏗️ TAP LDAP ARCHITECTURE

### **Purpose & Role**

- **Singer Protocol Tap**: Standardized data extraction from LDAP directories
- **Identity Data Source**: Primary source for user and group analytics
- **Directory Integration**: Bridge between LDAP/AD and data platforms
- **Incremental Sync**: Efficient change tracking via modifyTimestamp
- **Schema Discovery**: Automatic detection of LDAP schema attributes

### **Core Singer Components**

```python
# Singer protocol implementation structure
src/tap_ldap/
├── tap.py               # Main Singer tap implementation
├── client.py            # LDAP connection and operations
├── streams.py           # Stream definitions (users, groups, OUs)
├── ldif_processor.py    # LDIF file processing capabilities
├── ldif_stream.py       # LDIF streaming interface
└── __init__.py          # Package exports
```

### **Production Data Streams**

- **Users Stream**: inetOrgPerson, user, organizationalPerson objects
- **Groups Stream**: groupOfNames, groupOfUniqueNames, group objects
- **Organizational Units**: organizationalUnit hierarchy
- **Schema Stream**: LDAP schema metadata and attribute definitions
- **Custom Streams**: Configurable LDAP filters for specific queries

---

## 🔧 PROJECT-SPECIFIC TECHNICAL DETAILS

### **Development Commands**

```bash
# MANDATORY: Always from workspace venv
source /home/marlonsc/pyauto/.venv/bin/activate

# Singer protocol development
make install-dev       # Install development dependencies
make test              # Run complete test suite
make test-unit         # Unit tests only
make test-integration  # Integration tests with mock LDAP
make test-e2e          # End-to-end tests with Docker LDAP
make lint              # Code quality checks
make format            # Code formatting

# Singer tap operations
tap-ldap --config config.json --discover > catalog.json
tap-ldap --config config.json --catalog catalog.json --debug
tap-ldap --config config.json --test-connection
```

### **LDAP Connection Testing**

```bash
# Test LDAP connectivity
tap-ldap --config config.json --test

# Test with debug logging
export TAP_LDAP_LOG_LEVEL=DEBUG
export LDAP_TRACE_LEVEL=2
tap-ldap --config config.json --discover

# Test specific streams
tap-ldap --config config.json --catalog catalog.json --debug | head -100
```

### **Meltano Integration**

```bash
# Add to Meltano project
meltano add extractor tap-ldap

# Run via Meltano
meltano invoke tap-ldap --discover
meltano elt tap-ldap target-postgres --job_id=ldap_sync

# State management
meltano elt tap-ldap target-postgres --state_id=ldap_incremental
```

---

## 🚨 PROJECT-SPECIFIC KNOWN ISSUES

### **LDAP-Specific Challenges**

- **Large Directory Performance**: Memory usage with millions of entries
- **Paging Complexity**: Different LDAP servers implement paging differently
- **Schema Variations**: Active Directory vs OpenLDAP schema differences
- **Connection Stability**: Long-running extractions may timeout
- **Attribute Encoding**: Unicode and special character handling

### **Singer Protocol Considerations**

```python
# LDAP-specific Singer patterns
class LDAPSingerPatterns:
    """Production patterns for LDAP Singer implementation."""

    def handle_large_directories(self):
        """Handle directories with millions of entries."""
        # Use server-side paging
        page_size = min(1000, self.config.page_size)

        # Process in chunks to manage memory
        for page in self.ldap_client.paged_search(
            base_dn=self.base_dn,
            search_filter=self.user_filter,
            page_size=page_size
        ):
            for entry in page:
                yield self.transform_ldap_entry(entry)

    def incremental_bookmark_strategy(self):
        """Implement incremental sync with modifyTimestamp."""
        # Handle different timestamp formats across LDAP servers
        timestamp_formats = [
            "%Y%m%d%H%M%S.%fZ",      # GeneralizedTime
            "%Y%m%d%H%M%SZ",         # GeneralizedTime short
            "%Y-%m-%d %H:%M:%S",     # SQL format
        ]
        return self.parse_ldap_timestamp(value, timestamp_formats)
```

### **Production Error Handling**

```bash
# Common LDAP extraction issues
1. Connection Timeout: Increase network_timeout in config
2. Memory Issues: Reduce page_size, enable streaming
3. Authentication: Verify bind DN format and credentials
4. Large Attributes: Handle binary and large text attributes
5. Special Characters: Ensure proper UTF-8 encoding
```

---

## 🎯 PROJECT-SPECIFIC SUCCESS METRICS

### **Singer Protocol Compliance**

- **Schema Discovery**: 100% automatic stream detection
- **State Management**: Incremental sync with reliable bookmarks
- **Error Handling**: Graceful handling of LDAP server issues
- **Data Quality**: Complete and accurate directory data extraction
- **Performance**: >1000 entries/second extraction rate

### **Production Extraction Goals**

- **Data Completeness**: 100% user and group data extraction
- **Incremental Efficiency**: <5 minute sync cycles for changes
- **Connection Reliability**: 99%+ successful LDAP connections
- **Memory Efficiency**: <500MB memory usage for large directories
- **Error Recovery**: Automatic retry with exponential backoff

---

## 🔗 PROJECT-SPECIFIC INTEGRATIONS

### **Singer Ecosystem Integration**

- **Target Compatibility**: Works with all Singer-compliant targets
- **Meltano Plugin**: Official Meltano Hub plugin available
- **Schema Registry**: Automatic schema discovery and validation
- **State Management**: Full incremental sync capability

### **PyAuto Ecosystem Integration**

- **ldap-core-shared**: Shared LDAP models and utilities
- **target-ldap**: Round-trip synchronization capabilities
- **flext-ldap**: Advanced LDAP migration features
- **algar-oud-mig**: Migration project data source

### **Enterprise LDAP Integration**

```python
# Production LDAP configuration patterns
class ProductionLDAPConfig:
    """Production LDAP configuration for enterprise directories."""

    # Active Directory configuration
    AD_CONFIG = {
        "host": "dc.company.com",
        "port": 636,
        "use_ssl": True,
        "validate_certs": True,
        "bind_dn": "CN=svc-tap-ldap,OU=Service Accounts,DC=company,DC=com",
        "base_dn": "DC=company,DC=com",
        "user_filter": "(&(objectClass=user)(objectCategory=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))",
        "group_filter": "(&(objectClass=group))",
        "page_size": 1000,
        "timeout": 60,
    }

    # OpenLDAP configuration
    OPENLDAP_CONFIG = {
        "host": "ldap.company.com",
        "port": 636,
        "use_ssl": True,
        "bind_dn": "cn=tap-ldap,ou=service accounts,dc=company,dc=com",
        "base_dn": "dc=company,dc=com",
        "user_filter": "(objectClass=inetOrgPerson)",
        "group_filter": "(objectClass=groupOfNames)",
        "page_size": 500,
        "timeout": 30,
    }
```

---

## 📊 PROJECT-SPECIFIC MONITORING

### **Singer Protocol Metrics**

```python
# Key metrics for Singer tap monitoring
TAP_LDAP_METRICS = {
    "extraction_rate": "Records extracted per second",
    "schema_discovery_time": "Time to discover all streams",
    "state_bookmark_accuracy": "Incremental sync accuracy",
    "memory_usage_peak": "Peak memory during extraction",
    "connection_success_rate": "LDAP connection reliability",
    "data_completeness": "Percentage of expected records extracted",
}
```

### **LDAP-Specific Health Checks**

```bash
# Production monitoring commands
tap-ldap --config config.json --test                    # Connection test
tap-ldap --config config.json --discover --validate     # Schema validation
tap-ldap --config config.json --catalog catalog.json --dry-run  # Dry run test
```

---

## 📋 PROJECT-SPECIFIC MAINTENANCE

### **Regular Maintenance Tasks**

- **Daily**: Monitor extraction performance and connection health
- **Weekly**: Review incremental sync accuracy and bookmark positions
- **Monthly**: Update LDAP service account passwords and certificates
- **Quarterly**: Review and update stream schemas for directory changes

### **Singer Protocol Updates**

```bash
# Keep Singer SDK updated
pip install --upgrade singer-sdk

# Validate Singer compliance
singer-check-tap --tap tap-ldap --config config.json
singer-check-schema --schema users.json
```

### **Emergency Procedures**

```bash
# LDAP emergency troubleshooting
1. Test LDAP connectivity: ldapsearch -H $LDAP_URI -D "$BIND_DN" -w "$PASSWORD" -b "$BASE_DN" "(objectClass=*)" dn
2. Reset bookmark state: rm state.json && meltano elt tap-ldap target-postgres
3. Enable debug logging: export TAP_LDAP_LOG_LEVEL=DEBUG
4. Check directory server health: tap-ldap --config config.json --test
```

---

**PROJECT SUMMARY**: Singer protocol tap para extração de dados empresariais de diretórios LDAP/Active Directory com suporte a sincronização incremental e descoberta automática de schema.

**CRITICAL SUCCESS FACTOR**: Manter compatibilidade total com protocolo Singer enquanto oferece extração eficiente e confiável de dados de identidade corporativa.

---

_Última Atualização: 2025-06-26_  
_Próxima Revisão: Semanal durante sincronizações ativas_  
_Status: PRODUCTION READY - Uso ativo em produção com múltiplos targets_
