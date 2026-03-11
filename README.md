# CESSDA MCP Datasets Server

<!--
SPDX-License-Identifier: Apache-2.0
-->

MCP (Model Context Protocol) server for searching CESSDA research datasets. Enables AI assistants like Claude to search and discover social science research datasets from 22 European data archives.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Claude Desktop Setup](#claude-desktop-setup)
  - [Available Tools](#available-tools)
  - [Example Prompts](#example-prompts)
- [Development](#development)
- [Operations](#operations)
- [License](#license)

## Overview

This MCP server provides AI assistants with access to the [CESSDA Data Catalogue](https://datacatalogue.cessda.eu/), which contains metadata for social science research datasets from European data archives.

### Features

- 🔍 Search datasets by keywords, topics, countries, and date ranges
- 📊 Access metadata from 22 European social science data archives
- 🤖 Seamless integration with Claude Desktop and other MCP clients
- 🐳 Docker containerization support
- 📝 Structured JSON logging following CESSDA guidelines
- ⚙️ Configuration via environment variables (12-factor app)

### Available Tools

1. **search_cessda_datasets** - Search research datasets with flexible filtering
2. **get_cessda_filters** - Discover available filter values (topics, publishers, countries, languages)

## Installation

### Requirements

- Python 3.10 or higher
- pip

### Install from Source

```bash
# Clone the repository
git clone https://github.com/cessda/cessda.ai.mcp.cdc.git
cd cessda.ai.mcp.cdc

# Install in development mode
pip install -e .
```

### Install from PyPI (when published)

```bash
pip install mcp-cessda-datasets
```

### Verify Installation

```bash
mcp-cessda-datasets --help
```

## Configuration

The server follows the 12-factor app methodology and is configured via environment variables.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CESSDA_API_BASE_URL` | `https://datacatalogue.cessda.eu/api` | CESSDA API base URL |
| `CESSDA_API_TIMEOUT` | `30` | API request timeout (seconds) |
| `CESSDA_API_MAX_RETRIES` | `3` | Maximum retry attempts |
| `CESSDA_LOG_LEVEL` | `WARN` | Logging level (INFO, WARN, ERROR) |
| `CESSDA_DEFAULT_LANGUAGE` | `en` | Default metadata language |
| `CESSDA_DEFAULT_LIMIT` | `10` | Default search result limit |
| `CESSDA_MAX_LIMIT` | `200` | Maximum search result limit |

### Configuration File (Optional)

Create a `.env` file in your working directory:

```bash
CESSDA_API_TIMEOUT=60
CESSDA_LOG_LEVEL=INFO
CESSDA_DEFAULT_LIMIT=20
```

## Usage

### Claude Desktop Setup

1. **Locate your Claude Desktop configuration file:**

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add the MCP server configuration:**

```json
{
  "mcpServers": {
    "cessda-datasets": {
      "command": "python",
      "args": ["-m", "mcp_cessda_datasets.server"],
      "env": {
        "CESSDA_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Or if installed via pip:

```json
{
  "mcpServers": {
    "cessda-datasets": {
      "command": "mcp-cessda-datasets"
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Verify the server is connected** - Look for the MCP icon or check available tools

### Available Tools

#### 1. search_cessda_datasets

Search for research datasets with various filters.

**Parameters:**
- `query` (optional): Free-text search query
- `classifications` (optional): Topic filters (e.g., ["Political science", "Sociology"])
- `study_area_countries` (optional): Country filters (e.g., ["Sweden", "Norway"])
- `publishers` (optional): Data archive filters
- `keywords` (optional): Subject keyword filters
- `year_min` (optional): Earliest data collection year
- `year_max` (optional): Latest data collection year
- `language` (optional): Metadata language (ISO 639-1 code, default: "en")
- `limit` (optional): Max results (1-200, default: 10)
- `offset` (optional): Pagination offset (default: 0)

**Returns:** Search results with dataset metadata (title, abstract, creators, access URLs, etc.)

#### 2. get_cessda_filters

Get available values for filter types.

**Parameters:**
- `filter_type` (required): One of "classifications", "publishers", "countries", "languages"

**Returns:** List of valid values for the specified filter type

### Example Prompts

Try these prompts in Claude Desktop:

1. **Basic search:**
   > "Find datasets about climate change"

2. **Filtered search:**
   > "Show me political science datasets from Nordic countries collected between 2015 and 2020"

3. **Discover filters:**
   > "What topic classifications are available in CESSDA?"

4. **Advanced search:**
   > "Find datasets about unemployment published by the UK Data Service, in English, limited to 5 results"

5. **Multi-country search:**
   > "Search for datasets about migration in Germany, France, and Italy"

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/cessda/cessda.ai.mcp.cdc.git
cd cessda.ai.mcp.cdc

# Install with development dependencies
pip install -e ".[dev]"
```

### Project Structure

```
mcp-cessda-datasets/
├── LICENSE.txt                    # Apache 2.0 license
├── CONTRIBUTING.md                # Contribution guidelines
├── README.md                      # This file
├── pyproject.toml                 # Python package configuration
├── Dockerfile                     # Container image
└── src/
    └── mcp_cessda_datasets/
        ├── __init__.py           # Package initialization
        ├── server.py             # FastMCP server with tools
        ├── tools.py              # CESSDA API integration
        ├── config.py             # Environment configuration
        └── logging_config.py     # Structured JSON logging
```

### Code Standards

This project follows CESSDA Technical Guidelines:

- **Style**: PEP 8 (enforced via `black` and `ruff`)
- **Type Hints**: Required for all public functions
- **Documentation**: Docstrings for all modules, classes, and functions
- **Logging**: Structured JSON to stdout
- **Configuration**: Environment variables only (no hardcoded values)
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=mcp_cessda_datasets

# Format code
black src/

# Lint code
ruff check src/
```

### Adding New Features

1. Create a new branch
2. Add your feature with tests
3. Update documentation
4. Follow commit message conventions
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Operations

### Running in Docker

```bash
# Build image
docker build -t cessda/mcp-datasets:0.1.0 .

# Run container (STDIO mode)
docker run -i cessda/mcp-datasets:0.1.0
```

### Logging

The server outputs structured JSON logs to stdout following CESSDA guidelines:

```json
{
  "timestamp": "2025-01-15T10:30:45.123456Z",
  "level": "INFO",
  "message": "API request successful",
  "logger": "mcp_cessda_datasets",
  "results_count": 10,
  "total_available": 245
}
```

**Log Levels:**
- `INFO`: Informational messages (API requests, results)
- `WARN`: Warnings requiring attention (rate limits, validation issues)
- `ERROR`: Errors requiring investigation (API failures, exceptions)

### Monitoring

Monitor the server using:
- JSON log aggregation (ELK, Splunk, etc.)
- Check for `ERROR` and `WARN` level messages
- Track API response times and failure rates
- Monitor dataset search patterns

### Troubleshooting

**Issue:** Server not appearing in Claude Desktop

- Verify configuration file path and JSON syntax
- Check server installation: `which mcp-cessda-datasets`
- Review Claude Desktop logs for errors
- Restart Claude Desktop after configuration changes

**Issue:** API timeouts

- Increase `CESSDA_API_TIMEOUT` environment variable
- Check network connectivity to CESSDA API
- Review structured logs for timeout patterns

**Issue:** Empty search results

- Use `get_cessda_filters` to verify filter values
- Check spelling of countries, classifications, publishers
- Try broader search criteria or remove filters
- Verify metadata language matches available data

## Versioning

This project uses semantic versioning:

- **MAJOR**: Breaking changes to API or configuration
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Current version: **0.1.0**

See [CESSDA Release Guidelines](https://docs.tech.cessda.eu/software/releases.html) for details.

## License

Copyright © 2025 CESSDA ERIC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See [LICENSE.txt](LICENSE.txt) for full license text.

## Links

- [CESSDA Data Catalogue](https://datacatalogue.cessda.eu/)
- [CESSDA Technical Documentation](https://docs.tech.cessda.eu/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Issue Tracker](https://github.com/cessda/cessda.ai.mcp.cdc/issues)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
