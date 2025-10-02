# Implementation Plan: Zotero and Obsidian Integration

**Based on**: [ZOTERO_OBSIDIAN_INTEGRATION_SPEC.md](./ZOTERO_OBSIDIAN_INTEGRATION_SPEC.md)
**Status**: Ready for Implementation
**Created**: 2025-10-02
**Target Completion**: 6 weeks

---

## Executive Summary

This implementation plan outlines the development approach for integrating Zotero and Obsidian with ScholarsQuill. The integration will enable automated literature note generation from Zotero libraries with enhanced metadata mapping and Obsidian-compatible output.

**Key Deliverables**:
- Zotero API client with metadata mapping
- Batch collection processor
- Enhanced YAML frontmatter templates
- CLI commands for Zotero integration
- Obsidian-compatible markdown output
- Citation network enhancement using Zotero relations

---

## Phase 0: Research and Architecture Design

**Duration**: 3 days
**Dependencies**: None

### Research Tasks

**R1: Zotero API Deep Dive**
- Study Pyzotero API documentation in detail
- Test API rate limits and error responses
- Document all Zotero item types and their fields
- Create mapping table: Zotero fields → ScholarsQuill metadata
- Research best practices for API key management

**R2: Obsidian Format Standards**
- Review Obsidian YAML frontmatter specifications
- Test Obsidian property types (text, list, date, etc.)
- Document wikilink syntax and variations
- Research Obsidian plugin compatibility requirements
- Test Obsidian Local REST API capabilities

**R3: Citation Network Data Structures**
- Analyze Zotero relations structure
- Design citation graph representation
- Plan integration with existing citemap processor
- Research graph visualization options

**R4: Existing Codebase Analysis**
- Map current metadata extraction flow
- Identify reusable components
- Document template system architecture
- List required changes to existing code

### Architecture Design

**AD1: Component Architecture**
```
src/
├── zotero/
│   ├── __init__.py
│   ├── client.py              # ZoteroClient wrapper
│   ├── mapper.py              # Metadata mapping
│   ├── batch.py               # Batch processor
│   ├── cache.py               # Caching layer
│   └── models.py              # Zotero-specific models
├── obsidian/
│   ├── __init__.py
│   ├── writer.py              # Markdown writer
│   ├── formatter.py           # YAML frontmatter
│   └── rest_client.py         # Optional REST API
└── models.py                  # Enhanced PaperMetadata
```

**AD2: Data Flow Design**
```
Zotero Library
    ↓ (Pyzotero API)
ZoteroClient.fetch_items()
    ↓
ZoteroMetadataMapper.map()
    ↓
EnhancedPaperMetadata
    ↓
Existing Template Engine
    ↓
ObsidianWriter.write()
    ↓
Obsidian Vault (Markdown files)
```

**AD3: Configuration Strategy**
- Environment variables for API keys
- YAML config file for preferences
- Command-line arguments for runtime options
- Secure keyring integration (optional)

### Deliverables

- `docs/research/zotero-api-analysis.md` - Zotero API research findings
- `docs/research/obsidian-format-spec.md` - Obsidian format requirements
- `docs/research/metadata-mapping-table.md` - Complete field mapping
- `docs/architecture/component-design.md` - Detailed component specs
- `docs/architecture/data-flow.md` - System data flow diagrams

---

## Phase 1: Core Zotero Integration

**Duration**: 2 weeks
**Dependencies**: Phase 0 complete

### Sprint 1.1: Zotero Client Foundation (Week 1)

**Task 1.1.1: Project Setup**
- Add Pyzotero to dependencies in `pyproject.toml`
- Create `src/zotero/` package structure
- Set up test infrastructure for Zotero integration
- Create mock Zotero responses for testing

**Task 1.1.2: ZoteroClient Implementation**
```python
# src/zotero/client.py
class ZoteroClient:
    def __init__(self, library_id, library_type, api_key)
    def test_connection() -> bool
    def get_item(item_key: str) -> Dict
    def get_items(limit: int = 100) -> List[Dict]
    def get_collection(collection_key: str) -> Dict
    def get_collections() -> List[Dict]
    def get_collection_items(collection_key: str) -> List[Dict]
    def get_item_attachments(item_key: str) -> List[Dict]
```

**Task 1.1.3: Configuration Management**
```python
# src/zotero/config.py
@dataclass
class ZoteroConfig:
    library_id: str
    library_type: str
    api_key: str
    cache_enabled: bool = True
    cache_dir: Optional[Path] = None
    rate_limit_delay: float = 0.5

    @classmethod
    def from_env() -> ZoteroConfig

    @classmethod
    def from_file(config_path: Path) -> ZoteroConfig
```

**Task 1.1.4: Error Handling**
- Implement custom exception hierarchy
- Add retry logic with exponential backoff
- Create error logging system
- Handle API rate limiting gracefully

**Task 1.1.5: Unit Tests**
- Test connection validation
- Test error handling and retries
- Test configuration loading
- Mock API responses for offline testing

### Sprint 1.2: Metadata Mapping (Week 2)

**Task 1.2.1: Enhanced Data Models**
```python
# src/models.py
@dataclass
class EnhancedPaperMetadata(PaperMetadata):
    # Zotero-specific fields
    zotero_key: Optional[str] = None
    zotero_url: Optional[str] = None
    zotero_tags: List[str] = field(default_factory=list)
    zotero_collections: List[str] = field(default_factory=list)
    zotero_relations: Dict[str, List[str]] = field(default_factory=dict)
    date_added: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    abstract: Optional[str] = None
    url: Optional[str] = None

    def to_yaml_dict(self) -> Dict[str, Any]
```

**Task 1.2.2: ZoteroMetadataMapper Implementation**
```python
# src/zotero/mapper.py
class ZoteroMetadataMapper:
    def map_item(self, zotero_item: Dict) -> EnhancedPaperMetadata
    def map_creators(self, creators: List[Dict]) -> Tuple[str, List[str]]
    def map_tags(self, tags: List[Dict]) -> List[str]
    def map_collections(self, collections: List[str], client: ZoteroClient) -> List[str]
    def map_relations(self, relations: Dict) -> Dict[str, List[str]]
    def generate_zotero_url(self, library_id: str, library_type: str, item_key: str) -> str
```

**Task 1.2.3: Item Type Handlers**
- Create handlers for each Zotero item type:
  - `journalArticle` → journal article metadata
  - `book` → book metadata
  - `bookSection` → book chapter metadata
  - `conferencePaper` → conference paper metadata
  - `thesis` → thesis metadata
  - `report` → report metadata
  - Generic handler for other types

**Task 1.2.4: Validation Layer**
- Validate all mapped fields
- Handle missing or malformed data
- Log mapping warnings
- Fallback strategies for missing data

**Task 1.2.5: Integration Tests**
- Test mapping for all item types
- Test edge cases (missing fields, special characters)
- Test author name formatting
- Test citekey generation from Zotero data

### Sprint 1.3: Template Enhancement (Week 2)

**Task 1.3.1: Update YAML Frontmatter Templates**
Modify all templates (`balanced.md`, `research.md`, etc.):
```jinja2
> [!Metadata]
> **FirstAuthor**:: {{ first_author }}
{%- for author in authors %}
> **Author**:: {{ author }}
{%- endfor %}
> **Title**:: {{ title }}
> **Year**:: {{ year or "Unknown" }}
> **Citekey**:: {{ citekey }}
> **itemType**:: {{ item_type }}
{%- if journal %}
> **Journal**:: *{{ journal }}*
{%- endif %}
{%- if doi %}
> **DOI**:: {{ doi }}
{%- endif %}
> **PDF**:: [[{{ source_path }}]]
>
> **Zotero**:: [Open in Zotero]({{ zotero_url }})
> **ZoteroKey**:: {{ zotero_key }}
{%- if zotero_tags %}
> **ZoteroTags**:: {{ zotero_tags | join(', ') }}
{%- endif %}
{%- if zotero_collections %}
> **Collections**:: {{ zotero_collections | join(' > ') }}
{%- endif %}
{%- if date_added %}
> **DateAdded**:: {{ date_added }}
{%- endif %}
{%- if abstract %}

## Abstract
{{ abstract }}
{%- endif %}
```

**Task 1.3.2: Create Obsidian-Specific Template**
New template: `templates/obsidian.md`
- Obsidian property format
- Wikilink syntax for citations
- Tag formatting
- Callout blocks

**Task 1.3.3: Template Testing**
- Test all templates with Zotero metadata
- Verify Obsidian compatibility
- Test edge cases (special characters, long text)

### Phase 1 Deliverables

✅ `src/zotero/client.py` - Zotero API client
✅ `src/zotero/mapper.py` - Metadata mapper
✅ `src/zotero/config.py` - Configuration management
✅ `src/models.py` - Enhanced metadata models
✅ Updated templates with Zotero frontmatter
✅ Unit tests with >80% coverage
✅ Integration tests for API interaction
✅ Documentation: API usage, configuration guide

---

## Phase 2: Batch Processing

**Duration**: 1 week
**Dependencies**: Phase 1 complete

### Sprint 2.1: Batch Processor Core

**Task 2.1.1: Batch Processor Implementation**
```python
# src/zotero/batch.py
class ZoteroBatchProcessor:
    def __init__(self, client: ZoteroClient, output_dir: Path)

    def process_collection(
        self,
        collection_key: str,
        template_focus: str = "balanced",
        depth: str = "standard"
    ) -> BatchResult

    def process_all_items(
        self,
        template_focus: str = "balanced",
        depth: str = "standard",
        max_items: Optional[int] = None
    ) -> BatchResult

    def process_items_by_tag(
        self,
        tag: str,
        template_focus: str = "balanced"
    ) -> BatchResult
```

**Task 2.1.2: Progress Tracking**
```python
# src/zotero/progress.py
@dataclass
class BatchProgress:
    total_items: int
    processed_items: int
    failed_items: int
    current_item: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)

    def update(self, item_key: str, success: bool)
    def get_eta(self) -> timedelta
    def to_dict(self) -> Dict
```

**Task 2.1.3: Chunking and Pagination**
- Implement 50-item chunk processing (Zotero API limit)
- Add pagination for large collections
- Handle API pagination tokens
- Resume capability for interrupted processing

**Task 2.1.4: Error Recovery**
- Checkpoint saving after each chunk
- Resume from checkpoint on failure
- Individual item error handling (continue on error)
- Detailed error reporting

**Task 2.1.5: Caching Layer**
```python
# src/zotero/cache.py
class ZoteroCache:
    def __init__(self, cache_dir: Path)

    def get_item(self, item_key: str) -> Optional[Dict]
    def set_item(self, item_key: str, item_data: Dict)
    def get_collection(self, collection_key: str) -> Optional[Dict]
    def set_collection(self, collection_key: str, collection_data: Dict)
    def invalidate(self, item_key: str)
    def clear_all()
```

### Sprint 2.2: Output Organization

**Task 2.2.1: Collection → Folder Mapping**
```python
# src/obsidian/organizer.py
class ObsidianOrganizer:
    def create_folder_structure(
        self,
        collections: List[Dict],
        base_dir: Path
    ) -> Dict[str, Path]

    def get_output_path(
        self,
        item: EnhancedPaperMetadata,
        collection_paths: Dict[str, Path]
    ) -> Path

    def handle_name_conflicts(self, path: Path) -> Path
```

**Task 2.2.2: File Naming Strategy**
- Use citekey as filename: `smith2023neural.md`
- Handle duplicate citekeys (add suffix)
- Sanitize filenames for filesystem compatibility
- Create index file for each collection

**Task 2.2.3: Batch Result Reporting**
```python
@dataclass
class BatchResult:
    total_items: int
    successful: int
    failed: int
    skipped: int
    output_files: List[Path]
    errors: List[BatchError]
    duration: timedelta

    def to_summary(self) -> str
    def save_report(self, path: Path)
```

### Phase 2 Deliverables

✅ `src/zotero/batch.py` - Batch processor
✅ `src/zotero/progress.py` - Progress tracking
✅ `src/zotero/cache.py` - Caching system
✅ `src/obsidian/organizer.py` - Output organization
✅ Integration tests for batch processing
✅ Performance benchmarks (100 items in <2 min)
✅ Documentation: Batch processing guide

---

## Phase 3: CLI Integration

**Duration**: 1 week
**Dependencies**: Phase 2 complete

### Sprint 3.1: Command Implementation

**Task 3.1.1: Create `/zotero-note` Command**
```markdown
# .claude/commands/zotero-note.md
Process Zotero library items into literature notes.

Usage:
/zotero-note <collection_name> [options]
/zotero-note --all [options]
/zotero-note --item-key <key> [options]

Options:
--focus <type>     Template focus (research|theory|method|review|balanced)
--depth <level>    Analysis depth (quick|standard|deep)
--output <dir>     Output directory (default: literature-notes/)
--batch            Enable batch processing mode
--dry-run          Preview without writing files
--cache            Enable caching (default: true)

Examples:
/zotero-note "Machine Learning" --focus research --depth deep
/zotero-note --all --batch --output obsidian-vault/literature
/zotero-note --item-key ABC123 --focus balanced
```

**Task 3.1.2: Interactive Collection Picker**
```python
# src/zotero/cli_helpers.py
def select_collection(client: ZoteroClient) -> str:
    """Interactive collection selection with arrow keys"""
    collections = client.get_collections()
    # Use rich for interactive menu
    return selected_collection_key

def confirm_batch_processing(item_count: int) -> bool:
    """Confirm before processing large batches"""
    return user_confirmed
```

**Task 3.1.3: Configuration File Support**
```yaml
# .scholarsquill/zotero-config.yml
zotero:
  library_id: "12345"
  library_type: "user"
  # API key from environment: ZOTERO_API_KEY

output:
  default_dir: "obsidian-vault/literature"
  organize_by_collection: true

templates:
  default_focus: "balanced"
  default_depth: "standard"

cache:
  enabled: true
  dir: ".scholarsquill/cache/zotero"
  ttl_hours: 24
```

**Task 3.1.4: Environment Variable Support**
```bash
# Required
export ZOTERO_API_KEY="your-api-key"
export ZOTERO_LIBRARY_ID="12345"
export ZOTERO_LIBRARY_TYPE="user"

# Optional
export SCHOLARSQUILL_OUTPUT_DIR="obsidian-vault/"
export SCHOLARSQUILL_CACHE_DIR=".cache/zotero"
```

**Task 3.1.5: Enhanced `/note` Command**
Extend existing `/note` to support Zotero:
```bash
/note --zotero ABC123 --focus research
/note paper.pdf --enrich-from-zotero  # Find in Zotero by DOI/title
```

### Sprint 3.2: CLI User Experience

**Task 3.2.1: Progress Display**
- Use `rich` library for progress bars
- Show current item being processed
- Display ETA for batch operations
- Real-time error reporting

**Task 3.2.2: Dry-Run Mode**
- Preview what would be created
- Show metadata mapping for first 5 items
- Display output file structure
- No file writes, no API changes

**Task 3.2.3: Validation and Helpful Errors**
```python
def validate_config() -> List[str]:
    """Validate configuration and return errors"""
    errors = []
    if not os.getenv('ZOTERO_API_KEY'):
        errors.append("Missing ZOTERO_API_KEY environment variable")
    # ... more validations
    return errors

def suggest_fixes(error: Exception) -> str:
    """Provide actionable error messages"""
    # Map errors to solutions
```

**Task 3.2.4: Success Summary**
```
✅ Batch Processing Complete!

📊 Summary:
   Total Items: 147
   Successful: 145
   Failed: 2
   Duration: 2m 34s

📁 Output:
   Directory: obsidian-vault/literature/
   Files Created: 145

⚠️  Warnings:
   - 2 items missing DOI
   - 1 duplicate citekey (renamed to smith2023neural-2.md)

🔗 Next Steps:
   - Review failed items: /zotero-note --retry-failed
   - Generate citation map: /citemap --zotero-collection "Machine Learning"
```

### Phase 3 Deliverables

✅ `.claude/commands/zotero-note.md` - New command
✅ Enhanced `/note` command with Zotero support
✅ Interactive CLI helpers
✅ Configuration file support
✅ Environment variable handling
✅ Rich progress displays
✅ Documentation: CLI usage guide

---

## Phase 4: Obsidian Enhancement

**Duration**: 1 week
**Dependencies**: Phase 3 complete

### Sprint 4.1: Obsidian Writer

**Task 4.1.1: ObsidianWriter Implementation**
```python
# src/obsidian/writer.py
class ObsidianWriter:
    def __init__(self, vault_path: Path)

    def write_note(
        self,
        metadata: EnhancedPaperMetadata,
        content: str,
        collection_path: Optional[Path] = None
    ) -> Path

    def create_folder_structure(self, collections: List[str]) -> Dict[str, Path]

    def generate_wikilinks(
        self,
        citing_items: List[str],
        cited_items: List[str]
    ) -> str
```

**Task 4.1.2: YAML Frontmatter Formatter**
```python
# src/obsidian/formatter.py
class ObsidianFormatter:
    def format_frontmatter(self, metadata: EnhancedPaperMetadata) -> str:
        """Generate Obsidian-compatible YAML frontmatter"""

    def format_property(self, key: str, value: Any) -> str:
        """Format individual property for Obsidian"""

    def format_tags(self, tags: List[str]) -> str:
        """Format tags in Obsidian style"""

    def format_aliases(self, metadata: EnhancedPaperMetadata) -> List[str]:
        """Generate appropriate aliases"""
```

**Task 4.1.3: Wikilink Generation**
- Generate `[[citekey]]` links for citations
- Create `[[author YEAR]]` aliases
- Link to related papers via Zotero relations
- Link to collections and tags

**Task 4.1.4: Callout Blocks**
```markdown
> [!abstract]
> Paper abstract here...

> [!cite]
> BibTeX citation

> [!related]
> - [[related-paper-1]]
> - [[related-paper-2]]
```

### Sprint 4.2: Obsidian REST API (Optional)

**Task 4.2.1: REST Client Implementation**
```python
# src/obsidian/rest_client.py
class ObsidianRESTClient:
    def __init__(self, api_url: str = "https://127.0.0.1:27124")

    def create_note(self, path: str, content: str) -> bool
    def update_note(self, path: str, content: str) -> bool
    def read_note(self, path: str) -> str
    def list_notes(self, path: str = "/") -> List[str]
```

**Task 4.2.2: Direct Vault Manipulation**
- Create notes directly in Obsidian
- Update existing notes without file writes
- Check for duplicates before creating
- Trigger Obsidian refresh after batch

**Task 4.2.3: Configuration**
```yaml
obsidian:
  use_rest_api: false  # Default to file-based
  api_url: "https://127.0.0.1:27124"
  api_key: "optional-api-key"
```

### Sprint 4.3: Example Vault Structure

**Task 4.3.1: Create Template Vault**
```
obsidian-vault-template/
├── .obsidian/
│   ├── workspace.json
│   └── community-plugins.json
├── literature-notes/
│   ├── README.md
│   └── .gitkeep
├── citemap-analysis/
│   └── .gitkeep
├── templates/
│   ├── literature-note.md
│   └── citation-map.md
└── .scholarsquill/
    ├── zotero-config.yml
    └── README.md
```

**Task 4.3.2: Documentation**
- Setup guide for Obsidian vault
- Recommended Obsidian plugins
- Sample queries using Dataview
- CSS snippets for ScholarsQuill notes

### Phase 4 Deliverables

✅ `src/obsidian/writer.py` - Markdown writer
✅ `src/obsidian/formatter.py` - YAML formatter
✅ `src/obsidian/rest_client.py` - REST API client (optional)
✅ Example Obsidian vault template
✅ Obsidian integration guide
✅ CSS snippets for custom styling

---

## Phase 5: Citation Network Integration

**Duration**: 1 week
**Dependencies**: Phase 4 complete

### Sprint 5.1: Zotero Relations Extraction

**Task 5.1.1: Relations Parser**
```python
# src/zotero/relations.py
class RelationsExtractor:
    def extract_relations(self, item: Dict) -> Dict[str, List[str]]:
        """Extract citation relationships from Zotero item"""

    def get_citing_items(self, item_key: str, client: ZoteroClient) -> List[str]:
        """Find items that cite this item"""

    def get_cited_items(self, item_key: str) -> List[str]:
        """Get items cited by this item"""

    def build_citation_graph(self, items: List[Dict]) -> nx.Graph:
        """Build NetworkX graph from Zotero relations"""
```

**Task 5.1.2: Enhanced Citemap Processor**
```python
# src/citemap_processor.py (existing file - enhance)
class CitemapProcessor:
    # Existing methods...

    def process_with_zotero(
        self,
        item_key: str,
        client: ZoteroClient
    ) -> CitemapResult:
        """Generate citemap using Zotero relations"""

    def build_network_from_zotero(
        self,
        collection_key: str,
        client: ZoteroClient
    ) -> nx.Graph:
        """Build citation network for entire collection"""
```

**Task 5.1.3: Citation Context Enhancement**
- Extract citation context from PDF (existing)
- Enhance with Zotero metadata (new)
- Combine both sources for rich citation data
- Generate comparative analysis

### Sprint 5.2: Visualization Enhancement

**Task 5.2.1: Interactive Network Graph**
```python
# src/zotero/visualizer.py
def create_citation_network_viz(
    graph: nx.Graph,
    metadata_map: Dict[str, EnhancedPaperMetadata],
    output_path: Path
) -> Path:
    """Create interactive Plotly visualization"""
    # Node: Paper (colored by collection)
    # Edge: Citation relationship
    # Hover: Full metadata
    # Click: Open in Zotero/Obsidian
```

**Task 5.2.2: Network Analysis Metrics**
- Calculate centrality measures
- Identify key papers (high betweenness)
- Find paper clusters (communities)
- Trace citation lineage paths

**Task 5.2.3: Export Formats**
- HTML (interactive Plotly)
- GraphML (for Gephi/Cytoscape)
- JSON (for custom processing)
- Markdown report with analysis

### Sprint 5.3: Integration with Existing Citemap

**Task 5.3.1: Unified Citemap Command**
```bash
# Enhanced /citemap command
/citemap paper.pdf                    # Existing: PDF-based
/citemap --zotero ABC123             # New: Zotero item
/citemap --zotero-collection "ML"    # New: Entire collection
/citemap paper.pdf --enrich-zotero   # Hybrid: PDF + Zotero data
```

**Task 5.3.2: Merge Citation Data**
```python
def merge_citation_sources(
    pdf_citations: List[Citation],
    zotero_relations: Dict[str, List[str]],
    client: ZoteroClient
) -> List[EnrichedCitation]:
    """Combine PDF-extracted and Zotero citations"""
```

**Task 5.3.3: Citation Network Markdown**
```markdown
# Citation Network: Machine Learning Collection

## Network Statistics
- **Total Papers**: 147
- **Total Citations**: 523
- **Average Citations per Paper**: 3.6
- **Network Density**: 0.15

## Key Papers (High Centrality)
1. [[smith2023neural]] - Betweenness: 0.45
2. [[jones2022deep]] - Betweenness: 0.38
3. [[brown2021transformer]] - Betweenness: 0.31

## Citation Clusters
### Cluster 1: Deep Learning Fundamentals
- [[lecun2015deep]]
- [[goodfellow2016gan]]
- [[he2016resnet]]

### Cluster 2: Transformers and Attention
- [[vaswani2017attention]]
- [[devlin2019bert]]
- [[brown2020gpt3]]

## Visualization
[Interactive Network](./ml-collection-network.html)
```

### Phase 5 Deliverables

✅ `src/zotero/relations.py` - Relations extractor
✅ `src/zotero/visualizer.py` - Network visualization
✅ Enhanced `src/citemap_processor.py`
✅ Unified `/citemap` command with Zotero support
✅ Network analysis metrics
✅ Documentation: Citation network guide

---

## Phase 6: Testing and Documentation

**Duration**: 1 week
**Dependencies**: Phases 1-5 complete

### Sprint 6.1: Comprehensive Testing

**Task 6.1.1: Unit Test Coverage**
- Target: >80% code coverage
- Test all Zotero client methods
- Test metadata mapping for all item types
- Test batch processing logic
- Test error handling and retries

**Task 6.1.2: Integration Tests**
```python
# tests/integration/test_zotero_integration.py
def test_full_workflow_single_item():
    """Test: Zotero → ScholarsQuill → Obsidian"""

def test_batch_collection_processing():
    """Test batch processing of real collection"""

def test_citation_network_generation():
    """Test citation network from Zotero"""

def test_error_recovery():
    """Test checkpoint and resume"""
```

**Task 6.1.3: Performance Testing**
```python
# tests/performance/test_batch_performance.py
def test_100_items_under_2_minutes():
    """Benchmark: 100 items in <2 minutes"""

def test_memory_usage_1000_items():
    """Memory: <500MB for 1000 items"""

def test_cache_effectiveness():
    """Cache hit rate >70%"""
```

**Task 6.1.4: End-to-End Testing**
- Real Zotero library test
- Real Obsidian vault integration
- Manual verification of all features
- Cross-platform testing (macOS, Linux, Windows)

### Sprint 6.2: Documentation

**Task 6.2.1: User Documentation**

**Getting Started Guide**: `docs/guides/zotero-obsidian-quickstart.md`
```markdown
# Quick Start: Zotero to Obsidian with ScholarsQuill

## Prerequisites
- Zotero account with API access
- Python 3.8+
- ScholarsQuill installed

## 5-Minute Setup
1. Get Zotero API key
2. Configure ScholarsQuill
3. Run your first batch
4. View in Obsidian

## Example Workflow
...
```

**Configuration Guide**: `docs/guides/configuration.md`
- Environment variables
- Config file format
- Security best practices
- Troubleshooting

**Task 6.2.2: Developer Documentation**

**Architecture Guide**: `docs/architecture/zotero-integration.md`
- Component overview
- Data flow diagrams
- Extension points
- API reference

**Contributing Guide**: `docs/CONTRIBUTING.md`
- Development setup
- Testing requirements
- Code style guide
- PR process

**Task 6.2.3: Reference Documentation**

**API Reference**: Auto-generated from docstrings
```python
# Generate with Sphinx
sphinx-apidoc -o docs/api src/
```

**Field Mapping Table**: `docs/reference/zotero-field-mapping.md`
| Zotero Field | ScholarsQuill Field | Obsidian Property |
|--------------|---------------------|-------------------|
| title | title | title |
| creators | authors, first_author | authors |
| ...

**Task 6.2.4: Tutorial Videos/GIFs**
- Screen recording: First batch process
- GIF: Interactive collection picker
- GIF: Citation network visualization
- GIF: Obsidian integration demo

### Sprint 6.3: Release Preparation

**Task 6.3.1: Version Management**
- Update version in `pyproject.toml`
- Create CHANGELOG entry
- Tag release in git
- Update README badges

**Task 6.3.2: Package Distribution**
- Test PyPI upload process
- Verify installation from PyPI
- Test dependencies resolution
- Create release notes

**Task 6.3.3: Example Projects**
```
examples/
├── zotero-obsidian-workflow/
│   ├── README.md
│   ├── sample-config.yml
│   └── sample-vault/
├── citation-network-analysis/
│   ├── README.md
│   └── example-network.html
└── batch-processing-guide/
    ├── README.md
    └── screenshots/
```

### Phase 6 Deliverables

✅ Test suite with >80% coverage
✅ Performance benchmarks passed
✅ Complete user documentation
✅ Developer documentation
✅ Example projects
✅ Release preparation complete
✅ CHANGELOG.md updated
✅ Package ready for distribution

---

## Testing Strategy

### Unit Tests (>80% Coverage)

**Zotero Client Tests**
```python
# tests/unit/test_zotero_client.py
class TestZoteroClient:
    def test_connection_success(self, mock_api)
    def test_connection_failure(self, mock_api)
    def test_get_item(self, mock_api)
    def test_rate_limiting(self, mock_api)
    def test_retry_logic(self, mock_api)
```

**Metadata Mapper Tests**
```python
# tests/unit/test_zotero_mapper.py
class TestZoteroMetadataMapper:
    def test_map_journal_article(self, sample_item)
    def test_map_book(self, sample_item)
    def test_map_creators(self, sample_creators)
    def test_handle_missing_fields(self, incomplete_item)
    def test_citekey_generation(self, sample_item)
```

**Batch Processor Tests**
```python
# tests/unit/test_batch_processor.py
class TestBatchProcessor:
    def test_chunking(self, large_collection)
    def test_progress_tracking(self, mock_items)
    def test_error_recovery(self, failing_items)
    def test_checkpoint_resume(self, interrupted_batch)
```

### Integration Tests

**Full Workflow Tests**
```python
# tests/integration/test_workflows.py
def test_zotero_to_obsidian_workflow(test_library):
    """Complete workflow from Zotero to Obsidian"""
    client = ZoteroClient.from_test_config()
    processor = ZoteroBatchProcessor(client, output_dir=tmp_dir)
    result = processor.process_collection("test-collection")

    assert result.successful == len(test_items)
    assert all(output_file.exists() for output_file in result.output_files)
    # Verify Obsidian compatibility
    assert validate_obsidian_markdown(result.output_files[0])
```

### Performance Tests

**Benchmarks**
```python
# tests/performance/benchmarks.py
def test_batch_100_items_performance(benchmark):
    """100 items should process in <2 minutes"""
    result = benchmark(process_100_items)
    assert result.duration < timedelta(minutes=2)

def test_memory_usage_1000_items():
    """Memory usage should stay under 500MB"""
    memory_before = get_memory_usage()
    process_1000_items()
    memory_after = get_memory_usage()
    assert (memory_after - memory_before) < 500_000_000  # 500MB
```

### Manual Testing Checklist

- [ ] Connect to real Zotero library
- [ ] Process single item from each item type
- [ ] Batch process collection with 100+ items
- [ ] Test error recovery (disconnect during batch)
- [ ] Verify Obsidian compatibility
- [ ] Test citation network visualization
- [ ] Check all CLI commands work
- [ ] Verify configuration loading
- [ ] Test on macOS, Linux, Windows

---

## Dependencies and Tools

### Required Dependencies
```toml
[project.dependencies]
# Existing
"typer>=0.9.0"
"rich>=13.0.0"
"PyPDF2>=3.0.0"
"pdfplumber>=0.10.0"
"jinja2>=3.1.2"
"networkx>=2.8.0"
"plotly>=5.0.0"

# New
"pyzotero>=1.5.0"           # Zotero API client
"python-dotenv>=1.0.0"      # Environment variable management
"keyring>=24.0.0"           # Secure API key storage (optional)
"pyyaml>=6.0"               # YAML config files
```

### Development Dependencies
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0"
    "pytest-asyncio>=0.21.1"
    "pytest-cov>=4.1.0"
    "pytest-mock>=3.11.1"
    "pytest-benchmark>=4.0.0"
    "responses>=0.23.0"      # Mock HTTP requests
    "black>=23.7.0"
    "mypy>=1.5.0"
]
```

### Tools
- **Version Control**: Git
- **Testing**: pytest, pytest-cov
- **Documentation**: Sphinx, MkDocs
- **Code Quality**: black, mypy, flake8
- **Performance**: pytest-benchmark, memory_profiler

---

## Risk Management

### Technical Risks

**Risk 1: Zotero API Rate Limiting**
- **Likelihood**: Medium
- **Impact**: High (blocks batch processing)
- **Mitigation**:
  - Implement exponential backoff
  - Add caching layer (70% cache hit reduces API calls)
  - Progress checkpointing for resume

**Risk 2: Large Collection Processing Failures**
- **Likelihood**: Medium
- **Impact**: High (user frustration, data loss)
- **Mitigation**:
  - Atomic operations per item
  - Checkpoint after each chunk
  - Resume capability from checkpoint
  - Detailed error logging

**Risk 3: Metadata Mapping Inconsistencies**
- **Likelihood**: Medium
- **Impact**: Medium (poor quality notes)
- **Mitigation**:
  - Extensive testing with all item types
  - Validation layer for all fields
  - Fallback strategies for missing data
  - User feedback loop for improvements

**Risk 4: Obsidian Compatibility Issues**
- **Likelihood**: Low
- **Impact**: Medium (notes don't work in Obsidian)
- **Mitigation**:
  - Follow Obsidian markdown spec strictly
  - Test with actual Obsidian vault
  - Provide example vault template
  - Document known limitations

### External Risks

**Risk 5: Zotero API Changes**
- **Likelihood**: Low
- **Impact**: High (breaks integration)
- **Mitigation**:
  - Pin Pyzotero version
  - Monitor Zotero API announcements
  - Version compatibility testing
  - Graceful degradation

**Risk 6: Breaking Changes in Dependencies**
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**:
  - Pin all dependency versions
  - Regular dependency updates with testing
  - CI/CD pipeline for compatibility checks

---

## Success Metrics

### Quantitative Metrics

**Adoption**:
- 100+ users connect Zotero in first month
- 1000+ collections processed in first quarter
- 10,000+ notes generated in first quarter

**Quality**:
- Test coverage >80%
- Error rate <5% in batch processing
- User-reported bugs <10 per 1000 operations

**Performance**:
- 100 items process in <2 minutes (target: 1.5 min)
- Cache hit rate >70%
- Memory usage <500MB for 1000 items

### Qualitative Metrics

**User Satisfaction**:
- Positive feedback in user surveys (>80% satisfaction)
- Feature requests indicate engagement
- Community contributions and extensions

**Code Quality**:
- Maintainable architecture (subjective review)
- Clear documentation (user feedback)
- Easy to extend (developer feedback)

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 0: Research | 3 days | Architecture design, research docs |
| Phase 1: Core Zotero | 2 weeks | Client, mapper, enhanced templates |
| Phase 2: Batch Processing | 1 week | Batch processor, caching, organization |
| Phase 3: CLI Integration | 1 week | Commands, config, UX improvements |
| Phase 4: Obsidian | 1 week | Writer, formatter, vault template |
| Phase 5: Citation Network | 1 week | Relations, visualization, enhanced citemap |
| Phase 6: Testing & Docs | 1 week | Tests, documentation, release prep |
| **Total** | **6 weeks** | **Complete Zotero-Obsidian integration** |

---

## Next Steps

After completing this implementation plan:

1. **Review and Approval**
   - Technical review by maintainers
   - Security review for API key handling
   - User feedback on proposed workflow

2. **Environment Setup**
   - Set up development environment
   - Create test Zotero library
   - Set up test Obsidian vault

3. **Sprint Planning**
   - Break down tasks into 2-week sprints
   - Assign priorities
   - Set up project board

4. **Begin Phase 0**
   - Start research tasks
   - Create architecture diagrams
   - Write technical specifications

---

**Document Status**: Ready for implementation
**Next Review**: After Phase 0 completion (research and architecture)
**Approval Required**: Project maintainer sign-off before Phase 1
