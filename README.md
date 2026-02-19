# FLEXT-Tap-LDAP

<!-- TOC START -->

- [🚀 Key Features](#-key-features)
- [📦 Installation](#-installation)
- [🛠️ Usage](#-usage)
  - [Connection Settings](#connection-settings)
  - [Stream Customization](#stream-customization)
- [🏗️ Architecture](#-architecture)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

<!-- TOC END -->

[![Singer SDK](https://img.shields.io/badge/singer--sdk-compliant-brightgreen.svg)](https://sdk.meltano.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**FLEXT-Tap-LDAP** extracts data directly from enterprise LDAP directories (Active Directory, OpenLDAP, etc.). It enables real-time synchronization of organizational data into analytical backends.

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

## 🚀 Key Features

- **Multi-Attribute Search**: Configurable search filters (`ldap_filter`) and base DNs.
- **Paging Support**: Handles large result sets efficiently with server-side paging.
- **Security**: Supports StartTLS/LDAPS and bind DN authentication.
- **Operational Attributes**: Extracts critical metadata (`createTimestamp`, `modifyTimestamp`) for incremental replication.
- **Multiple Object Classes**: Streams for `Users`, `Groups`, and `OrganizationalUnits`.

## 📦 Installation

To usage in your Meltano project, add the extractor to your `meltano.yml`:

```yaml
plugins:
  extractors:
    - name: tap-ldap
      pip_url: flext-tap-ldap
      config:
        host: ${LDAP_HOST}
        port: 636
        use_ssl: true
        base_dn: ${LDAP_BASE_DN}
        bind_dn: ${LDAP_BIND_DN}
        password: ${LDAP_PASSWORD}
```

## 🛠️ Usage

### Connection Settings

Configure the tap for secure connectivity:

```json
{
  "host": "ad.example.com",
  "port": 636,
  "use_ssl": true,
  "start_tls": false,
  "timeout": 30,
  "page_size": 1000
}
```

### Stream Customization

Define custom streams for specific object classes or attributes:

```json
{
  "custom_streams": [
    {
      "name": "developers",
      "search_filter": "(&(objectClass=person)(memberOf=CN=Developers,OU=Groups,DC=example,DC=com))",
      "attributes": ["cn", "mail", "githubId"]
    }
  ]
}
```

## 🏗️ Architecture

Built on the Singer SDK, ensuring compatibility with all major Targets:

- **Client**: Encapsulates `python-ldap` logic for connection management.
- **Discovery**: Automatically maps LDAP object classes to Singer schemas.
- **Incremental Sync**: Leverages `modifyTimestamp` for efficient updates.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/development.md) for details on adding new stream types or enhancing filter capabilities.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
