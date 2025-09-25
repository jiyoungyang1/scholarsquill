# ScholarSquill Kiro

⚠️ **Project Status: In Development** ⚠️

This project is currently under active development. The core functionality is operational, but significant improvements are planned for metadata extraction and citation mapping capabilities.

An intelligent Model Context Protocol (MCP) server for automated processing of scientific PDF papers into structured markdown literature notes, comprehensive mini-reviews, and discourse pattern analysis.

## Overview

ScholarSquill transforms academic research workflows by automatically converting PDF papers into well-structured literature notes and analyzing academic discourse patterns. The system provides intelligent content analysis, customizable template-based generation, sophisticated mini-review creation, and code language extraction capabilities for academic researchers, students, and professionals.

## Key Features

### Core Functionality
- **Literature Note Generation**: Convert PDF papers into structured markdown literature notes
- **Discourse Pattern Analysis**: Extract academic "code language" and argument structures
- **Citation Context Mapping**: Analyze citation contexts and build reference networks showing intellectual lineage
- **Intelligent PDF Processing**: Advanced text extraction and metadata analysis from scientific papers
- **Content Classification**: Automatic identification of paper types (research, theory, review, methodology)
- **Template-Based Generation**: Customizable markdown templates for different analysis types
- **Mini-Review Creation**: Synthesize multiple papers into comprehensive topical reviews
- **Batch Processing**: Process multiple PDFs simultaneously with parallel execution
- **MCP Integration**: Full Model Context Protocol compliance for seamless AI assistant integration

### Analysis Templates

**Literature Notes**:
- **Research Focus**: Emphasis on methodology, results, and implications
- **Theory Focus**: Theoretical frameworks, models, and conceptual analysis
- **Review Focus**: Literature synthesis and comparative analysis
- **Method Focus**: Detailed methodology and technical implementation
- **Balanced**: General-purpose template for comprehensive coverage

**Code Language Analysis**:
- **Discourse**: Complete rhetorical and linguistic analysis
- **Architecture**: Argument structure and logical flow patterns
- **Terminology**: Domain-specific vocabulary and technical expressions
- **Rhetoric**: Persuasion strategies and authority positioning
- **Sections**: Section-specific language patterns
- **Functions**: Discovered linguistic functions and patterns
- **Summary**: Key insights and writing conventions

### Advanced Features
- **Discourse Pattern Extraction**: Identify academic argument structures and rhetoric
- **Field-Specific Analysis**: Context-aware analysis for different academic disciplines  
- **Focus Filtering**: Target specific aspects of discourse or literature analysis
- **Combined Batch Analysis**: Single output file analyzing patterns across multiple papers
- **Citekey Generation**: Automatic creation of standardized citation keys *(under improvement)*
- **Depth Control**: Configurable analysis depth (quick, standard, deep)
- **Quality Validation**: Content integrity checks and processing validation
- **Robust Error Handling**: Graceful handling of various PDF formats and edge cases
- **Interactive Citation Networks**: Generate interactive HTML visualizations of citation relationships
- **Reference Network Analysis**: Build comprehensive networks showing intellectual lineage between papers

## Installation

### Requirements
- Python 3.8 or higher
- Model Context Protocol (MCP) compatible AI assistant (Claude, etc.)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/scholarsquill/scholarsquill.git
cd scholarsquill

# Install dependencies
pip install -r requirements.txt

# Optional: Install development dependencies
pip install -r requirements-dev.txt
```

### Optional Extensions
```bash
# OCR capabilities for scanned PDFs
pip install "scholarsquill[ocr]"

# Advanced NLP features
pip install "scholarsquill[nlp-advanced]"
```

## Usage

### MCP Server Usage (Primary Interface)

The primary interface is through MCP commands when used with Claude or other MCP-compatible AI assistants. Three main tools are available:

- `/sq:note` - Literature note generation from PDF papers
- `/sq:codelang` - Discourse pattern and code language analysis
- `/sq:citemap` - Citation context mapping and reference network analysis

#### Literature Note Generation (/sq:note)
```bash
/sq:note paper.pdf                           # Quick analysis with defaults
/sq:note papers/ --batch                     # Batch process directory
/sq:note paper.pdf --focus theory            # Theoretical analysis focus
/sq:note paper.pdf --depth deep             # Deep analysis mode
```

#### Discourse Pattern Analysis (/sq:codelang)
```bash
/sq:codelang paper.pdf                       # Full discourse analysis
/sq:codelang paper.pdf --focus architecture  # Argument structure patterns
/sq:codelang paper.pdf --focus terminology   # Domain-specific language
/sq:codelang paper.pdf --focus rhetoric      # Persuasion and positioning
/sq:codelang papers/ --batch --keyword quantum --focus summary  # Combined analysis
```

#### Citation Context Mapping (/sq:citemap)
```bash
/sq:citemap paper.pdf                            # Single paper citation analysis
/sq:citemap papers/ --batch                      # Batch analysis with cross-references
/sq:citemap paper.pdf --output-dir citations/    # Custom output directory
/sq:citemap papers/ --batch --output-dir network/ # Cross-reference network analysis
```

#### Citekey-Based Targeting
Target papers by author-year-keyword pattern instead of file paths:
```bash
/sq:note yang2024multi                       # Single paper by citekey
/sq:note fukuda2014 --focus research         # Find and analyze Fukuda 2014 paper
/sq:note yang2024multi,smith2023data --batch # Multiple papers by citekeys
```

#### Mini-Review Generation
Create comprehensive topic-focused reviews from multiple papers:
```bash
/sq:note papers/ --minireview --topic "Kirkwood-Buff finite size correction" --focus theory
/sq:note ganguly2012,ploetz2010 --minireview --topic "Kirkwood-Buff theory"
```

#### Focus Areas and Options

**Literature Notes (/sq:note)**:
- **Focus**: `research`, `theory`, `review`, `method`, `balanced`
- **Depth**: `quick` (500-800 words), `standard` (700-1500 words), `deep` (1200-2800 words)

**Code Language Analysis (/sq:codelang)**:
- **Focus**: `discourse` (full), `architecture`, `terminology`, `rhetoric`, `sections`, `functions`, `summary`
- **Section Filter**: `all`, `introduction`, `methods`, `results`, `discussion`
- **Field**: `auto-detect`, `physics`, `cs`, `biology`, etc.
- **Keyword**: Custom keyword for batch analysis filenames

**Citation Context Mapping (/sq:citemap)** *(under active development)*:
- **Single File**: Creates detailed citation context map for individual papers
- **Batch Mode**: Analyzes cross-references, common sources, and intellectual lineage
- **Network Analysis**: Builds interactive reference network visualizations showing citation relationships
- **Interactive HTML**: Generates clickable network graphs with citing papers and cited references
- **Output**: `Citemap_[keyword]_[count].md` and `Citemap_[keyword]_[count]_network.html`

### Command Line Interface (Development)

For direct CLI usage during development:

#### Process Single PDF
```bash
# Basic processing with default settings
python -m src.main process paper.pdf

# Specify focus and depth
python -m src.main process paper.pdf --focus theory --depth deep --output output/

# Research-focused analysis
python -m src.main process methodology_paper.pdf --focus method --depth standard
```

#### Batch Processing
```bash
# Process entire directory
python -m src.main batch papers_directory/ --focus research --output literature_notes/

# Theory-focused batch processing
python -m src.main batch theoretical_papers/ --focus theory --depth deep
```

### MCP Server Mode

Run as an MCP server for integration with AI assistants:

```bash
# Start MCP server
python -m src.main server

# Server will communicate via stdio for MCP protocol
```

### Python API

```python
import asyncio
from src.main import ScholarsQuillKiroCLI

async def process_papers():
    cli = ScholarsQuillKiroCLI()
    await cli.initialize()
    
    # Process single file
    result = await cli.process_file(
        "paper.pdf",
        focus="research",
        depth="deep",
        verbose=True
    )
    
    # Process batch
    batch_result = await cli.process_batch(
        "papers_directory/",
        focus="theory",
        depth="standard"
    )
    
    # Create citation context map
    citemap_result = await cli.process_citemap(
        "paper.pdf",
        batch=False,
        verbose=True
    )
    
    # Batch citation analysis
    batch_citemap_result = await cli.process_citemap(
        "papers_directory/",
        batch=True,
        verbose=True
    )
    
    await cli.shutdown()

# Run processing
asyncio.run(process_papers())
```

### Mini-Review Generation

Create comprehensive reviews from multiple papers using template-based generation:

```python
from src.minireview_processor import MiniReviewProcessor
from src.models import ProcessingOptions, FocusType, DepthType

async def create_review():
    processor = MiniReviewProcessor()
    
    options = ProcessingOptions(
        topic="Machine Learning in Bioinformatics",
        focus=FocusType.RESEARCH,
        depth=DepthType.DEEP,
        minireview=True
    )
    
    result = await processor.create_minireview("papers_directory/", options)
    print(f"Mini-review created: {result['output_path']}")

asyncio.run(create_review())
```

### Code Language Analysis Examples

Analyze discourse patterns and academic "code language":

```python
# Single paper discourse analysis
/sq:codelang neural_networks_paper.pdf --focus architecture
# Output: Codelang_smith2023neural.md

# Field-specific terminology analysis
/sq:codelang quantum_paper.pdf --focus terminology --field physics
# Output: Codelang_yang2024quantum.md

# Batch analysis with custom keyword
/sq:codelang ml_papers/ --batch --focus rhetoric --keyword deeplearning
# Output: Codelang_deeplearning_rhetoric.md

# Section-specific analysis
/sq:codelang paper.pdf --focus sections --section_filter introduction
# Output: Codelang_garcia2022intro.md
```

#### Output File Naming

**Literature Notes**:
- Single: `[title]_literature_note.md`
- Batch: `[title]_literature_note.md` (one per paper)

**Code Language Analysis**:
- Single: `Codelang_[citekey].md`
- Batch: `Codelang_[keyword]_[focus].md` (combined analysis)

## Configuration

### Environment Variables

```bash
# Core settings
export SQ_OUTPUT_DIR="/path/to/output"
export SQ_TEMPLATES_DIR="/path/to/templates"
export SQ_LOG_LEVEL="INFO"

# Processing limits
export SQ_MAX_FILE_SIZE_MB="50"
export SQ_BATCH_SIZE_LIMIT="100"

# Advanced settings
export SQ_ENABLE_OCR="true"
export SQ_NLP_MODEL="en_core_web_sm"
```

### Configuration File

Create `config.yaml` for advanced configuration:

```yaml
server:
  output_dir: "output/"
  max_file_size_mb: 50
  batch_size_limit: 100
  log_level: "INFO"

processing:
  default_focus: "balanced"
  default_depth: "standard"
  enable_mermaid: true
  enable_citekey_generation: true

templates:
  directory: "templates/"
  custom_templates: []

nlp:
  model: "en_core_web_sm"
  enable_advanced_features: false
```

## Project Structure

```
scholarsquill/
├── src/                      # Core source code
│   ├── main.py              # CLI and MCP server entry point
│   ├── server.py            # MCP server implementation
│   ├── models.py            # Data models and types
│   ├── config.py            # Configuration management
│   ├── pdf_processor.py     # PDF text extraction
│   ├── content_analyzer.py  # Content analysis and classification
│   ├── note_generator.py    # Literature note generation
│   ├── minireview_processor.py # Mini-review creation
│   ├── citemap_processor.py # Citation context mapping
│   ├── template_engine.py   # Template processing
│   ├── batch_processor.py   # Batch processing logic
│   └── utils.py             # Utility functions
├── templates/               # Note generation templates
│   ├── research.md          # Research-focused template
│   ├── theory.md            # Theory-focused template
│   ├── review.md            # Review-focused template
│   ├── method.md            # Method-focused template
│   ├── minireview.md        # Mini-review template
│   ├── citemap.md           # Citation context mapping template
│   ├── citemap_batch.md     # Batch citation network template
│   └── balanced.md          # General-purpose template
├── tests/                   # Test suite
│   ├── examples/            # Example usage templates
│   └── test_*.py            # Unit and integration tests
├── docs/                    # Documentation
├── dev_artifacts/           # Development files (excluded from Git)
├── requirements.txt         # Core dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Testing and Validation

### Run Test Suite

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/ -m "unit"
pytest tests/ -m "integration"

# Test with coverage
pytest tests/ --cov=src --cov-report=html
```

### Manual Testing with MCP

```bash
# Start the MCP server
python -m src.main server

# Test with real PDFs (development artifacts)
# See dev_artifacts/ directory for sample papers and test scripts
```

## Integration Examples

### With Claude AI

Add to your Claude MCP configuration file:

```json
{
  "servers": {
    "scholarsquill": {
      "command": "python",
      "args": ["-m", "src.main", "server"],
      "cwd": "/path/to/scholarsquill"
    }
  }
}
```

Then use the `/sq:note` command in Claude to process academic papers.

### With Other AI Assistants

The MCP protocol ensures compatibility with various AI assistants that support Model Context Protocol.

## Advanced Usage

### Custom Templates

Create custom templates in the `templates/` directory:

```markdown
# Custom Template Example
# {{ paper.title }}

**Authors**: {{ paper.authors | join(', ') }}
**Year**: {{ paper.year }}
**Citekey**: {{ paper.citekey }}

## Custom Analysis
{{ analysis.custom_section }}

## Key Findings
{% for finding in analysis.key_findings %}
- {{ finding }}
{% endfor %}
```

### Batch Processing with Custom Options

```python
# Advanced batch processing
from src.batch_processor import BatchProcessor

processor = BatchProcessor()
results = await processor.process_directory(
    "papers/",
    options={
        "focus": "research",
        "depth": "deep",
        "parallel": True,
        "max_workers": 4,
        "output_format": "markdown",
        "include_diagrams": True
    }
)
```

## Performance and Scalability

### Optimization Features
- **Parallel Processing**: Multi-threaded PDF processing for batch operations
- **Memory Management**: Efficient handling of large PDF files
- **Caching**: Template and analysis result caching for improved performance
- **Streaming**: Progressive processing for large document collections

### Benchmarks
- **Single PDF**: 2-5 seconds average processing time
- **Batch Processing**: 50+ PDFs processed in parallel
- **Memory Usage**: <500MB for typical academic papers
- **File Size Support**: Up to 50MB PDF files (configurable)

## Troubleshooting

### Common Issues

**PDF Processing Errors**
```bash
# Check PDF integrity
python -m src.main analyze problematic_paper.pdf --verbose

# Enable debug logging
export SQ_LOG_LEVEL="DEBUG"
python -m src.main process paper.pdf
```

**Template Issues**
```bash
# Validate templates
python -m src.main templates --verbose

# Check template syntax
python -c "from src.template_engine import TemplateEngine; TemplateEngine().validate_templates()"
```

**MCP Server Issues**
```bash
# Test MCP server locally
python -m src.main server --verbose

# Check MCP protocol compliance
mcp-client test scholarsquill
```

## Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/
isort src/ tests/

# Run type checking
mypy src/
```

### Code Quality Standards

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks for quality assurance

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built on the Model Context Protocol (MCP) framework
- Utilizes advanced PDF processing libraries
- Inspired by academic research workflows and note-taking best practices
- Community contributions and feedback welcomed

## Development Status

### Currently Working
✅ **Core Literature Note Generation**: Fully functional PDF-to-markdown conversion  
✅ **Code Language Analysis**: Discourse pattern extraction and academic writing analysis  
✅ **Batch Processing**: Multi-file processing with parallel execution  
✅ **Template System**: Customizable output templates with Jinja2  
✅ **MCP Integration**: Full Model Context Protocol server implementation  
✅ **Citation Network Visualization**: Interactive HTML network graphs  

### Under Active Development
🚧 **Metadata Extraction**: Improving accuracy of author, title, and year extraction from PDFs  
🚧 **Citation Context Mapping**: Enhancing reference parsing and cross-paper citation analysis  
🚧 **Reference Matching**: Better algorithm for identifying shared citations across papers  
🚧 **Network Edge Detection**: Improved logic for connecting papers through shared references  

### Planned Improvements
📋 **AI-Enhanced Metadata**: Use LLM assistance for better metadata extraction from complex PDFs  
📋 **Advanced Citation Parsing**: Support for multiple citation formats and improved reference matching  
📋 **Enhanced Network Analysis**: Clustering, centrality measures, and citation flow analysis  
📋 **Error Recovery**: Better handling of malformed PDFs and incomplete metadata  
📋 **Performance Optimization**: Caching and parallel processing for large document collections  

## Support

For issues, feature requests, or questions:
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the wiki for detailed usage instructions
- **Discussions**: Community discussions and questions

---

**ScholarSquill Kiro** - Transforming academic research through intelligent document processing.

*Note: This is an active development project. Core features are functional, but metadata extraction and citation mapping capabilities are being enhanced. Contributions and feedback are welcome as we work toward a stable release.*