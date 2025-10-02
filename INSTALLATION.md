# ScholarsQuill Installation Guide

Complete guide to installing and configuring ScholarsQuill for Claude Code.

## Prerequisites

- Python 3.8+ installed
- Claude Code installed
- Git (optional, for cloning repository)

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/scholarsquill/scholarsquill.git
cd scholarsquill

# Install dependencies
pip install typer rich PyPDF2 pdfplumber jinja2 networkx plotly

# Run installation
./scholarsquill install
```

### Method 2: Development Install

```bash
# Clone the repository
git clone https://github.com/scholarsquill/scholarsquill.git
cd scholarsquill

# Install in development mode (with all dependencies)
pip install -e .

# Install slash commands
scholarsquill install
```

### Method 3: Manual Installation

If you prefer manual setup:

1. **Copy Command Files**:
   ```bash
   mkdir -p ~/.claude/commands
   cp .claude/commands/note.md ~/.claude/commands/
   cp .claude/commands/citemap.md ~/.claude/commands/
   cp .claude/commands/codelang.md ~/.claude/commands/
   ```

2. **Configure MCP Server**:
   Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):
   ```json
   {
     "mcpServers": {
       "scholarsquill": {
         "command": "/usr/local/bin/python3",
         "args": ["-m", "src.legacy_mcp_server.server"],
         "cwd": "/path/to/scholarsquill",
         "env": {
           "PYTHONPATH": "/path/to/scholarsquill"
         }
       }
     }
   }
   ```

3. **Restart Claude Code**

## Verify Installation

```bash
# Check installation status
./scholarsquill check
```

You should see:
- ✓ Commands directory found
- ✓ /note installed
- ✓ /citemap installed
- ✓ /codelang installed
- ✓ MCP server configured

## Using ScholarsQuill Commands

After restarting Claude Code, three new slash commands will be available:

### /note - Literature Note Generation

```
/note paper.pdf
/note paper.pdf --focus research --depth deep
/note papers/ --batch
```

**Arguments**:
- `target` (required): PDF file or directory path
- `--focus`: Analysis focus - research, theory, review, method, balanced (default: balanced)
- `--depth`: Analysis depth - quick, standard, deep (default: standard)
- `--batch`: Enable batch processing for directories
- `--output`: Output directory (default: literature-notes/)

**Output**: `[citekey].md` (e.g., `smith2020protein.md`)

### /citemap - Citation Network Analysis

```
/citemap paper.pdf
/citemap papers/ --batch --keyword neuroscience
```

**Arguments**:
- `target` (required): PDF file or directory path
- `--batch`: Enable batch processing with cross-reference analysis
- `--keyword`: Custom keyword for batch filename
- `--output`: Output directory (default: citemap-analysis/)

**Output**:
- `[citekey]_citemap.md` - Citation analysis
- `[citekey]_citemap_network.html` - Interactive network visualization

### /codelang - Discourse Pattern Analysis

```
/codelang paper.pdf
/codelang paper.pdf --focus terminology --field biology
/codelang paper.pdf --section introduction --depth deep
```

**Arguments**:
- `target` (required): PDF file or directory path
- `--field`: Academic field - auto-detect, physics, cs, biology, etc. (default: auto-detect)
- `--focus`: Analysis focus - discourse, architecture, terminology, rhetoric, sections, functions, summary (default: discourse)
- `--section`: Section filter - all, introduction, methods, results, discussion (default: all)
- `--depth`: Analysis depth - quick, standard, deep (default: standard)
- `--batch`: Enable batch processing
- `--keyword`: Custom keyword for batch filename
- `--output`: Output directory (default: codelang-analysis/)

**Output**: `[citekey]_codelang.md` (e.g., `smith2020protein_codelang.md`)

## Troubleshooting

### Commands Not Appearing in Claude Code

1. **Verify Installation**:
   ```bash
   ./scholarsquill check
   ```

2. **Check MCP Server Configuration**:
   - Location: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Must have `scholarsquill` entry in `mcpServers`
   - Must use `src.legacy_mcp_server.server` (not `src.server`)

3. **Restart Claude Code Completely**:
   - Quit Claude Code entirely
   - Relaunch the application
   - Wait 10-15 seconds for MCP server to initialize

4. **Check Logs**:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp.log
   ```

### MCP Server Not Working

```bash
# Test MCP server manually
cd /path/to/scholarsquill
python3 -m src.legacy_mcp_server.server
```

If you see errors, check:
- Python version (must be 3.8+)
- Required packages installed (PyPDF2, pdfplumber, jinja2, networkx)
- PYTHONPATH environment variable set correctly

### Permission Errors

```bash
# Make sure command files are readable
chmod 644 ~/.claude/commands/*.md

# Make CLI wrapper executable
chmod +x scholarsquill
```

## Uninstallation

To remove ScholarsQuill slash commands:

```bash
./scholarsquill uninstall
```

This removes command files from `~/.claude/commands/` but leaves the MCP server configuration intact.

To completely remove ScholarsQuill:
1. Run `./scholarsquill uninstall`
2. Remove ScholarsQuill from Claude Desktop config manually
3. Delete the scholarsquill directory

## Getting Help

```bash
# CLI help
./scholarsquill --help

# Command-specific help
./scholarsquill install --help
./scholarsquill check --help

# In Claude Code
/note --help
/citemap --help
/codelang --help
```

## Support

- Issues: https://github.com/scholarsquill/scholarsquill/issues
- Documentation: See README.md and CURRENT_ARCHITECTURE.md
