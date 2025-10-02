# Legacy MCP Server Files

These files were moved here during the transformation to standalone AI agent architecture.

## Files Moved (Not Needed for Standalone AI Agent)

### MCP Server Infrastructure
- `server.py` - FastMCP server implementation
- `server_core.py` - MCP server core logic
- `mcp_mock.py` - MCP testing mock
- `command_parser.py` - MCP command parsing
- `config.py` - MCP server configuration  
- `main.py` - MCP server entry point

### External Tool Dependencies
- `pdf_processor.py` - External PDF library usage
- `batch_processor.py` - Complex batch processing logic
- `file_writer.py` - File writing utilities
- `utils.py` - Utility functions for MCP
- `interfaces.py` - Interface definitions for MCP
- `exceptions.py` - Custom exception handling

### Complex Processing Logic
- `content_analyzer.py` - Complex content analysis
- `note_generator.py` - Template-based note generation
- `claude_literature_generator.py` - Old Claude integration
- `llm_integration.py` - LLM integration layer

## Why Moved

ScholarsQuill was transformed from an MCP server to a pure AI agent that:
- Uses AI intelligence instead of external tools
- Works through command pattern recognition
- Requires zero installation or dependencies
- Processes PDFs through AI understanding

These files represented the old architecture and are preserved here for reference but not used in the new standalone approach.

## New Architecture

The new ScholarsQuill uses only:
- Template files for AI guidance
- Analysis patterns for behavioral specification
- Pure AI intelligence for all processing
- Command pattern recognition for activation

See: `STANDALONE_ARCHITECTURE.md` for details.