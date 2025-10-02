# ScholarsQuill Quick Start Guide

**Transform your academic research workflow with automated PDF analysis**

## Installation (5 minutes)

### Step 1: Get ScholarsQuill

```bash
# Clone the repository
git clone https://github.com/scholarsquill/scholarsquill.git
cd scholarsquill
```

### Step 2: Automated Installation

```bash
# Run the automated installer
./scholarsquill install
```

This command will:
- ✓ Install all required Python dependencies automatically
- ✓ Copy slash command files to ~/.claude/commands/
- ✓ Verify MCP server configuration
- ✓ Display installation status

### Step 3: Restart Claude Code

Completely quit and restart Claude Code to load the commands.

### Step 4: Verify Installation

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

After restart, three powerful slash commands are available in Claude Code:

### 1. Generate Literature Notes (`/note`)

```bash
/note paper.pdf
/note paper.pdf --focus research --depth deep
/note papers/ --batch
```

**Output**: `[citekey].md` (e.g., `smith2020protein.md`)

**Arguments**:
- `target` - PDF file or directory path
- `--focus` - Analysis focus: research, theory, method, review, balanced (default: balanced)
- `--depth` - Analysis depth: quick, standard, deep (default: standard)
- `--batch` - Enable batch processing for directories
- `--output` - Output directory (default: literature-notes/)

**Features**:
- Intelligent AI analysis of methodology, findings, implications
- Focus-specific templates for different paper types
- Citekey-based naming (authorYEARkeyword format)
- Obsidian-compatible PDF links `[[source.pdf]]`
- Structured markdown output ready for research workflows

### 2. Create Citation Networks (`/citemap`)

```bash
/citemap paper.pdf
/citemap papers/ --batch --keyword neuroscience
```

**Output**:
- `[citekey]_citemap.md` - Citation context analysis
- `[citekey]_citemap_network.html` - Interactive visualization

**Arguments**:
- `target` - PDF file or directory path
- `--batch` - Enable cross-reference analysis
- `--keyword` - Custom batch filename keyword
- `--output` - Output directory (default: citemap-analysis/)

**Features**:
- Citation context extraction with purposes
- Reference relationship mapping
- Interactive HTML network visualization
- Intellectual lineage tracking
- Cross-paper connection analysis in batch mode

### 3. Analyze Discourse Patterns (`/codelang`)

```bash
/codelang paper.pdf
/codelang paper.pdf --focus terminology --field biology
/codelang paper.pdf --section introduction --depth deep
```

**Output**: `[citekey]_codelang.md`

**Arguments**:
- `target` - PDF file or directory path
- `--field` - Academic field: auto-detect, physics, cs, biology, etc. (default: auto-detect)
- `--focus` - Analysis type: discourse, architecture, terminology, rhetoric, sections, functions, summary (default: discourse)
- `--section` - Section filter: all, introduction, methods, results, discussion (default: all)
- `--depth` - Analysis depth: quick, standard, deep (default: standard)
- `--batch` - Process multiple files
- `--keyword` - Custom batch filename
- `--output` - Output directory (default: codelang-analysis/)

**Features**:
- Field-specific terminology extraction
- Argument structure and discourse architecture mapping
- Rhetorical device identification
- Academic writing convention analysis
- Section-by-section functional analysis

## Complete Workflow Example

```bash
# Step 1: Install ScholarsQuill (one-time setup)
git clone https://github.com/scholarsquill/scholarsquill.git
cd scholarsquill
./scholarsquill install
# Restart Claude Code

# Step 2: In Claude Code, process your PDFs
/note papers/protein_folding.pdf --focus research --depth deep
# → Output: literature-notes/smith2020protein.md

/citemap papers/protein_folding.pdf
# → Output: citemap-analysis/smith2020protein_citemap.md
#          citemap-analysis/smith2020protein_citemap_network.html

/codelang papers/protein_folding.pdf --focus terminology --field biology
# → Output: codelang-analysis/smith2020protein_codelang.md

# Step 3: View interactive citation network
open citemap-analysis/smith2020protein_citemap_network.html
```

## Output File Structure

### Literature Notes
**Filename**: `[citekey].md` (e.g., `smith2020protein.md`)

**Content**:
- Paper metadata (author, year, title, DOI, journal)
- PDF link: `[[source.pdf]]` for Obsidian
- Focus-specific sections (methodology, findings, implications, etc.)
- Critical evaluation and research implications
- Cross-references to related work

### Citation Maps
**Markdown**: `[citekey]_citemap.md`
- Citation contexts with purposes
- Reference list with metadata
- Cross-paper relationships
- Network topology analysis

**HTML**: `[citekey]_citemap_network.html`
- Interactive network visualization
- Clickable nodes and edges
- Zoom and pan capabilities
- Citation context tooltips

### Discourse Analysis
**Markdown**: `[citekey]_codelang.md`
- Terminology analysis
- Discourse architecture
- Rhetorical patterns
- Academic writing conventions
- Field-specific language insights

## Focus Options Reference

### Literature Notes (`/note`)

| Focus | Best For | Key Sections |
|-------|----------|--------------|
| research | Experimental papers | Methodology, findings, experimental design |
| theory | Theoretical works | Frameworks, mathematical models, conceptual foundations |
| method | Technical papers | Procedures, implementation, validation |
| review | Literature reviews | Synthesis, gaps, research directions |
| balanced | General papers | Comprehensive coverage of all aspects |

### Discourse Analysis (`/codelang`)

| Focus | Analyzes | Output |
|-------|----------|--------|
| discourse | Overall argument structure | Discourse patterns, claim-evidence structure |
| architecture | Information organization | Section purposes, narrative flow |
| terminology | Field-specific language | Key terms, concepts, definitions |
| rhetoric | Persuasive strategies | Rhetorical devices, hedging, claiming |
| sections | Section-by-section analysis | Functional analysis of each section |
| functions | Linguistic functions | Hedging, citing, claiming, contrasting |
| summary | High-level overview | Executive summary of discourse |

## Citekey Format

ScholarsQuill generates academic citekeys: `authorYEARkeyword`

**Examples**:
- `smith2020protein` - Smith et al. (2020), "Protein Folding Dynamics"
- `jones2019machine` - Jones & Brown (2019), "Machine Learning Methods"
- `garcia2021molecular` - García et al. (2021), "Molecular Simulation"

## Batch Processing

Process multiple papers efficiently:

```bash
# Literature notes for entire directory
/note papers_directory/ --batch --focus research

# Citation network across multiple papers
/citemap papers_directory/ --batch --keyword neuroscience

# Discourse analysis of multiple papers
/codelang papers_directory/ --batch --focus terminology --field biology
```

**Benefits**:
- Cross-reference analysis
- Consistent naming and organization
- Batch-specific output filenames
- Efficient processing of paper collections

## Obsidian Integration

All outputs are Obsidian-compatible:
- PDF links: `[[filename.pdf]]`
- Citekey-based naming for cross-referencing
- Markdown metadata format
- Ready for Obsidian vault integration

**Setup**:
1. Create Obsidian vault
2. Configure output directories to vault location
3. Use `/note` with `--output /path/to/vault/Literature/`
4. PDF links automatically work in Obsidian

## Troubleshooting

### Commands Not Appearing

**Solution**:
```bash
# 1. Check installation
./scholarsquill check

# 2. Verify commands installed
ls -la ~/.claude/commands/ | grep -E "(note|citemap|codelang)"

# 3. Check MCP configuration
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | grep scholarsquill

# 4. Restart Claude Code completely (quit and relaunch)
```

### MCP Server Issues

**Common Problem**: Wrong server path

**Solution**: Verify configuration uses `src.legacy_mcp_server.server`:

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

### Dependency Issues

```bash
# Reinstall dependencies
pip install typer rich PyPDF2 pdfplumber jinja2 networkx plotly

# Verify installation
python3 -c "import typer, rich, PyPDF2, pdfplumber, jinja2, networkx, plotly; print('All dependencies OK')"
```

### PDF Processing Errors

**Requirements**:
- PDFs must contain extractable text (not scanned images)
- File must be readable and not password-protected
- Sufficient content for analysis (not cover pages only)

**See [INSTALLATION.md](INSTALLATION.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.**

## CLI Management

```bash
# Check installation status
./scholarsquill check

# Reinstall commands (with --force to overwrite)
./scholarsquill install --force

# Remove commands
./scholarsquill uninstall

# Show version
./scholarsquill version
```

## Advanced Tips

### Custom Output Directories

```bash
/note paper.pdf --output ~/Research/LiteratureNotes/
/citemap paper.pdf --output ~/Research/CitationMaps/
/codelang paper.pdf --output ~/Research/DiscourseAnalysis/
```

### Combining Focus and Depth

```bash
# Deep research analysis
/note paper.pdf --focus research --depth deep

# Quick theoretical overview
/note paper.pdf --focus theory --depth quick

# Standard methodological analysis
/note paper.pdf --focus method --depth standard
```

### Field-Specific Discourse Analysis

```bash
/codelang physics_paper.pdf --field physics --focus terminology
/codelang cs_paper.pdf --field computer-science --focus architecture
/codelang bio_paper.pdf --field biology --focus rhetoric
```

### Section-Focused Analysis

```bash
# Analyze only introduction
/codelang paper.pdf --section introduction --focus rhetoric

# Methods section terminology
/codelang paper.pdf --section methods --focus terminology

# Results and discussion
/codelang paper.pdf --section results --focus functions
```

## Next Steps

1. **Process your first paper**: `/note yourpaper.pdf`
2. **Explore citation networks**: `/citemap yourpaper.pdf`
3. **Analyze discourse patterns**: `/codelang yourpaper.pdf --focus terminology`
4. **Try batch processing**: `/note papers_directory/ --batch`
5. **Integrate with Obsidian**: Configure output to your vault
6. **Experiment with focus options**: Find what works for your research
7. **Share your workflow**: Help improve ScholarsQuill

## Getting Help

```bash
# CLI help
./scholarsquill --help

# In Claude Code
/note --help
/citemap --help
/codelang --help
```

**Documentation**:
- [INSTALLATION.md](INSTALLATION.md) - Complete installation guide
- [README.md](README.md) - Project overview and features
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [CURRENT_ARCHITECTURE.md](CURRENT_ARCHITECTURE.md) - Technical details

**Support**:
- Issues: https://github.com/scholarsquill/scholarsquill/issues
- Discussions: Share workflows and ask questions

---

**Ready to transform your research workflow?**

```bash
git clone https://github.com/scholarsquill/scholarsquill.git
cd scholarsquill
./scholarsquill install
```

*Start with `/note yourpaper.pdf` and experience AI-powered academic PDF analysis!*
