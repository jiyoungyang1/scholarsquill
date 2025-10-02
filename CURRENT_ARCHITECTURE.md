# ScholarsQuill Current Architecture

**MCP Server + AI Agent Integration for Academic PDF Processing**

## Overview

ScholarsQuill operates as a **Model Context Protocol (MCP) server** that provides PDF processing capabilities to **Claude Code AI Agent**. This hybrid architecture combines:

- **MCP Server**: Technical PDF processing, content extraction, template provision
- **AI Agent**: Intelligent content analysis, literature note generation, academic reasoning

## Architecture Diagram

```
Claude Code AI Agent
        ↕ (MCP Protocol)
ScholarsQuill MCP Server
        ↓
PDF Processing + Template System
        ↓
Intelligent Literature Notes
```

## Integration Flow

### 1. Command Execution
```
User types: /note paper.pdf --focus research
    ↓
Claude Desktop routes to ScholarsQuill MCP server
    ↓
MCP server processes command
```

### 2. MCP Server Processing
```
ScholarsQuill MCP Server:
- Extracts PDF content (src/content_extractor.py)
- Extracts metadata (src/metadata_extractor.py) 
- Loads appropriate template (src/template_loader.py)
- Provides analysis instructions
- Returns structured data to Claude AI
```

### 3. AI Agent Analysis
```
Claude Code AI Agent:
- Receives PDF content + template + instructions
- Applies intelligent analysis to content
- Generates comprehensive literature note
- Uses academic reasoning and domain knowledge
```

## Current Working Commands

### /note - Literature Note Generation
**MCP Tool**: `sq_note` → **Slash Command**: `/note`

**Usage**: `/note paper.pdf --focus research --depth standard`

**Process**:
1. MCP extracts PDF content and metadata
2. MCP provides focus-appropriate template
3. Claude AI analyzes content intelligently
4. Claude generates complete literature note

### /citemap - Citation Network Analysis  
**MCP Tool**: `sq_citemap` → **Slash Command**: `/citemap`

**Usage**: `/citemap paper.pdf --batch`

**Process**:
1. MCP extracts citations and reference contexts
2. MCP provides citation analysis template
3. Claude AI analyzes citation patterns
4. Claude generates citation network analysis

### /codelang - Discourse Pattern Analysis
**MCP Tool**: `sq_codelang` → **Slash Command**: `/codelang`

**Usage**: `/codelang paper.pdf --focus terminology --field biology`

**Process**:
1. MCP extracts text and identifies patterns
2. MCP provides discourse analysis template  
3. Claude AI analyzes academic language patterns
4. Claude generates discourse analysis

## File Structure

```
src/
├── content_extractor.py       # PDF content extraction
├── metadata_extractor.py      # PDF metadata extraction
├── citemap_processor.py       # Citation analysis
├── template_engine.py         # Template management
├── template_loader.py         # Template loading system
├── analysis_instructions.py   # AI guidance generation
├── models.py                  # Data structures
└── legacy_mcp_server/
    └── server.py              # MCP tool registration & FastMCP server
```

## Connection Point

**Claude Desktop Configuration**: `/Users/yyangg00/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "scholarsquill": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "src.legacy_mcp_server.server"],
      "cwd": "/Users/yyangg00/scholarsquill/scholarsquill"
    }
  }
}
```

This configuration:
1. Starts the ScholarsQuill MCP server on Claude Code startup
2. Registers MCP tools as slash commands
3. Enables AI agent to use ScholarsQuill capabilities

## MCP + AI Division of Labor

### MCP Server Responsibilities
- ✅ PDF text extraction using external libraries
- ✅ Metadata extraction and structuring
- ✅ Template loading and management
- ✅ Citation parsing and reference extraction
- ✅ File I/O operations
- ✅ Content preprocessing and organization

### AI Agent Responsibilities  
- ✅ Intelligent content analysis and comprehension
- ✅ Academic reasoning and domain knowledge application
- ✅ Literature note composition and writing
- ✅ Pattern recognition in academic discourse
- ✅ Synthesis and insight generation
- ✅ Template filling with meaningful content

## Key Features

### Focus Areas
- **research**: Methodology, findings, experimental design
- **theory**: Theoretical frameworks, mathematical models
- **method**: Experimental procedures, technical implementation
- **review**: Literature synthesis, research gaps
- **balanced**: General-purpose comprehensive analysis

### Depth Levels
- **quick**: High-level overview and key points
- **standard**: Comprehensive analysis with details
- **deep**: Exhaustive analysis with extensive detail

### Batch Processing
- Single file: Individual paper analysis
- Batch mode: Multiple papers with cross-analysis
- Directory processing: Automatic PDF discovery

## Template System

ScholarsQuill provides structured templates that guide Claude AI's analysis:

1. **Focus-specific templates**: Optimized for different paper types
2. **Embedded instructions**: HTML comments guide AI analysis
3. **Section structure**: Consistent academic note organization
4. **Analysis prompts**: Specific guidance for each section

## Output Generation

**Claude AI generates**:
- Complete literature notes in markdown format
- Citation network analyses with relationship mapping
- Discourse pattern analyses of academic language
- Cross-paper comparative analyses in batch mode

## Quality Standards

### MCP Server Standards
- Reliable PDF content extraction
- Accurate metadata parsing
- Consistent template provision
- Robust error handling

### AI Agent Standards  
- Academically rigorous analysis
- Evidence-based conclusions
- Proper citation handling
- Professional academic writing

## Advantages of MCP + AI Architecture

1. **Separation of Concerns**: MCP handles technical tasks, AI handles intelligence
2. **Reliability**: MCP ensures consistent PDF processing
3. **Flexibility**: AI adapts analysis to paper content and context
4. **Scalability**: MCP can process batches while AI maintains quality
5. **Maintainability**: Clear boundaries between technical and analytical components

## Current Status

✅ **Fully Operational**: All three commands working in Claude Code
✅ **MCP Integration**: Successfully registered and accessible
✅ **AI Processing**: Claude intelligently analyzes provided content
✅ **Template System**: Focus-specific templates guide analysis
✅ **Batch Capabilities**: Multiple file processing supported

---

*ScholarsQuill successfully combines MCP server reliability with AI agent intelligence for comprehensive academic PDF analysis.*