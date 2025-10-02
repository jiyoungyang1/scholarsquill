# Feature Specification: Zotero and Obsidian Integration for ScholarsQuill

**Feature ID**: ZSOI-001
**Status**: Draft
**Created**: 2025-10-02
**Author**: AI Assistant based on user requirements
**Priority**: High

---

## 1. Overview

### 1.1 Feature Summary

Integrate ScholarsQuill with Zotero and Obsidian to enable:
- Automated extraction of metadata from Zotero libraries
- Batch processing of Zotero collections into literature notes
- Bidirectional synchronization between Zotero and Obsidian
- Enhanced metadata mapping preserving Zotero tags, collections, and relations
- Citation network visualization using Zotero citation data

### 1.2 Problem Statement

Current ScholarsQuill implementation:
- Requires manual PDF file handling
- Extracts metadata from PDFs only (messy, unreliable)
- No integration with existing reference managers
- Lacks batch processing from organized collections
- No bidirectional workflow with note-taking systems

Users need:
- Seamless workflow from Zotero library to Obsidian notes
- Preserve existing Zotero organization (collections, tags)
- Batch processing of entire collections
- Clickable links between systems
- Automated metadata extraction from Zotero's clean data

### 1.3 Success Criteria

**Must Have**:
- Fetch items from Zotero library using Pyzotero API
- Map Zotero metadata to ScholarsQuill PaperMetadata structure
- Generate Obsidian-compatible markdown notes with YAML frontmatter
- Support batch processing of Zotero collections
- Preserve Zotero tags and collection organization

**Should Have**:
- Bidirectional links (Zotero → Obsidian → Zotero)
- Citation network from Zotero relations
- PDF attachment handling from Zotero storage
- Progress tracking for batch operations

**Nice to Have**:
- Obsidian Local REST API integration for direct note creation
- Automatic collection → folder mapping
- Watch mode for real-time Zotero sync

---

## 2. Requirements

### 2.1 Functional Requirements

**FR-1: Zotero Connection**
- Connect to Zotero library using library ID, library type, and API key
- Support both user and group libraries
- Validate connection and permissions

**FR-2: Metadata Extraction from Zotero**
- Fetch items with complete metadata (title, authors, year, DOI, etc.)
- Extract Zotero-specific data (item key, collections, tags, relations)
- Map to ScholarsQuill PaperMetadata structure
- Handle all Zotero item types (journalArticle, book, conferencePaper, etc.)

**FR-3: Batch Collection Processing**
- List all user collections
- Fetch all items from selected collection(s)
- Process items in chunks (50-item API limit)
- Generate literature notes for each item
- Organize output by collection structure

**FR-4: Enhanced Metadata Mapping**
- Include Zotero key for bidirectional linking
- Preserve Zotero tags in YAML frontmatter
- Map Zotero collections to folders/tags
- Store Zotero URL for click-through access
- Include date_added and date_modified timestamps

**FR-5: PDF Attachment Handling**
- Detect if Zotero item has PDF attachment
- Download PDF from Zotero storage (optional)
- Link to existing local PDF path
- Fall back to ScholarsQuill PDF extraction if needed

**FR-6: Obsidian Integration**
- Generate markdown files with Obsidian-compatible YAML frontmatter
- Use `[[wikilink]]` syntax for internal linking
- Support Obsidian properties (aliases, tags, cssclasses)
- Create folder structure matching Zotero collections
- Optional: Use Obsidian Local REST API for direct vault manipulation

**FR-7: Citation Network Enhancement**
- Extract Zotero item relations for citation mapping
- Build citation network from Zotero data
- Enhance existing `/citemap` with Zotero relationship data
- Generate interactive visualizations with Zotero context

### 2.2 Non-Functional Requirements

**NFR-1: Performance**
- Process 50 items per API call (Zotero limit)
- Handle collections with 1000+ items efficiently
- Rate limiting compliance with Zotero API
- Parallel processing where possible

**NFR-2: Reliability**
- Handle API failures gracefully with retry logic
- Validate all Zotero metadata before processing
- Atomic operations for batch processing
- Progress saving for large collections

**NFR-3: Security**
- Secure API key storage (environment variables or keyring)
- Read-only Zotero access by default
- No hardcoded credentials
- HTTPS for all Zotero API calls

**NFR-4: Usability**
- Simple configuration (library ID, API key)
- Clear progress indicators for batch operations
- Informative error messages
- Dry-run mode for preview

**NFR-5: Compatibility**
- Python 3.8+ (ScholarsQuill requirement)
- Pyzotero library for Zotero API
- Compatible with existing ScholarsQuill templates
- Obsidian markdown format compliance

---

## 3. Technical Design

### 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  ScholarsQuill CLI                  │
│                 (/note, /citemap)                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              Zotero Integration Layer               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Zotero API   │  │ Metadata     │  │ Batch     │ │
│  │ Client       │  │ Mapper       │  │ Processor │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│            Existing ScholarsQuill Core              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Template     │  │ Note         │  │ Citemap   │ │
│  │ Engine       │  │ Generator    │  │ Processor │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                 Obsidian Vault                      │
│     (Markdown files with YAML frontmatter)          │
└─────────────────────────────────────────────────────┘
```

### 3.2 Component Design

**Component 1: ZoteroClient**
- Wraps Pyzotero library
- Handles authentication and connection
- Provides high-level methods for common operations
- Implements caching and rate limiting

**Component 2: ZoteroMetadataMapper**
- Maps Zotero item to PaperMetadata
- Handles creator name formatting
- Extracts and validates all metadata fields
- Generates enhanced YAML frontmatter

**Component 3: ZoteroBatchProcessor**
- Processes collections in chunks
- Manages progress tracking
- Handles errors and retries
- Generates organized output structure

**Component 4: ObsidianWriter**
- Writes markdown files with Obsidian format
- Creates folder structure
- Manages file naming and deduplication
- Optional: REST API integration

### 3.3 Data Models

**ZoteroConfig**
```python
@dataclass
class ZoteroConfig:
    library_id: str
    library_type: str  # 'user' or 'group'
    api_key: str
    cache_dir: Optional[Path] = None
    rate_limit_delay: float = 0.5  # seconds between requests
```

**EnhancedPaperMetadata** (extends existing PaperMetadata)
```python
@dataclass
class EnhancedPaperMetadata(PaperMetadata):
    # Existing fields from PaperMetadata
    # title, first_author, authors, year, citekey, doi, etc.

    # New Zotero-specific fields
    zotero_key: Optional[str] = None
    zotero_url: Optional[str] = None
    zotero_tags: List[str] = field(default_factory=list)
    zotero_collections: List[str] = field(default_factory=list)
    zotero_relations: Dict[str, List[str]] = field(default_factory=dict)
    date_added: Optional[str] = None
    date_modified: Optional[str] = None
    item_url: Optional[str] = None
    abstract: Optional[str] = None
```

### 3.4 API Design

**CLI Commands**

New `/zotero-note` command:
```bash
/zotero-note <collection_name> --focus research --depth standard --output obsidian-vault/
/zotero-note --all --batch --output literature-notes/
/zotero-note --item-key ABC123 --focus balanced
```

Enhanced `/note` command with Zotero support:
```bash
/note --zotero <item_key> --focus research
/note paper.pdf --enrich-from-zotero  # Enhance PDF metadata with Zotero
```

**Python API**

```python
from scholarsquill.zotero import ZoteroClient, ZoteroBatchProcessor

# Initialize client
client = ZoteroClient(
    library_id="12345",
    library_type="user",
    api_key="API_KEY_HERE"
)

# Batch process collection
processor = ZoteroBatchProcessor(client)
results = processor.process_collection(
    collection_name="Machine Learning Papers",
    output_dir="obsidian-vault/literature",
    template_focus="research",
    depth="standard"
)

# Process single item
item = client.get_item("ABC123")
metadata = client.map_to_metadata(item)
note = generator.generate_note(metadata)
```

### 3.5 Database/Storage Design

**Zotero Cache Structure**
```
.scholarsquill/cache/zotero/
├── items/
│   ├── ABC123.json          # Cached item data
│   └── DEF456.json
├── collections/
│   ├── COL001.json          # Collection metadata
│   └── COL002.json
├── attachments/
│   └── ABC123_attachment.pdf
└── index.json               # Cache index with timestamps
```

**Obsidian Vault Organization**
```
obsidian-vault/
├── literature-notes/
│   ├── machine-learning/           # Zotero collection
│   │   ├── smith2023neural.md
│   │   └── jones2024deep.md
│   └── neural-networks/            # Another collection
│       └── brown2022transformer.md
├── citemap-analysis/
│   └── smith2023neural_citemap.md
└── .scholarsquill/
    └── zotero-sync.json            # Sync state
```

---

## 4. Implementation Plan

### 4.1 Phase 1: Core Zotero Integration (Week 1-2)

**Tasks**:
1. Install and configure Pyzotero dependency
2. Implement ZoteroClient wrapper
3. Implement ZoteroMetadataMapper
4. Create enhanced YAML frontmatter templates
5. Update existing templates to support Zotero fields
6. Write unit tests for Zotero components

**Deliverables**:
- `src/zotero_client.py` - Zotero API client
- `src/zotero_mapper.py` - Metadata mapping
- Updated template files with Zotero frontmatter
- Unit tests with >80% coverage

### 4.2 Phase 2: Batch Processing (Week 3)

**Tasks**:
1. Implement ZoteroBatchProcessor
2. Add progress tracking and logging
3. Implement error handling and retry logic
4. Create collection → folder mapping
5. Add caching layer for performance
6. Integration tests for batch processing

**Deliverables**:
- `src/zotero_batch.py` - Batch processor
- Progress indicators and logging
- Integration tests
- Performance benchmarks

### 4.3 Phase 3: CLI Integration (Week 4)

**Tasks**:
1. Create `/zotero-note` slash command
2. Update existing `/note` command with Zotero support
3. Add configuration management (API keys, etc.)
4. Create interactive collection picker
5. Add dry-run and preview modes
6. Update documentation

**Deliverables**:
- `.claude/commands/zotero-note.md`
- Updated CLI interface
- Configuration templates
- User documentation

### 4.4 Phase 4: Obsidian Enhancement (Week 5)

**Tasks**:
1. Implement Obsidian-specific formatting
2. Add wikilink generation for citations
3. Create folder structure automation
4. Optional: Obsidian Local REST API integration
5. Add Obsidian plugin compatibility features
6. Create example vault structure

**Deliverables**:
- `src/obsidian_writer.py`
- Obsidian formatting utilities
- Example vault template
- Integration guide

### 4.5 Phase 5: Citation Network Integration (Week 6)

**Tasks**:
1. Extract Zotero item relations
2. Enhance `/citemap` with Zotero data
3. Build citation network from Zotero
4. Create interactive visualization
5. Add cross-reference features
6. End-to-end testing

**Deliverables**:
- Enhanced citemap processor
- Zotero citation network support
- Interactive visualizations
- Complete integration tests

---

## 5. Testing Strategy

### 5.1 Unit Tests

**Zotero Client Tests**:
- Connection and authentication
- API request/response handling
- Error handling and retries
- Caching mechanisms

**Metadata Mapper Tests**:
- All Zotero item types
- Edge cases (missing fields, special characters)
- Author name formatting
- Citekey generation from Zotero data

**Batch Processor Tests**:
- Collection fetching
- Chunking and pagination
- Progress tracking
- Error recovery

### 5.2 Integration Tests

- End-to-end: Zotero → ScholarsQuill → Obsidian
- Batch processing of real collections
- PDF attachment handling
- Citation network generation

### 5.3 Manual Testing

- Test with real Zotero libraries
- Verify Obsidian compatibility
- Check link functionality
- Validate folder organization

---

## 6. Documentation

### 6.1 User Documentation

**Getting Started Guide**:
- Setting up Zotero API access
- Configuring ScholarsQuill with Zotero
- First batch processing workflow
- Obsidian vault setup

**Reference Documentation**:
- Command reference for `/zotero-note`
- Configuration options
- Metadata field mapping table
- Troubleshooting guide

**Tutorial**:
- "From Zotero Library to Obsidian Vault in 5 Minutes"
- "Building Citation Networks from Zotero"
- "Advanced Batch Processing Workflows"

### 6.2 Developer Documentation

- Zotero API integration architecture
- Adding new Zotero item types
- Custom metadata mappers
- Extending batch processors

---

## 7. Dependencies

### 7.1 New Dependencies

```toml
[project]
dependencies = [
    # Existing dependencies...
    "pyzotero>=1.5.0",          # Zotero API client
]

[project.optional-dependencies]
obsidian = [
    "requests>=2.31.0",          # For Obsidian Local REST API
]
```

### 7.2 External Services

- **Zotero API**: Web API v3, rate limits apply
- **Obsidian Local REST API** (optional): Local HTTPS API

---

## 8. Security Considerations

### 8.1 API Key Management

- Store API keys in environment variables (`ZOTERO_API_KEY`)
- Support keyring/keychain for secure storage
- Never log or print API keys
- Clear instructions for key generation

### 8.2 Data Privacy

- All Zotero data is user's own library
- No external data transmission except Zotero API
- Local caching with user consent
- Option to disable caching

### 8.3 File System Access

- Write only to specified output directories
- Validate all file paths
- No deletion of existing files without confirmation

---

## 9. Performance Considerations

### 9.1 Optimization Strategies

- **Batch API Calls**: 50 items per request (Zotero limit)
- **Caching**: Cache Zotero items to reduce API calls
- **Parallel Processing**: Process notes in parallel
- **Progressive Loading**: Stream results for large collections

### 9.2 Performance Targets

- Fetch 100 items: < 30 seconds
- Generate 100 notes: < 2 minutes
- Build citation network (100 papers): < 1 minute
- Memory usage: < 500MB for 1000 items

---

## 10. Future Enhancements

### 10.1 Potential Features

**Version 2.0**:
- Real-time Zotero sync with watch mode
- Automatic note updates when Zotero items change
- Two-way sync (Obsidian → Zotero)
- Support for Zotero annotations and highlights

**Version 3.0**:
- Group library collaboration features
- Advanced citation network analysis
- Integration with other reference managers (Mendeley, EndNote)
- Web interface for batch processing

### 10.2 Research Areas

- AI-powered metadata enrichment from Zotero abstracts
- Automatic tag generation from paper content
- Smart collection suggestions based on research interests
- Cross-vault citation network analysis

---

## 11. Success Metrics

### 11.1 Adoption Metrics

- Number of users connecting Zotero accounts
- Average batch processing size
- Collections processed per user
- Notes generated per month

### 11.2 Quality Metrics

- Metadata mapping accuracy (>95%)
- Error rate in batch processing (<5%)
- User-reported issues per 1000 operations
- Test coverage (>80%)

### 11.3 Performance Metrics

- API call efficiency (minimize redundant calls)
- Average processing time per item
- Cache hit rate
- User satisfaction (surveys/feedback)

---

## 12. Risks and Mitigations

### 12.1 Technical Risks

**Risk**: Zotero API rate limiting
- **Mitigation**: Implement exponential backoff and caching

**Risk**: Large collection processing failures
- **Mitigation**: Checkpoint/resume capability, atomic operations

**Risk**: Metadata mapping inconsistencies
- **Mitigation**: Extensive testing, validation layer, fallback strategies

### 12.2 External Risks

**Risk**: Zotero API changes
- **Mitigation**: Version pinning, monitoring API announcements

**Risk**: Obsidian format changes
- **Mitigation**: Follow Obsidian standard markdown, minimal custom features

---

## 13. Acceptance Criteria

### 13.1 Must Pass

✅ Connect to Zotero library with valid credentials
✅ Fetch and map metadata for all supported item types
✅ Batch process collection with 100+ items successfully
✅ Generate Obsidian-compatible notes with complete metadata
✅ Preserve Zotero tags and collections
✅ Create bidirectional links (Zotero ↔ Obsidian)
✅ Handle errors gracefully with informative messages
✅ Pass all unit and integration tests
✅ Documentation complete and accurate

### 13.2 Performance Requirements

✅ Process 50 items in < 30 seconds
✅ Memory usage < 500MB for 1000 items
✅ Cache reduces redundant API calls by >70%
✅ Error recovery succeeds in >95% of failures

---

## 14. Approval

**Specification Review**: Pending
**Technical Review**: Pending
**Security Review**: Pending
**Final Approval**: Pending

---

**Document Version**: 1.0
**Last Updated**: 2025-10-02
**Next Review**: After Phase 1 completion
