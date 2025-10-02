# ScholarsQuill Troubleshooting Guide

**Based on real user troubleshooting experiences**

## Critical Issue: Slash Commands Not Appearing

This is the most common issue when setting up ScholarsQuill with Claude Desktop.

### 1. Verify MCP Server Configuration

**File to check**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Correct configuration**:
```json
{
  "mcpServers": {
    "scholarsquill": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "src.legacy_mcp_server.server"],
      "cwd": "/Users/username/scholarsquill/scholarsquill",
      "env": {
        "PYTHONPATH": "/Users/username/scholarsquill/scholarsquill"
      }
    }
  }
}
```

**Key points**:
- Use `src.legacy_mcp_server.server` (NOT `src.server`)
- Ensure `cwd` points to your actual ScholarsQuill directory
- Use absolute paths everywhere
- Add PYTHONPATH environment variable

### 2. Check Server Status

Run these commands to verify:

```bash
# Check if the server file exists
ls -la /Users/username/scholarsquill/scholarsquill/src/legacy_mcp_server/server.py

# Verify Python path matches your config
which python3

# Check if dependencies are installed
pip list | grep -E "fastmcp|PyMuPDF|jinja2|networkx|plotly"
```

### 3. Verify Available MCP Servers

In Claude Desktop, check what MCP servers are loaded:
- Look for "scholarsquill" in the available MCP servers list
- If missing, the configuration or restart step failed

### 4. Required Dependencies

Ensure these are installed:
```bash
pip install fastmcp PyMuPDF pathlib typing jinja2 networkx plotly
```

### 5. Restart Requirement

Always restart Claude Desktop completely after changing the configuration file:
- Quit Claude Desktop entirely (Command+Q on Mac)
- Reopen Claude Desktop
- Wait 30-60 seconds for MCP servers to initialize

### 6. Test Commands

The three commands should be available as slash commands:
- `/note` - Literature notes
- `/citemap` - Citation networks  
- `/codelang` - Code-language analysis

## Common Mistakes to Avoid

### 1. Wrong Server Path
**Wrong**: `"args": ["-m", "src.server"]`
**Correct**: `"args": ["-m", "src.legacy_mcp_server.server"]`

### 2. Forgetting to Restart
Configuration changes require a **full restart** of Claude Desktop, not just closing the window.

### 3. Relative Paths
**Wrong**: `"cwd": "./scholarsquill"`
**Correct**: `"cwd": "/Users/username/scholarsquill/scholarsquill"`

### 4. Missing Dependencies
ScholarsQuill requires specific Python packages. Install them all before testing.

### 5. Wrong Python Version
Ensure the Python path in config matches your installed Python:
```bash
which python3
# Should match the "command" in your MCP config
```

## Quick Fix Commands

### Check Configuration
```bash
# View current configuration
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check if configuration file exists
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Verify Installation
```bash
# Check Python path matches config
which python3

# Verify server file exists (replace path with yours)
ls -la /Users/username/scholarsquill/scholarsquill/src/legacy_mcp_server/server.py

# Check dependencies
pip list | grep -E "fastmcp|PyMuPDF|jinja2|networkx|plotly"
```

### Test Setup
```bash
# Try running the server directly (for debugging)
cd /Users/username/scholarsquill/scholarsquill
python3 -m src.legacy_mcp_server.server --version
```

## Step-by-Step Resolution

If commands still don't appear, follow this exact sequence:

1. **Fix Configuration**:
   ```bash
   # Edit the config file
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
   
   Ensure it matches the correct format above.

2. **Verify Server File**:
   ```bash
   # Check the server file exists
   ls -la /path/to/your/scholarsquill/src/legacy_mcp_server/server.py
   ```

3. **Install Dependencies**:
   ```bash
   # Install all required packages
   pip install fastmcp PyMuPDF pathlib typing jinja2 networkx plotly
   ```

4. **Complete Restart**:
   - Quit Claude Desktop completely (Command+Q)
   - Wait 5 seconds
   - Reopen Claude Desktop
   - Wait 30 seconds for initialization

5. **Test Commands**:
   - Type `/` in Claude Desktop
   - Look for `note`, `citemap`, `codelang` commands
   - If they appear, configuration is successful!

## Additional Issues

### PDF Processing Errors
- Ensure PDFs contain extractable text (not scanned images)
- Check file permissions and accessibility
- Verify PDF file is not corrupted or password-protected

### Empty or Incorrect Output
- Try with different PDF files
- Check if PDF has sufficient content for analysis
- Verify focus and depth parameters are appropriate

### Python Environment Issues
- Make sure you're using the correct Python environment
- If using virtual environments, ensure packages are installed in the right one
- Consider using system Python instead of virtual environments for MCP

## Getting Help

If you're still having issues:

1. **Check Claude Desktop logs** for MCP server errors
2. **Verify all file paths** are absolute and correct
3. **Test with sample PDFs** in the `test_project/input/` directory
4. **Try a minimal configuration** first, then add complexity

## Success Indicators

You know it's working when:
- Slash commands `/note`, `/citemap`, `/codelang` appear in Claude Desktop
- Running `/note test.pdf` generates a literature note
- Output files use citekey format (e.g., `smith2020protein.md`)
- PDF links appear as `[[filename.pdf]]` in generated notes

---

**The key lesson**: Always check the server path in your MCP configuration first (`src.legacy_mcp_server.server`), then restart Claude Desktop completely.