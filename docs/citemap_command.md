---
name: sq:citemap
description: "Create citation context maps and reference networks from scientific PDF papers"
category: citation analysis
complexity: advanced
mcp-servers: [scholarsquill]
personas: [academic, researcher]
---

# /sq:citemap - Citation Context Mapping and Reference Network Analysis

## Overview

The `/sq:citemap` command creates detailed citation context maps and reference networks from scientific PDF papers. It analyzes how papers connect different ideas through their citation practices, extracts reference relationships, and builds intellectual lineage networks showing the flow of ideas across literature.

## Triggers

- Citation analysis and reference mapping requirements
- Understanding intellectual connections between papers
- Reference network analysis and visualization needs
- Cross-paper citation relationship discovery
- Research lineage and influence tracking workflows

## Usage Syntax

```bash
/sq:citemap [target] [OPTIONS]
```

### Basic Usage
```bash
/sq:citemap paper.pdf                            # Single paper citation analysis
/sq:citemap papers/ --batch                      # Batch analysis with cross-references
/sq:citemap paper.pdf --output-dir citations/    # Custom output directory
```

### Advanced Usage
```bash
/sq:citemap papers/ --batch --output-dir network/  # Cross-reference network analysis
/sq:citemap paper.pdf --output-dir ./analysis/     # Detailed single paper analysis
```

## Command Options

### Core Parameters

| Option | Values | Default | Description | Mode |
|--------|--------|---------|-------------|------|
| `target` | `file.pdf` \| `directory/` | Required | PDF file or directory path | All |
| `--batch` | flag | false | Enable batch processing with cross-reference analysis | Batch |
| `--output-dir` | `directory/` | `citemap-analysis/` | Output directory for generated maps | All |

### Processing Modes

| Mode | Command Pattern | Output | Use Case |
|------|----------------|--------|----------|
| **Single** | `/sq:citemap paper.pdf` | One citation context map (`Citemap_[citekey].md`) | Individual paper citation analysis |
| **Batch** | `/sq:citemap papers/ --batch` | One comprehensive network analysis (`Citemap_Batch_[folder]_[count]papers.md`) | Cross-paper citation relationships |

## Analysis Features

### Single Paper Analysis
- **Citation Context Extraction**: Identifies all citations and their surrounding context
- **Reference List Processing**: Extracts and parses complete reference list
- **Citation Purpose Classification**: Categorizes citations by purpose (supporting evidence, contrasting view, methodology source, etc.)
- **Section Analysis**: Tracks which sections contain which types of citations
- **Network Generation**: Creates reference network diagram showing citation relationships

### Batch Analysis Features
- **Cross-Reference Detection**: Identifies papers that cite each other within the collection
- **Common Sources Analysis**: Finds references cited by multiple papers in the collection
- **Citation Pattern Analysis**: Statistical analysis of citation practices across papers
- **Intellectual Lineage Mapping**: Traces chronological citation relationships
- **Network Visualization**: Comprehensive network diagram of all citation relationships

## Citation Context Analysis

### Citation Purpose Categories

The system automatically categorizes citations by their purpose:

- **Supporting Evidence**: Citations used to support claims and arguments
- **Contrasting View**: Citations presenting opposing viewpoints or contradicting findings
- **Methodology Source**: Citations for methods, techniques, and procedures
- **Background Context**: Citations providing background information and context
- **Comparison**: Citations used for comparative analysis
- **General Reference**: Basic citations and general references

### Section Distribution Analysis

Tracks citation patterns across paper sections:
- **Introduction**: Background and context citations
- **Methods**: Methodology and procedural citations
- **Results**: Supporting evidence and comparison citations  
- **Discussion**: Interpretation and contrasting view citations

## Output Structure

### Single Paper Citemap (`Citemap_[citekey].md`)

```markdown
# Citation Context Map: [Paper Title]

## Citation Analysis Summary
- Total citations found
- Unique references count
- Network complexity metrics

## Citation Context Analysis
- Detailed citation contexts grouped by purpose
- Full surrounding context for each citation
- Section and purpose classification

## Reference Network
- Complete reference list with parsed metadata
- Network visualization with mermaid diagrams
- Citation relationship mapping

## Citation Pattern Analysis
- Section-wise citation distribution
- Purpose-wise citation usage statistics
- Citation density analysis

## Intellectual Connections
- Key citation contexts and their significance
- Network insights and connection patterns
- Citation practice analysis
```

### Batch Network Analysis (`Citemap_Batch_[folder]_[count]papers.md`)

```markdown
# Batch Citation Network Analysis

## Cross-Reference Analysis Summary
- Collection statistics and processing results
- Papers successfully analyzed

## Cross-Reference Relationships
- Papers citing each other within collection
- Bidirectional citation patterns
- Citation chains and lineage

## Common Sources Analysis
- Most frequently cited sources across papers
- Citation frequency distribution
- Shared intellectual foundations

## Citation Pattern Analysis
- Citation purpose distribution across collection
- Section distribution patterns
- Comparative citation practices

## Intellectual Lineage Analysis
- Foundational works in collection
- Chronological citation relationships
- Research evolution patterns

## Reference Network Visualization
- Cross-paper citation network diagram
- Network statistics and connectivity analysis
- Research landscape insights
```

## Behavioral Flow

### Single Paper Processing
1. **Extract PDF Content**: Parse PDF text and structure
2. **Identify Citations**: Use multiple citation format patterns to find all citations
3. **Extract Context**: Capture surrounding context for each citation
4. **Parse References**: Extract and parse complete reference list
5. **Classify Citations**: Determine purpose and section for each citation
6. **Build Network**: Create reference network representation
7. **Generate Analysis**: Produce comprehensive citation context map

### Batch Processing
1. **Discover Papers**: Scan directory for PDF files
2. **Process Individual Papers**: Generate citation data for each paper
3. **Cross-Reference Analysis**: Compare citations between papers
4. **Common Sources Detection**: Identify frequently cited sources
5. **Pattern Analysis**: Analyze citation practices across collection
6. **Network Construction**: Build comprehensive cross-paper network
7. **Generate Report**: Produce batch analysis with network visualization

## Advanced Features

### Citation Format Support
- **Author-Year**: (Smith 2020), Smith et al. (2019)
- **Numbered**: [1], [1-3], [1,2,5]
- **Mixed Formats**: Support for various citation styles within same paper

### Reference Parsing
- **Author Extraction**: Identifies primary and co-authors
- **Year Detection**: Extracts publication years
- **Title Parsing**: Attempts to extract paper titles
- **Journal Recognition**: Identifies publication venues when possible

### Network Analysis
- **Node Generation**: Creates nodes for each unique reference
- **Edge Creation**: Links based on citation contexts
- **Cluster Analysis**: Groups references by citation purpose
- **Centrality Metrics**: Identifies key references and connection patterns

## Use Cases and Examples

### Academic Research
```bash
# Analyze citation patterns in your own paper
/sq:citemap my_paper.pdf

# Compare citation practices across a research domain
/sq:citemap domain_papers/ --batch --output-dir domain_analysis/
```

### Literature Review Preparation
```bash
# Map citation landscape for literature review
/sq:citemap review_papers/ --batch --output-dir lit_review_citations/

# Understand reference relationships in key papers
/sq:citemap key_papers/ --batch
```

### Research Domain Analysis
```bash
# Analyze intellectual connections in a research area
/sq:citemap research_area_papers/ --batch --output-dir network_analysis/

# Track citation lineage in emerging field
/sq:citemap emerging_field/ --batch
```

## Integration with Research Workflows

### Reference Management
- **Citation Discovery**: Identify key papers through citation analysis
- **Reference Validation**: Verify reference completeness and accuracy
- **Network Mapping**: Understand intellectual connections between papers

### Literature Review
- **Foundation Identification**: Find foundational works through citation frequency
- **Gap Analysis**: Identify under-cited or missing references
- **Trend Analysis**: Track citation patterns over time

### Academic Writing
- **Citation Strategy**: Understand effective citation practices
- **Reference Selection**: Choose appropriate references based on purpose
- **Network Positioning**: Position your work within citation networks

## Output File Naming

### Single Paper Analysis
- **Format**: `Citemap_[citekey].md`
- **Example**: `Citemap_smith2024neural.md`

### Batch Analysis
- **Format**: `Citemap_Batch_[folder]_[count]papers.md`
- **Example**: `Citemap_Batch_ml_papers_15papers.md`

## Performance Considerations

### Processing Time
- **Single Paper**: 30-60 seconds average
- **Batch Processing**: 2-5 minutes for 10-20 papers
- **Large Collections**: Scales linearly with paper count

### Accuracy Factors
- **PDF Quality**: Text-based PDFs provide better accuracy than scanned images
- **Citation Formats**: Consistent citation formatting improves detection
- **Reference Lists**: Well-formatted reference sections enable better parsing

## Limitations and Boundaries

### Will Process
- Scientific papers in standard PDF formats
- Papers with extractable text content
- Standard academic citation formats
- Individual papers or directories of papers

### Will Not Process
- Non-academic content or documents
- Heavily formatted or image-based PDFs without OCR
- Papers with non-standard or proprietary citation formats
- Password-protected or DRM-restricted PDFs

### Accuracy Considerations
- Citation detection accuracy depends on format consistency
- Reference parsing may vary based on formatting standards
- Cross-reference matching relies on author-year patterns
- Network analysis quality improves with larger collections

## Error Handling

### Common Issues
- **Citation Detection Failures**: Automatic fallback to alternative patterns
- **Reference Parsing Errors**: Graceful degradation with partial information
- **Cross-Reference Matching**: Conservative matching to avoid false positives
- **Network Generation**: Handles incomplete or missing data

### Recovery Strategies
- **Multiple Citation Patterns**: Uses various regex patterns for comprehensive detection
- **Partial Processing**: Continues with available data when some elements fail
- **Error Reporting**: Provides detailed feedback on processing issues
- **Fallback Options**: Alternative processing paths for difficult documents

This comprehensive citation context mapping tool provides researchers with powerful insights into the intellectual connections and reference relationships that structure academic literature, enabling deeper understanding of research domains and more effective literature analysis.