---
name: sq:note
description: "Generate structured literature notes from scientific PDF papers with intelligent analysis and customizable templates"
category: literature
complexity: advanced
mcp-servers: [scholarsquill]
personas: [academic, researcher]
---

# /sq:note - Scientific Literature Note Generation

## Overview

The `/sq:note` command transforms scientific PDF papers into structured markdown literature notes using intelligent content analysis, metadata extraction, and customizable templates. It provides comprehensive analysis capabilities with focus areas, depth controls, and batch processing for research workflows.

## Triggers
- Scientific paper analysis and note-taking requirements
- Literature review and research documentation needs  
- Academic writing and research synthesis workflows
- Batch processing of paper collections for systematic analysis
- Cross-paper thematic analysis and comparison studies

## Usage Syntax

```bash
/sq:note [target] [OPTIONS]
```

### Basic Usage
```bash
/sq:note paper.pdf                           # Quick analysis with defaults
/sq:note papers/ --batch                     # Batch process directory
/sq:note paper.pdf --focus theoretical       # Theoretical analysis focus
/sq:note paper.pdf --depth deep             # Deep analysis mode
```

### Citekey-Based Targeting (NEW)
```bash
/sq:note yang2024multi                       # Single paper by citekey
/sq:note fukuda2014 --focus research         # Find and analyze Fukuda 2014 paper
/sq:note yang2024multi,smith2023data --batch # Multiple papers by citekeys
```

### Advanced Usage
```bash
/sq:note paper.pdf --focus research --depth deep        # Empirical deep analysis
/sq:note papers/ --batch --output notes/                # Batch with output directory
/sq:note papers/ --minireview --topic "Kirkwood-Buff finite size correction" --focus theoretical
/sq:note ganguly2012,ploetz2010 --minireview --topic "Kirkwood-Buff theory" # Mini-review from citekeys
```

### Mini-Review Mode (NEW)
```bash
/sq:note papers/ --minireview --topic "protein folding mechanisms" --focus theoretical --depth deep
/sq:note papers/ --minireview --topic "CRISPR evolution" --focus review
```

## Command Options

### Core Parameters

| Option | Values | Default | Description | Mode |
|--------|--------|---------|-------------|------|
| `target` | `file.pdf` \| `directory/` \| `citekey` \| `citekey1,citekey2` | Required | PDF file, directory path, or citekey(s) | All |
| `--focus` | `research` \| `theory` \| `review` \| `method` \| `balanced` | `balanced` | Analysis focus area | All |
| `--depth` | `quick` \| `standard` \| `deep` | `standard` | Analysis depth level | All |
| `--batch` | flag | false | Process directory as individual notes | Batch |
| `--minireview` | flag | false | Create comprehensive topic mini-review | Mini-Review |
| `--topic` | `"topic description"` | Required with minireview | Topic focus for mini-review | Mini-Review |
| `--output-dir` | `directory/` | target directory | Output directory for notes | All |

### Processing Modes

| Mode | Command Pattern | Output | Use Case |
|------|----------------|--------|----------|
| **Single** | `/sq:note paper.pdf` | One literature note per PDF | Individual paper analysis |
| **Batch** | `/sq:note papers/ --batch` | Multiple individual notes | Many papers, separate notes |
| **Mini-Review** | `/sq:note papers/ --minireview --topic "topic"` | One comprehensive review (`Review_[topic].md`) | Topic-focused cross-paper analysis |
| **Citekey Single** | `/sq:note yang2024multi` | One literature note | Find and analyze specific paper by citekey |
| **Citekey Batch** | `/sq:note yang2024,smith2023 --batch` | Multiple individual notes | Multiple papers by citekeys |

## Citekey-Based Targeting

### Overview
The system supports targeting papers by **citekeys** instead of file paths. A citekey is a short identifier like `yang2024multi` that gets matched against PDF filenames to find the corresponding paper.

### Citekey Format
- **Pattern**: `lastname + year + firstwordoftitle`
- **Examples**: `fukuda2014thermodynamic`, `yang2024multi`, `ganguly2012kirkwood`
- **Components**: Three parts (lastname, year, first meaningful title word) with no separators

### How Citekey Matching Works

1. **Component Extraction**: `fukuda2014thermodynamic` → `['fukuda', '2014', 'thermodynamic']`
2. **PDF Search**: Searches common directories for PDF files containing these components
3. **Scoring**: Files are scored by how many components match the filename
4. **Selection**: Best matching file is selected (requires ≥2 component matches)

### Search Directories
The system automatically searches these directories for matching PDFs:
- Current working directory
- `./papers/`, `./pdfs/`, `./literature/`, `./docs/`
- `./tests/examples/papers/` (for testing)

### Citekey Usage Examples

#### Single Paper Analysis
```bash
/sq:note fukuda2014                          # Finds "Fukuda et al. - 2014 - Thermodynamic..."
/sq:note yang2024multi --focus research      # Research analysis of Yang 2024 paper
/sq:note ganguly2012 --depth deep           # Deep analysis of Ganguly 2012 paper
```

#### Multiple Papers (Batch Mode)
```bash
/sq:note fukuda2014,ganguly2012 --batch     # Individual notes for both papers
/sq:note yang2024,smith2023,jones2022 --batch --output ./notes/
```

#### Mini-Review Mode
```bash
/sq:note ganguly2012,ploetz2010 --minireview --topic "Kirkwood-Buff theory"
/sq:note fukuda2014,yang2024 --minireview --topic "protein stability" --focus research
```

### Citekey Matching Examples

| Citekey | Matches PDF Filename |
|---------|---------------------|
| `fukuda2014thermodynamic` | `Fukuda et al. - 2014 - Thermodynamic and Fluorescence...pdf` |
| `yang2024multi` | `Yang et al. - 2024 - Multi-scale Analysis...pdf` |
| `ganguly2012kirkwood` | `Ganguly et al. - 2012 - Kirkwood–Buff Coarse-Grained...pdf` |
| `smith2023data` | `Smith - 2023 - Data-driven approaches...pdf` |

### Error Handling
- **No Match Found**: Clear error with suggestions for improving the citekey
- **Multiple Matches**: Automatically selects best scoring match
- **Invalid Citekey**: Validation error with examples of proper citekey format

### Analysis Focus Areas

#### `--focus research` (Experimental Focus)
- **Targets**: Experimental research papers, empirical studies, data-driven investigations
- **Structure**: Research questions, methodology, results, statistical analysis, implications
- **Template**: Empirical research with experimental methodology sections
- **Length**: Adaptive to source paper length (see depth scaling below)
- **Emphasis**: Experimental design, data analysis, reproducibility, validation
- **YAML Type**: `empirical`

#### `--focus theory` (Theoretical Focus)
- **Targets**: Mathematical models, computational frameworks, theoretical papers
- **Structure**: Theoretical framework, mathematical formulation, model validation, applications
- **Template**: Theoretical analysis with mathematical focus
- **Length**: Adaptive to source paper length (see depth scaling below)
- **Emphasis**: Mathematical rigor, theoretical contributions, model validation
- **YAML Type**: `theoretical`

#### `--focus review` (Literature Focus)
- **Targets**: Literature reviews, survey papers, meta-analyses, systematic reviews
- **Structure**: Literature scope, synthesis, gaps analysis, future directions
- **Template**: Literature synthesis with comprehensive coverage
- **Length**: Adaptive to source paper length (see depth scaling below)
- **Emphasis**: Comprehensiveness, critical synthesis, research landscape
- **YAML Type**: `review`

#### `--focus method` (Methodological Focus)
- **Targets**: Methodological papers, technical procedures, protocol development
- **Structure**: Method overview, specifications, validation, applications, limitations
- **Template**: Technical methodology with detailed implementation
- **Length**: Adaptive to source paper length (see depth scaling below)
- **Emphasis**: Technical detail, reproducibility, practical implementation
- **YAML Type**: `methodological`

#### `--focus balanced` (Comprehensive Focus)
- **Targets**: General papers requiring multi-faceted analysis
- **Structure**: Adaptive comprehensive template covering all aspects
- **Template**: Integrated approach with balanced coverage
- **Length**: Adaptive to source paper length (see depth scaling below)
- **Emphasis**: Comprehensive coverage across all research dimensions
- **YAML Type**: `comprehensive`

### Analysis Depth Levels

#### `--depth quick`
- **Target Length**: 500-800 words
- **Processing Time**: ~30-60 seconds per paper
- **Coverage**: Essential points, key findings, basic methodology
- **Use Case**: Rapid screening, initial assessment, large batch processing

#### `--depth standard` (Default)
- **Target Length**: 700-1500 words  
- **Processing Time**: ~60-120 seconds per paper
- **Coverage**: Comprehensive analysis with detailed explanations
- **Use Case**: Regular literature note generation, balanced detail level

#### `--depth deep`
- **Target Length**: 1200-2800 words
- **Processing Time**: ~120-240 seconds per paper
- **Coverage**: Extensive analysis, critical evaluation, comprehensive context
- **Use Case**: Detailed research, thesis writing, comprehensive understanding

### Batch Processing Options

| Option | Description | Example |
|--------|-------------|---------|
| `--batch` | Enable batch processing for directories | `--batch` |
| `--theme` | Thematic analysis across multiple papers | `--theme "CRISPR evolution"` |
| `--output` | Output directory for generated notes | `--output literature_notes/` |
| `--parallel` | Enable parallel processing | `--parallel 4` |
| `--filter` | Filter papers by criteria | `--filter "year>=2020"` |

### File Naming and Organization

#### Automatic Naming Scheme
- **Format**: `author+year+firstword` (e.g., `smith2024protein.md`)
- **Rules**: `[last_name][year][first_meaningful_word]`
- **Examples**:
  - Yang et al. 2024 "Multi-domain Protein Design" → `yang2024multi.md`
  - Smith & Jones 2023 "Advanced CRISPR Methods" → `smith2023advanced.md`

#### Custom Naming Options
| Option | Description | Example |
|--------|-------------|---------|
| `--citekey` | Override automatic citekey generation | `--citekey smith2024custom` |
| `--prefix` | Add prefix to filename | `--prefix review_` |
| `--suffix` | Add suffix to filename | `--suffix _analysis` |

### Template and Format Options

| Option | Values | Description |
|--------|--------|-------------|
| `--template` | `experimental` \| `theoretical` \| `review` \| `method` \| `custom` | Note structure template |
| `--style` | `academic` \| `informal` \| `technical` | Writing style preference |
| `--citations` | `apa` \| `ieee` \| `nature` \| `custom` | Citation format style |
| `--tags` | `auto` \| `manual` \| `none` | Tag generation method |

## Behavioral Flow

### Single Paper Processing
1. **Validate**: Check PDF accessibility and format
2. **Extract**: PDF text and metadata extraction
3. **Analyze**: Content analysis and paper type classification
4. **Structure**: Apply appropriate template and focus area
5. **Generate**: Create structured markdown note
6. **Save**: Write to file with automatic naming

### Batch Processing
1. **Discover**: Scan directory for PDF files
2. **Filter**: Apply filtering criteria if specified
3. **Classify**: Group papers by type and theme
4. **Process**: Generate individual notes in parallel
5. **Organize**: Structure output directory with clear naming

### Mini-Review Processing
1. **Validate**: Ensure topic is specified and directory exists
2. **Analyze**: AI-driven examination of each PDF for topic relevance
3. **Filter**: Include only papers above relevance threshold
4. **Extract**: Gather key contributions, methods, and mechanistic insights
5. **Synthesize**: Create intelligent comprehensive topic-focused review
6. **Link**: Apply Obsidian [[filename]] linking throughout
7. **Visualize**: Generate advanced network diagram with mermaid
8. **Save**: Write single mini-review note (`Review_[topic].md`) with academic structure

## Mini-Review Mode: Intelligent Topic-Focused Analysis

### Overview
The `--minireview` mode creates **one comprehensive mini-review note** with intelligent analysis of multiple papers focusing on a specific topic. Unlike batch mode (which creates individual notes), mini-review mode generates a single academic review with mechanistic insights, Obsidian-style linking, and advanced network analysis of how your topic has been examined across the literature.

### Syntax
```bash
/sq:note <directory> --minireview --topic "topic description" [--focus type] [--depth level]
```

### Key Features
- **AI-Driven Topic Analysis**: Intelligent examination of papers for relevance to your specified topic
- **Mechanistic Insights**: Goes beyond listing to provide mechanistic understanding and theoretical advances
- **Obsidian Integration**: Full `[[filename]]` linking throughout for seamless note network
- **Advanced Network Visualization**: Sophisticated mermaid diagrams showing literature connections and evolution
- **Academic Quality**: Professional mini-review format suitable for research documentation
- **Template-Based Generation**: Uses sophisticated Jinja2 templates for consistent, customizable output
- **Smart Filename**: `Review_[topic].md` format with 50-character topic length limitation

### Example Commands
```bash
# Theoretical analysis of specific topic
/sq:note papers/ --minireview --topic "Kirkwood-Buff finite size correction" --focus theory --depth deep

# Methodological review
/sq:note papers/ --minireview --topic "protein folding mechanisms" --focus method --depth standard

# Comprehensive review across domains
/sq:note papers/ --minireview --topic "CRISPR applications" --focus balanced --depth deep
```

### Mini-Review vs Batch Mode Comparison

| Feature | Batch Mode (`--batch`) | Mini-Review Mode (`--minireview`) |
|---------|----------------------|------------------------------|
| **Output** | Multiple individual notes | One comprehensive mini-review |
| **Focus** | Process all papers | AI-driven topic-focused analysis |
| **Requirements** | Directory of PDFs | Directory + `--topic` |
| **Use Case** | Individual paper notes | Cross-paper mechanistic analysis |
| **File Naming** | `authoryeartitle.md` | `Review_[topic].md` |
| **Content** | Standard literature notes | Academic mini-review with mechanistic insights |
| **Linking** | Standard markdown | Obsidian `[[filename]]` linking |
| **Analysis Type** | Individual paper analysis | Intelligent network analysis |

### Mini-Review Output Structure
The mini-review mode generates a comprehensive academic review following this structure:

```markdown
# [Topic]: A Comprehensive Literature Network Review

## Overview
[Systematic review scope and significance]

## Identified References from Literature Collection
### Primary References Analyzed:
[Numbered list of papers with relevance indicators]

### Key Theoretical Frameworks Covered:
[Mathematical relationships and core equations]

## Detailed Reference Analysis
### Foundation Layer: Theoretical Development
### Computational Implementation Layer  
### Application Layer: Practical Implementations

## Network Connectivity Analysis
### Central Hub References
### Theoretical Foundation Cluster
### Computational Methods Cluster
### Application-Focused Cluster

## Literature Network Diagram
```mermaid
%%{init: {'flowchart': {'htmlLabels': true, 'useMaxWidth': true, 'curve': 'basis'}}}%%
%%{wrap}%%
graph LR
    [Interactive network visualization of paper relationships]
```

## Missing References and Gaps
### Incomplete Coverage Areas
### Research Gap Analysis

## Literature Network Evolution
### Historical Development
### Methodological Progression

## Future Directions and Recommendations
### Research Priorities
### Methodological Development

## Personal Synthesis Notes
[Space for user annotations and insights]
```

## Output Structure

### Generated Literature Note Sections

#### Standard Template Structure
```markdown
# Literature Note: [Paper Title]

## Citation Information
**Authors:** [Author List]
**Year:** [Publication Year]
**Journal:** [Journal Name]
**DOI:** [DOI Link]
**Citekey:** `[Generated Citekey]`

## Executive Summary
[2-3 sentence paper summary]

## [Focus-Specific Sections]
[Varies by focus area - see focus descriptions above]

## Key Findings
[Major results and conclusions]

## Critical Assessment
[Strengths, limitations, significance]

## Personal Notes and Insights
[Space for user annotations]

## Tags and Keywords
`[auto-generated tags]` `[domain]` `[method]` `literature-note`

---
**Note Generated:** [Timestamp]
**Analysis Method:** MCP + Claude direct PDF analysis
**Focus:** [Focus Area] | **Depth:** [Depth Level]
```

#### Metadata Block Format
```yaml
---
title: "Paper Title"
authors: ["Author 1", "Author 2"]
year: 2024
journal: "Journal Name"
doi: "10.xxxx/xxxxx"
citekey: "author2024title"
tags: ["tag1", "tag2", "tag3"]
focus: "theoretical"
depth: "standard"
generated: "2024-09-20T15:30:00Z"
---
```

### Batch Analysis Output

When using `--batch --theme`, an additional synthesis note is generated:

```markdown
# Batch Literature Analysis: [Theme]

## Analysis Overview
**Theme:** [Theme Description]
**Papers Analyzed:** [Count]
**Year Range:** [Start-End]
**Analysis Date:** [Date]

## Individual Paper Notes
[Links to individual notes]

## Cross-Paper Analysis
### Historical Evolution
[Chronological development analysis]

### Methodological Progression
[Method evolution across papers]

### Key Findings Synthesis
[Combined insights and patterns]

### Current State and Gaps
[Research landscape assessment]

### Future Trajectory
[Predicted research directions]

## Personal Synthesis
[User space for cross-paper insights]
```

## Tool Coordination

### Primary Tools
- **PDF Processing**: Intelligent text extraction and metadata parsing
- **Content Analysis**: Natural language processing for classification and sectioning
- **Template Engine**: Dynamic template selection and rendering
- **File Management**: Organized output with consistent naming

### Integration Points
- **MCP Protocol**: Seamless tool registration and execution
- **Task Delegation**: Complex PDF analysis delegated to specialized agents
- **Error Recovery**: Graceful handling of PDF reading limitations
- **Progress Tracking**: Real-time processing status for batch operations

## Examples

### Quick Literature Screening
```bash
/sq:note papers/recent_advances/ --batch --depth quick --filter "year>=2023"
```
**Use Case**: Rapidly assess 50+ recent papers  
**Output**: Concise 500-word notes focusing on key contributions  
**Time**: ~2-3 minutes for 20 papers

### Comprehensive Theoretical Analysis
```bash
/sq:note theoretical_paper.pdf --focus theoretical --depth deep --style academic
```
**Use Case**: Detailed analysis for thesis research  
**Output**: 2000+ word comprehensive note with mathematical details  
**Time**: ~3-4 minutes per paper

### Thematic Literature Review
```bash
/sq:note protein_folding_papers/ --batch --theme "AI approaches to protein folding" --focus method --output ai_folding_review/
```
**Use Case**: Systematic review across 15-30 papers  
**Output**: Individual method-focused notes + synthesis analysis  
**Time**: ~30-45 minutes for 25 papers

### Rapid Conference Paper Processing
```bash
/sq:note conference_proceedings/ --batch --depth quick --parallel 8 --filter "pages>=6"
```
**Use Case**: Process conference proceedings efficiently  
**Output**: Quick assessment notes for substantial papers  
**Time**: ~15-20 minutes for 100 papers

### Topic-Focused Synthesis Review
```bash
/sq:note research_collection/ --synthesize --topic "Kirkwood-Buff finite size correction" --focus theory --depth deep
```
**Use Case**: Comprehensive topic analysis across multiple papers  
**Output**: Single academic review with network visualization  
**Time**: ~5-10 minutes for 15-30 papers

### Cross-Domain Synthesis Analysis
```bash
/sq:note multidisciplinary_papers/ --synthesize --topic "machine learning in drug discovery" --focus balanced --depth standard
```
**Use Case**: Interdisciplinary topic review spanning multiple domains  
**Output**: Comprehensive synthesis with methodological progression analysis  
**Time**: ~3-8 minutes for 10-25 papers

## Advanced Features

### Intelligent PDF Handling
- **Multi-format Support**: Handles various PDF types and layouts
- **OCR Fallback**: Automatic OCR for scanned documents
- **Metadata Extraction**: Intelligent extraction from PDF properties and content
- **Error Recovery**: Graceful handling of corrupted or protected PDFs

### Content Intelligence
- **Paper Type Detection**: Automatic classification (experimental/theoretical/review/method)
- **Section Recognition**: Intelligent identification of paper sections
- **Equation Extraction**: Mathematical formula preservation
- **Figure/Table Awareness**: Recognition and description of visual elements

### Quality Assurance
- **Completeness Validation**: Ensures all template sections are filled
- **Citation Verification**: Validates extracted metadata
- **Consistency Checking**: Maintains style and format consistency
- **Error Reporting**: Clear feedback on processing issues

## Limitations and Boundaries

### Will Process
- Scientific papers in PDF format (text-based or OCR-capable)
- Individual papers or batch directories
- Papers in English and major European languages
- Various academic document formats and styles

### Will Not Process
- Non-academic content (news articles, blogs, marketing materials)
- Audio/video content or multimedia-heavy documents
- Password-protected or DRM-restricted PDFs
- Documents requiring specialized domain knowledge beyond scientific literature

### Performance Considerations
- **File Size Limit**: 50MB per PDF (configurable)
- **Batch Size Limit**: 50 papers per batch (configurable)
- **Processing Time**: Varies by depth (30 seconds to 4 minutes per paper)
- **Memory Usage**: Optimized for standard academic workstation resources

## Error Handling and Recovery

### Common Scenarios
- **PDF Reading Errors**: Automatic fallback to alternative extraction methods
- **Metadata Extraction Failures**: Graceful degradation with filename parsing
- **Template Rendering Issues**: Fallback to basic template structure
- **Batch Processing Interruptions**: Resume capability with progress tracking

### Error Response Format
```json
{
  "success": false,
  "error": {
    "type": "PDF_PROCESSING_ERROR",
    "message": "Failed to extract text from PDF",
    "code": "TEXT_EXTRACTION_FAILED",
    "suggestions": [
      "Check if PDF contains extractable text",
      "Try OCR if PDF contains scanned images",
      "Ensure PDF is not password-protected"
    ]
  },
  "partial_results": {
    "metadata_extracted": true,
    "filename_generated": "paper2024unknown.md"
  }
}
```

## Integration with Research Workflows

### Reference Management
- **Zotero Integration**: Compatible citekey and metadata formats
- **BibTeX Export**: Generate BibTeX entries from extracted metadata
- **Citation Networks**: Track cross-references between papers

### Knowledge Management
- **Obsidian Integration**: Compatible with graph-based note systems
- **Tag Systems**: Hierarchical and network-based tagging
- **Link Generation**: Automatic cross-references between related papers

### Academic Writing
- **Draft Integration**: Notes structured for direct integration into manuscripts
- **Citation Ready**: Properly formatted citations and references
- **Evidence Compilation**: Organized findings for systematic reviews

This comprehensive command interface provides researchers with a powerful tool for transforming their PDF literature into structured, searchable, and highly organized knowledge bases that support advanced academic workflows.