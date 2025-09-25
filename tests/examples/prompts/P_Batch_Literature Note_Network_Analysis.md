# Literature Network Analysis Prompt

## Task Overview
Create a comprehensive literature network review analyzing the interconnected references within a specific manuscript subsection, similar to existing network reviews in the project.

## Input Requirements
- **Target subsection**: Specify the manuscript subsection requiring analysis
- **Reference list**: Identified citations from the subsection  
- **Existing literature notes**: Available analysis in `@03-PROJECTS/RP5/00 Literature Notes/`
- **Zotero storage**: PDF access for missing literature notes
- **Template reference**: Existing network review file for structural guidance

## Analysis Framework

### Step 1: Reference Inventory
- [ ] Extract all citations from target subsection
- [ ] Check availability of literature notes for each reference
- [ ] Identify missing references requiring analysis
- [ ] Categorize references by availability status

### Step 2: Comprehensive Reference Analysis
For each reference, document:
- **Key Contribution**: Primary theoretical/methodological innovation
- **Theoretical Framework**: Mathematical equations, core concepts
- **Methodological Innovation**: Novel approaches or techniques  
- **Applications**: Practical implementations and systems studied
- **Connection**: How it links to other references in the network

### Step 3: Missing Reference Research
For references without literature notes:
- [ ] Search web for key publications and theoretical contributions
- [ ] Read available PDFs using PyPDF2 for text extraction
- [ ] Check `.zotero-ft-cache` files for preprocessed content
- [ ] Analyze theoretical frameworks and methodological contributions

### Step 4: Network Connectivity Analysis
Document:
- **Hub References**: Most connected/cited works (identify top 3)
- **Theoretical Clusters**: Groups of related foundational work
- **Methodological Clusters**: Computational implementation developments  
- **Application Clusters**: Practical/therapeutic applications
- **Critical Pathways**: Key development routes through the network

### Step 5: Network Visualization
Create Mermaid diagram with:
- **Configuration Header**: 
  ```
  %%{init: {'flowchart': {'htmlLabels': true, 'useMaxWidth': true, 'curve': 'basis'}}}%%
  %%{wrap}%%
  ```
- **Layout**: Left-right flow (`graph LR`) for optimal display width
- **Temporal Layers**: Subgraphs showing chronological development
- **Node Styling**: 
  - Hub references: Yellow fill, thick border
  - Complete analysis: Green fill, solid border
  - Missing/incomplete: Red fill, dashed border
- **Connection Types**: Solid arrows for established links, dashed for gaps
- **Compact Labels**: Short reference names with key descriptors

### Step 6: Historical Evolution Analysis
Document:
- **Historical Development**: Chronological progression of the field
- **Methodological Progression**: Evolution from theory to applications
- **Scope Extensions**: How frameworks expanded over time
- **Missing Elements**: Gaps requiring additional research

## Output Structure

### File Organization
Create: `/03-PROJECTS/RP5/00 Literature Notes/[Subsection]_Network_Review.md`

### Content Structure
```markdown
# [Subsection Name]: A Comprehensive Literature Network Review

## Overview
[Brief description of the literature network scope and significance]

## Identified References from "[Subsection Name]"
### Primary References Cited:
[Numbered list with status indicators]

### Key Theoretical Frameworks Covered:
[Mathematical relationships and core equations]

## Detailed Reference Analysis
### Foundation Layer: [Category Name]
[Detailed analysis by reference with status, contributions, frameworks]

### Computational Implementation Layer
[Methods and computational developments]

### Application Layer: [Domain Name]  
[Practical applications and recent developments]

### Missing References - Comprehensive Web Analysis
[Analysis of references without literature notes]

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
    [Complete network diagram following the specification above]
```
[Analysis key and network statistics]

## Missing References and Gaps
### Incomplete Citations
### Potential Additional Key References
### Modern Computational Gaps

## Literature Network Evolution
### Historical Development
### Methodological Progression

[Concluding synthesis of network maturity and applications]
```

## Quality Standards

### Analysis Depth
- **Complete Coverage**: All cited references analyzed or status documented
- **Theoretical Rigor**: Mathematical frameworks and equations included
- **Methodological Detail**: Implementation approaches and innovations
- **Connection Clarity**: Explicit links between references documented

### Network Visualization
- **Mermaid Configuration**: Include `%%{init: {'flowchart': {'htmlLabels': true, 'useMaxWidth': true, 'curve': 'basis'}}}%%` and `%%{wrap}%%` headers
- **Display Optimization**: Wide layout for screen compatibility with responsive sizing
- **Visual Hierarchy**: Clear distinction between reference types
- **Temporal Flow**: Chronological development visible
- **Gap Identification**: Missing elements clearly marked

### Documentation Standards
- **Citation Consistency**: Use project citekey format throughout
- **Status Tracking**: Clear indicators for analysis completeness
- **Cross-Referencing**: Links to existing literature notes where available
- **Comprehensive Coverage**: No references left unanalyzed or unexplained

## Tools and Resources

### Search and Analysis Tools
- **Web Search**: For missing references and theoretical background
- **PDF Analysis**: PyPDF2 for text extraction from zotero storage
- **Literature Notes**: Existing analysis in project folders
- **Cross-References**: Connection to related network reviews

### Technical Implementation
- **File Reading**: Use Read tool for literature notes and cached content
- **Text Processing**: Extract key theoretical contributions and methodologies
- **Network Analysis**: Identify hubs, clusters, and critical pathways
- **Visualization**: Mermaid diagrams optimized for display width

## Success Criteria
- [ ] All references from subsection analyzed or status documented
- [ ] Network connectivity patterns identified and visualized
- [ ] Historical development and methodological progression documented
- [ ] Missing elements and research gaps clearly identified  
- [ ] Comprehensive review file created following established format
- [ ] Visual network diagram optimized for display and analysis

This framework ensures systematic, comprehensive analysis of literature networks supporting specific manuscript subsections, providing both detailed reference analysis and broader network understanding for academic research projects.