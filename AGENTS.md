# AGENTS.md

## About ScholarsQuill

**ScholarsQuill** is an advanced Academic PDF Processing MCP (Model Context Protocol) server that transforms academic research workflows. It automatically generates structured literature notes, interactive citation networks, and code-language analysis from academic PDFs, making research more efficient and insightful.

ScholarsQuill integrates with MCP-compatible AI agents like Claude Code through the Model Context Protocol, providing seamless access to academic PDF processing tools through slash commands.

The toolkit supports multiple AI coding assistants with MCP capabilities, allowing researchers to use their preferred tools while maintaining consistent academic PDF processing workflows.

---

## General Practices

- All MCP tool descriptions must include the three core tools: `sq_note`, `sq_citemap`, and `sq_codelang`.
- MCP server configurations must maintain compatibility across supported AI agents.
- Output filenames follow citekey format (author-year-keyword) for academic consistency.

## Adding New Agent Support

This section explains how to add support for new AI agents/assistants to ScholarsQuill. Use this guide as a reference when integrating new MCP-compatible AI tools into academic research workflows.

### Overview

ScholarsQuill supports multiple AI agents through MCP server configuration. Each agent has its own conventions for:

- **MCP Server Configuration** (JSON configuration files)
- **Installation Methods** (CLI tools, desktop applications, etc.)
- **Tool Invocation Patterns** (`/note`, `/citemap`, `/codelang` slash commands)
- **Project Directory Integration** (working directory setup)

### Current Supported Agents

| Agent | Type | MCP Support | CLI Tool | Description |
|-------|------|-------------|----------|-------------|
| **Claude Code** | CLI Tool | Full MCP | `claude` | Anthropic's Claude with native MCP support |
| **Claude Desktop** | Desktop App | Full MCP | N/A (GUI-based) | Anthropic's Claude with native MCP support |
| **Custom MCP Client** | Various | Full MCP | Varies | Any MCP-compatible AI assistant |

### Step-by-Step Integration Guide

Follow these steps to add a new agent (using a hypothetical "ResearchAI" as an example):

#### 1. Update MCP Server Configuration

Create agent-specific configuration for the ScholarsQuill MCP server:

```json
{
  "mcpServers": {
    "scholarsquill": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/scholarsquill/scholarsquill"
    }
  }
}
```

#### 2. Create Agent-Specific Setup Guide

Create setup documentation for the new agent:

```markdown
# ScholarsQuill MCP Server Setup

## ResearchAI Integration

1. **Add to ResearchAI config** (`~/.researchai/config.json`):
   ```json
   {
     "mcpServers": {
       "scholarsquill": {
         "command": "/usr/local/bin/python3",
         "args": ["-m", "src.server"],
         "cwd": "/path/to/scholarsquill/scholarsquill"
       }
     }
   }
   ```

2. **Restart ResearchAI**

3. **Test with commands**:
   - `/note input/paper.pdf` - Generate literature note
   - `/citemap input/paper.pdf` - Create citation map with HTML network
   - `/codelang input/paper.pdf` - Generate code-language analysis

## Available Tools

- **sq_note**: Process academic PDF into structured literature note
- **sq_citemap**: Generate citation network analysis with interactive HTML visualization
- **sq_codelang**: Generate structured code-language analysis for computational papers

## Usage Examples

```bash
# In ResearchAI:
/note input/research_paper.pdf --focus research
/citemap input/research_paper.pdf --batch
/codelang input/research_paper.pdf --focus terminology
```
```

#### 3. Update Documentation

Update all documentation to include the new agent:

- MCP configuration examples
- Setup instructions
- Tool usage patterns
- Troubleshooting guides

#### 4. Update README Documentation

Update the **Supported AI Agents** section in `README.md` to include the new agent:

```markdown
| Agent                                                     | Support | MCP Integration |
|-----------------------------------------------------------|---------| ----------------|
| [Claude Code](https://www.anthropic.com/claude-code)     | ✅       | Full MCP support |
| [Claude Desktop](https://www.anthropic.com/claude)       | ✅       | Full MCP support |
| [ResearchAI](https://researchai.example.com)            | ✅       | Full MCP support |
| Custom MCP Client                                        | ✅       | Compatible |
```

#### 5. Update Quick Start Guide

Modify `QUICK_START.md` to include the new agent in examples:

```markdown
Choose your AI agent:
- **claude-code** (recommended): Claude Code with MCP support
- **claude-desktop**: Claude Desktop with MCP support
- **researchai**: ResearchAI with full MCP integration
- **custom**: Other MCP-compatible AI assistant
```

#### 6. Test Integration

Test the new agent integration:

```bash
# Test MCP server connection
# Test all three core commands
/note test.pdf --focus research
/citemap test.pdf --batch
/codelang test.pdf --focus terminology

# Verify output format
# Check citekey-based filenames
# Confirm Obsidian PDF linking
```

## Agent Categories

### Desktop Applications
GUI-based applications with native MCP support:
- **Claude Desktop**: Built-in MCP server integration
- **ResearchAI Desktop**: (Hypothetical) Academic-focused AI with MCP

### CLI-Based Agents
Require a command-line tool to be installed:
- **Gemini CLI**: `gemini` CLI with planned MCP support
- **Custom CLI Tools**: Various research-specific CLI tools

### MCP-Compatible Services
Web services or APIs that support the MCP protocol:
- **Custom MCP Client**: Any service implementing MCP server protocol
- **Research Platform APIs**: Academic platform integrations

## MCP Configuration Patterns

### Desktop Application Config
Used by: Claude Desktop, ResearchAI Desktop

```json
{
  "mcpServers": {
    "scholarsquill": {
      "command": "python",
      "args": ["-m", "scholarsquill.server"],
      "cwd": "/path/to/project"
    }
  }
}
```

### CLI Tool Integration
Used by: Gemini CLI, Custom CLI tools

```bash
# Direct server execution
python -m scholarsquill.server --direct input/paper.pdf

# Or via CLI wrapper
gemini mcp connect scholarsquill
```

### Custom Service Integration
Used by: Custom MCP clients, API services

```python
# MCP client connection
client = MCPClient("python", ["-m", "scholarsquill.server"])
result = await client.call_tool("sq_note", {"file_path": "input/paper.pdf"})
```

## Tool Configuration Standards

All agents must support the three core Scholar's Quill tools:

### sq_note
- **Purpose**: Generate structured literature notes from academic PDFs
- **Input**: PDF file path
- **Output**: `[citekey].md` (e.g., `smith2020protein.md`)
- **Templates**: Research, theory, method, review, balanced focus areas
- **Features**: Citekey-based naming, Obsidian PDF linking

### sq_citemap
- **Purpose**: Create citation network analysis with interactive visualization
- **Input**: PDF file path
- **Output**: 
  - `[citekey]_citemap.md` - Citation context analysis
  - `[citekey]_citemap_network.html` - Interactive network
- **Features**: Reference relationship mapping, network topology

### sq_codelang
- **Purpose**: Generate structured code-language analysis for computational papers
- **Input**: PDF file path  
- **Output**: `[citekey]_codelang.md`
- **Focus**: Academic discourse patterns, terminology analysis, rhetorical structure

## Directory Structure Conventions

ScholarsQuill projects follow a consistent structure:

```
scholarsquill/
├── src/
│   ├── server.py            # Main MCP server
│   ├── metadata_extractor.py
│   └── citemap_processor.py
├── templates/               # Analysis templates
├── test_project/
│   ├── input/               # PDF files for processing
│   └── output/              # Generated notes and visualizations
└── README.md               # Project documentation
```

## Testing New Agent Integration

1. **Configuration Test**: Verify correct MCP server configuration
2. **Connection Test**: Ensure MCP server loads in agent
3. **Tool Test**: Ensure all three tools (sq_note, sq_citemap, sq_codelang) work
4. **Output Test**: Validate citekey-based filenames and Obsidian PDF linking
5. **Command Test**: Confirm slash commands (/note, /citemap, /codelang) work

## Common Pitfalls

1. **Missing Tool Descriptions**: Always include all three core tools in documentation
2. **Incorrect MCP Configuration**: Ensure server command and arguments are correct
3. **Path Issues**: Use absolute paths for project working directory
4. **Version Compatibility**: Check MCP protocol version compatibility
5. **Help Text Inconsistency**: Update all user-facing text consistently

## Agent-Specific Requirements

### Claude Code
- **Installation**: Download from Anthropic website
- **Configuration**: Add MCP server to Claude Code configuration
- **Features**: Full MCP support, CLI interface, slash commands

### Claude Desktop
- **Installation**: Download from Anthropic website
- **Configuration**: `claude_desktop_config.json` in system config directory
- **Features**: Full MCP support, rich UI, conversation context

### Custom MCP Client
- **Installation**: Varies by implementation
- **Configuration**: MCP server connection parameters
- **Features**: Full protocol compatibility required

## Future Considerations

When adding new agents:
- Ensure MCP protocol compatibility (version 1.0.0+)
- Consider agent-specific academic research features
- Document any special requirements or limitations
- Test with various PDF types (computational, theoretical, experimental)
- Update this guide with lessons learned

## Academic Research Workflow Integration

New agents should support the complete Scholar's Quill workflow:

1. **PDF Ingestion**: Handle academic PDF formats reliably
2. **Literature Analysis**: Generate structured academic notes
3. **Citation Mapping**: Create and visualize citation networks
4. **Code Analysis**: Process computational/methodological content
5. **Export Capabilities**: Support multiple output formats

---

*This documentation should be updated whenever new agents are added to maintain accuracy and completeness. For questions about agent integration, refer to the MCP specification at https://modelcontextprotocol.io/*