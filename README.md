# ScholarsQuill

**Academic PDF Processing with MCP Server + AI Agent Integration**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## What is ScholarsQuill?

ScholarsQuill is an **MCP server** that provides PDF processing capabilities to **AI Agent**. This hybrid architecture combines reliable PDF extraction with intelligent AI analysis to automatically generate structured literature notes, citation network visualizations, and discourse pattern analysis - making academic research more efficient and insightful.

## Quick Start

### 1. Install ScholarsQuill

```bash
# Clone the repository
git clone https://github.com/scholarsquill/scholarsquill.git
cd scholarsquill

# Install dependencies
pip install typer rich PyPDF2 pdfplumber jinja2 networkx plotly pyzotero

# Install slash commands to Claude Code
./scholarsquill install
```

### 2. Restart Claude Code

Completely quit and restart Claude Code to load the commands.

### 3. Use ScholarsQuill Commands

In Claude Code, you now have access to four powerful slash commands:

```bash
/note research_paper.pdf --focus research --depth standard
/citemap research_paper.pdf --batch
/codelang research_paper.pdf --focus terminology --field biology
/zotero --collection ABC123 --template research
```

**See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions and troubleshooting.**

## What You Get

### Literature Notes (`/note`)
Generate structured literature notes with intelligent AI analysis.

**Command**: `/note paper.pdf --focus research --depth standard`

**Output**: `[citekey].md` (e.g., `smith2020protein.md`)

**Features**:
- Author-year-keyword format citekeys
- Focus-specific templates (research, theory, method, review, balanced)
- Analysis depth levels (quick, standard, deep)
- Obsidian-style PDF links `[[source.pdf]]`
- Batch processing support

**Arguments**:
- `target` - PDF file or directory path
- `--focus` - Analysis focus (default: balanced)
- `--depth` - Analysis depth (default: standard)
- `--batch` - Process multiple files
- `--output` - Output directory (default: literature-notes/)

### Citation Networks (`/citemap`)
Build interactive citation network visualizations.

**Command**: `/citemap paper.pdf --batch`

**Output**:
- `[citekey]_citemap.md` - Citation context analysis
- `[citekey]_citemap_network.html` - Interactive network visualization

**Features**:
- Citation context extraction
- Reference network building
- Cross-paper relationship analysis
- Interactive HTML visualizations
- Intellectual lineage mapping

**Arguments**:
- `target` - PDF file or directory path
- `--batch` - Enable cross-reference analysis
- `--keyword` - Custom batch filename keyword
- `--output` - Output directory (default: citemap-analysis/)

### Discourse Analysis (`/codelang`)
Analyze academic discourse patterns and field-specific language.

**Command**: `/codelang paper.pdf --focus terminology --field biology`

**Output**: `[citekey]_codelang.md` (e.g., `smith2020protein_codelang.md`)

**Features**:
- Field-specific terminology extraction
- Discourse architecture mapping
- Rhetorical pattern analysis
- Section-by-section functional analysis
- Academic language conventions

**Arguments**:
- `target` - PDF file or directory path
- `--field` - Academic field (auto-detect, physics, cs, biology, etc.)
- `--focus` - Analysis type (discourse, architecture, terminology, rhetoric, sections, functions, summary)
- `--section` - Section filter (all, introduction, methods, results, discussion)
- `--depth` - Analysis depth (quick, standard, deep)
- `--batch` - Process multiple files
- `--output` - Output directory (default: codelang-analysis/)

### Zotero Integration (`/zotero`)
Sync your Zotero library to Obsidian with automated literature note generation.

**Command**: `/zotero --collection ABC123 --template research`

**Output**: Obsidian-compatible markdown notes in your vault

**Features**:
- Direct Zotero API integration
- Automatic metadata mapping (authors, year, DOI, tags, collections)
- Batch processing with progress tracking
- Citekey collision handling
- 24-hour caching to reduce API calls
- Checkpoint system for large batches
- Bidirectional links (Zotero ↔ Obsidian)

**Arguments**:
- `--collection <id>` - Process specific Zotero collection
- `--all` - Process entire library
- `--limit <n>` - Limit number of items
- `--item <key>` - Process single item
- `--template <name>` - Template choice (balanced, research, theory, method, review)
- `--output <path>` - Obsidian vault path

**Setup**:
1. Get Zotero API key from https://www.zotero.org/settings/keys/new
2. Set environment variables:
   ```bash
   export ZOTERO_LIBRARY_ID=your_library_id
   export ZOTERO_LIBRARY_TYPE=user  # or 'group'
   export ZOTERO_API_KEY=your_api_key
   ```
3. Run `/zotero --collection <id>`

## Example Workflow

### PDF-based Workflow
```bash
# 1. Install ScholarsQuill
cd scholarsquill
./scholarsquill install

# 2. Restart Claude Code

# 3. Process PDFs in Claude Code
/note papers/protein_folding.pdf --focus research --depth deep
# → Output: literature-notes/smith2020protein.md

/citemap papers/protein_folding.pdf
# → Output: citemap-analysis/smith2020protein_citemap.md
#          citemap-analysis/smith2020protein_citemap_network.html

/codelang papers/protein_folding.pdf --focus terminology --field biology
# → Output: codelang-analysis/smith2020protein_codelang.md

# 4. Open interactive citation network in browser
open citemap-analysis/smith2020protein_citemap_network.html
```

### Zotero-based Workflow
```bash
# 1. Configure Zotero credentials
export ZOTERO_LIBRARY_ID=12345
export ZOTERO_LIBRARY_TYPE=user
export ZOTERO_API_KEY=your_api_key_here

# 2. Sync Zotero collection to Obsidian
/zotero --collection ABC123 --template research --output ~/Obsidian/Vault
# → Processing: Machine Learning Papers (50 items)
# → Output: 50 notes in ~/Obsidian/Vault/Machine_Learning/

# 3. Process entire library with limit
/zotero --all --limit 100 --template balanced
# → Output: 100 notes with comprehensive analysis

# 4. Single item processing
/zotero --item XYZ789 --template theory
# → Output: Single detailed theory-focused note
```

## ScholarsQuill CLI

The CLI tool manages installation and configuration:

```bash
./scholarsquill install    # Install slash commands to Claude Code
./scholarsquill check      # Verify installation status
./scholarsquill uninstall  # Remove slash commands
./scholarsquill version    # Show version information
```

### Installation Status Check

```bash
./scholarsquill check
```

Displays:
- Commands directory status
- Individual command installation (✓ /note, /citemap, /codelang)
- MCP server configuration status
- Python dependency status

## Architecture

### MCP Server + AI Agent Integration

```
Claude Code AI Agent
        ↕ (MCP Protocol)
ScholarsQuill MCP Server
        ↓
PDF Processing + Templates
        ↓
Intelligent Literature Notes
```

**Division of Labor**:
- **MCP Server**: PDF extraction, metadata parsing, template provision
- **AI Agent**: Intelligent analysis, comprehension, note generation

**Benefits**:
- Reliable PDF processing with consistent quality
- Flexible AI analysis adapting to content
- Separation of concerns for maintainability
- Scalable batch processing

## Supported AI Agents

| Agent                                                     | Support | MCP Integration |
|-----------------------------------------------------------|---------|-----------------|
| [Claude Code](https://www.anthropic.com/claude-code)     | Full    | Native MCP      |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli)| Planned | Future          |
| Custom MCP Client                                         | Yes     | Compatible      |

## Prerequisites

- **Python 3.8+** (Python 3.10+ required for full MCP functionality)
- **Claude Code** or other MCP-compatible AI agent
- **Git** (optional, for cloning repository)

## Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide with troubleshooting
- **[QUICK_START.md](QUICK_START.md)** - Detailed usage instructions
- **[CURRENT_ARCHITECTURE.md](CURRENT_ARCHITECTURE.md)** - Technical architecture overview
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

## Troubleshooting

### Commands Not Appearing

1. Check installation: `./scholarsquill check`
2. Verify MCP server configuration in Claude Desktop config
3. Completely restart Claude Code (quit and relaunch)
4. Wait 10-15 seconds for MCP server initialization

### MCP Server Issues

**Common problem**: Wrong server path in configuration

**Solution**: Must use `src.legacy_mcp_server.server` NOT `src.server`

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.**

## Why ScholarsQuill?

**Before ScholarsQuill:**
- Manual PDF reading and note-taking
- Lost track of citation relationships
- Tedious literature review process
- Isolated paper analysis

**After ScholarsQuill:**
- Automated structured note generation with AI intelligence
- Visual citation network exploration
- Efficient literature review workflows
- Connected understanding of research landscape
- Field-specific discourse analysis

## Core Features

### Intelligent Literature Notes
- Multi-template system (research, theory, method, review, balanced)
- Structured analysis (methodology, findings, implications)
- Academic formatting ready for research workflows
- Citekey-based organization (authorYEARkeyword)
- Obsidian integration with PDF links
- **NEW**: Zotero metadata integration with bidirectional links

### Interactive Citation Networks
- Visual network exploration of paper connections
- Citation context understanding
- Interactive HTML with clickable relationships
- Network analysis identifying key papers
- Cross-paper relationship mapping
- **NEW**: Zotero relationship extraction and citation network enhancement

### Discourse Pattern Analysis
- Field-specific terminology extraction
- Argument structure mapping
- Rhetorical device identification
- Academic discourse conventions
- Section-by-section functional analysis

### Zotero → Obsidian Sync
- Direct Zotero API integration
- Automatic metadata extraction and mapping
- Batch processing with progress tracking and checkpoints
- Smart caching (24-hour TTL, 70%+ hit rate)
- Citekey collision handling with numeric suffixes
- Collection hierarchy preservation in folder structure
- Bidirectional linking (Zotero URLs in notes)
- Support for all common item types (articles, books, conferences, theses)

### Modern MCP Integration
- Standard protocol works with any MCP-compatible agent
- One-time setup for seamless use
- Clean tool interface (sq_note, sq_citemap, sq_codelang)
- Slash command convenience in Claude Code
- **NEW**: `/zotero` command for library sync

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Acknowledgments

ScholarsQuill builds on:
- **Model Context Protocol (MCP)** for AI agent integration
- **Modern Python ecosystem** (setuptools, typer, rich)
- **Academic research workflows** and best practices
- **Open source PDF processing** (PyPDF2, pdfplumber)

---

**Ready to transform your research workflow?**

```bash
git clone https://github.com/scholarsquill/scholarsquill.git
cd scholarsquill
./scholarsquill install
```

*ScholarsQuill - Making academic research more efficient, one paper at a time.*
