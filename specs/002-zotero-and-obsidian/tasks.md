# Tasks: Zotero and Obsidian Integration

**Feature Branch**: `002-zotero-and-obsidian`
**Input**: Design documents from `/specs/002-zotero-and-obsidian/`
**Prerequisites**: spec.md (complete), plan.md (template)

## Tech Stack (from existing codebase)
- **Language**: Python 3.8+
- **Dependencies**: pyzotero (NEW), typer, rich, PyPDF2, pdfplumber, jinja2, networkx, plotly
- **Testing**: pytest, pytest-asyncio
- **Structure**: Single project (src/, tests/)

## Path Conventions
- **Source**: `src/zotero/`, `src/obsidian/`, `src/models/`
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/contract/`
- **Templates**: `templates/`
- **Config**: Project root for config files

---

## Phase 3.1: Setup & Dependencies

- [x] **T001** Create Zotero integration module structure
  - Create `src/zotero/__init__.py`
  - Create `src/zotero/client.py` (empty)
  - Create `src/zotero/mapper.py` (empty)
  - Create `src/zotero/batch_processor.py` (empty)
  - Create `src/zotero/cache.py` (empty)

- [x] **T002** Create Obsidian integration module structure
  - Create `src/obsidian/__init__.py`
  - Create `src/obsidian/formatter.py` (empty)
  - Create `src/obsidian/writer.py` (empty)

- [x] **T003** Add pyzotero dependency to pyproject.toml
  - Add `pyzotero>=1.5.0` to dependencies list
  - Run `pip install pyzotero` to verify installation

- [x] **T004** [P] Create configuration schema in `src/models.py`
  - Add `ZoteroConfig` class with fields: library_id, library_type, api_key
  - Add `ObsidianConfig` class with fields: vault_path, use_rest_api, rest_api_port
  - Add `BatchConfig` class with fields: batch_size, checkpoint_interval, cache_ttl

- [x] **T005** [P] Create test directory structure
  - Create `tests/unit/test_zotero_client.py` (empty)
  - Create `tests/unit/test_zotero_mapper.py` (empty)
  - Create `tests/unit/test_zotero_batch_processor.py` (empty)
  - Create `tests/unit/test_obsidian_formatter.py` (empty)
  - Create `tests/integration/test_zotero_integration.py` (empty)
  - Create `tests/integration/test_batch_workflow.py` (empty)

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Zotero Client Tests

- [x] **T006** [P] Unit test for Zotero client connection in `tests/unit/test_zotero_client.py`
  - Test `ZoteroClient.__init__()` with valid credentials
  - Test connection failure with invalid API key
  - Test library type validation (user vs group)
  - Tests MUST fail (no implementation yet)

- [x] **T007** [P] Unit test for fetching items in `tests/unit/test_zotero_client.py`
  - Test `get_items()` returns list of items
  - Test `get_collection_items()` with collection ID
  - Test pagination handling (>100 items)
  - Test rate limit retry logic
  - Tests MUST fail (no implementation yet)

### Metadata Mapping Tests

- [x] **T008** [P] Unit test for Zotero → ScholarsQuill mapping in `tests/unit/test_zotero_mapper.py`
  - Test `map_zotero_item()` for journalArticle type
  - Test mapping for book, conferencePaper, thesis types
  - Test citekey generation from Zotero metadata
  - Test tag preservation
  - Test collection hierarchy mapping
  - Tests MUST fail (no implementation yet)

- [x] **T009** [P] Unit test for citekey collision handling in `tests/unit/test_zotero_mapper.py`
  - Test `generate_citekey()` with unique author/year
  - Test collision detection (same citekey exists)
  - Test numeric suffix appending (smith2023-2, smith2023-3)
  - Tests MUST fail (no implementation yet)

### Batch Processing Tests

- [x] **T010** [P] Unit test for batch processor in `tests/unit/test_zotero_batch_processor.py`
  - Test `process_batch()` with 10 items
  - Test progress tracking callback
  - Test checkpoint creation every N items
  - Test resume from checkpoint after interruption
  - Test summary report generation
  - Tests MUST fail (no implementation yet)

- [x] **T011** [P] Unit test for cache operations in `tests/unit/test_zotero_batch_processor.py`
  - Test cache storage of Zotero items
  - Test cache retrieval (hit scenario)
  - Test cache expiration (24 hour TTL)
  - Test cache invalidation
  - Tests MUST fail (no implementation yet)

### Obsidian Output Tests

- [x] **T012** [P] Unit test for Obsidian formatter in `tests/unit/test_obsidian_formatter.py`
  - Test `format_yaml_frontmatter()` with Zotero metadata
  - Test wikilink generation for note references
  - Test Zotero URL formatting (zotero://select/...)
  - Test tag formatting for Obsidian
  - Test collection folder path generation
  - Tests MUST fail (no implementation yet)

- [x] **T013** [P] Unit test for markdown writer in `tests/unit/test_obsidian_formatter.py`
  - Test `write_note()` creates file with proper structure
  - Test filename conflict handling (duplicate citekeys)
  - Test folder creation for nested collections
  - Tests MUST fail (no implementation yet)

### Integration Tests

- [x] **T014** [P] Integration test for end-to-end workflow in `tests/integration/test_zotero_integration.py`
  - Test: Fetch Zotero item → Map metadata → Generate note → Write file
  - Verify YAML frontmatter correctness
  - Verify file location matches collection structure
  - Tests MUST fail (no implementation yet)

- [x] **T015** [P] Integration test for batch processing in `tests/integration/test_batch_workflow.py`
  - Test: Process collection with 50 items
  - Verify all 50 notes created
  - Verify progress tracking works
  - Verify summary report accuracy
  - Tests MUST fail (no implementation yet)

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Zotero Client Implementation

- [x] **T016** Implement ZoteroClient class in `src/zotero/client.py`
  - Implement `__init__()` with credentials validation
  - Implement connection to Zotero API using pyzotero
  - Implement library type handling (user/group)
  - Add error handling for authentication failures
  - Make T006 tests pass

- [x] **T017** Implement item fetching in `src/zotero/client.py`
  - Implement `get_items()` with pagination support
  - Implement `get_collection_items()` with collection ID
  - Implement rate limit handling with exponential backoff
  - Add retry logic for failed requests
  - Make T007 tests pass

### Metadata Mapping Implementation

- [x] **T018** [P] Implement ZoteroMetadataMapper class in `src/zotero/mapper.py`
  - Implement `map_zotero_item()` for common item types
  - Map Zotero fields to PaperMetadata structure
  - Add type-specific handlers (journalArticle, book, etc.)
  - Preserve tags and collections
  - Make T008 tests pass

- [x] **T019** [P] Implement citekey generation in `src/zotero/mapper.py`
  - Implement `generate_citekey()` using authorYEARkeyword format
  - Implement collision detection logic
  - Implement numeric suffix appending
  - Add warning logging for collisions
  - Make T009 tests pass

- [x] **T020** Extend PaperMetadata in `src/models.py`
  - Add `zotero_key: str` field
  - Add `zotero_url: str` field
  - Add `zotero_tags: List[str]` field
  - Add `zotero_collections: List[str]` field
  - Add `date_added: datetime` field
  - Add `date_modified: datetime` field

### Batch Processing Implementation

- [x] **T021** Implement ZoteroBatchProcessor in `src/zotero/batch_processor.py`
  - Implement `process_batch()` with item iteration
  - Implement progress tracking with callback
  - Implement checkpoint creation logic
  - Implement resume from checkpoint
  - Implement summary report generation
  - Make T010 tests pass

- [x] **T022** Implement caching in `src/zotero/cache.py`
  - Implement cache storage using file-based cache
  - Implement TTL-based expiration (default 24 hours)
  - Implement cache retrieval with hit/miss tracking
  - Implement cache invalidation API
  - Make T011 tests pass

### Obsidian Output Implementation

- [x] **T023** [P] Implement ObsidianFormatter in `src/obsidian/formatter.py`
  - Implement `format_yaml_frontmatter()` with enhanced metadata
  - Implement wikilink generation for cross-references
  - Implement Zotero URL formatting
  - Implement tag formatting for Obsidian syntax
  - Implement collection folder path mapping
  - Make T012 tests pass

- [x] **T024** [P] Implement ObsidianWriter in `src/obsidian/writer.py`
  - Implement `write_note()` with file creation
  - Implement filename conflict resolution
  - Implement nested folder creation for collections
  - Add file write error handling
  - Make T013 tests pass

---

## Phase 3.4: Integration & CLI

- [x] **T025** Integrate Zotero client with batch processor
  - Connect `ZoteroClient.get_collection_items()` to `ZoteroBatchProcessor`
  - Add error handling for API failures during batch
  - Make T015 integration test pass

- [x] **T026** Integrate metadata mapper with Obsidian formatter
  - Connect `ZoteroMetadataMapper.map_zotero_item()` to `ObsidianFormatter`
  - Ensure seamless data flow from Zotero to Obsidian format
  - Make T014 integration test pass

- [x] **T027** Update templates to support Zotero metadata
  - Modify `templates/balanced.md` to include Zotero fields
  - Modify `templates/research.md` to include Zotero fields
  - Modify `templates/theory.md` to include Zotero fields
  - Modify `templates/method.md` to include Zotero fields
  - Modify `templates/review.md` to include Zotero fields
  - Add Zotero URL section
  - Add collection tags section

- [x] **T028** Create CLI command for Zotero sync in slash command
  - Create `.claude/commands/zotero.md` with command definition
  - Add `--collection` flag for specific collection
  - Add `--all` flag for entire library
  - Add `--batch-size` flag for batch configuration
  - Add `--output` flag for output directory
  - Integrate with existing `/note` command workflow

---

## Phase 3.5: Citation Network Enhancement

- [x] **T029** [P] Extend citemap processor in `src/citemap_processor.py`
  - Add `extract_zotero_relations()` method
  - Parse Zotero item relations field
  - Build NetworkX graph from Zotero relationships
  - Make existing citemap tests pass with Zotero data

- [x] **T030** [P] Update citation network visualization
  - Enhance `generate_network_visualization()` with Zotero links
  - Add node metadata from Zotero (tags, collections)
  - Add interactive tooltips with Zotero URLs
  - Color nodes by collection

- [x] **T031** Integrate Zotero citation network with `/citemap` command
  - Modify `.claude/commands/citemap.md` to support Zotero input
  - Add `--zotero-collection` flag
  - Connect to ZoteroClient for relationship extraction

---

## Phase 3.6: Configuration & Error Handling

- [x] **T032** [P] Implement configuration loading
  - Create `src/config.py` module
  - Implement environment variable loading (ZOTERO_API_KEY, etc.)
  - Implement YAML config file loading
  - Add configuration validation
  - Add clear error messages for missing config

- [x] **T033** [P] Add comprehensive error handling
  - Add custom exceptions in `src/exceptions.py`
  - Add `ZoteroAuthenticationError`
  - Add `ZoteroRateLimitError`
  - Add `CitekeyCollisionError`
  - Add `ObsidianWriteError`
  - Update all modules with proper error handling

- [x] **T034** Add logging throughout modules
  - Configure logging in `src/__init__.py`
  - Add INFO logs for progress tracking
  - Add WARNING logs for collisions, retries
  - Add ERROR logs for failures
  - Add DEBUG logs for API calls

---

## Phase 3.7: Documentation & Polish

- [x] **T035** [P] Create user documentation in `docs/ZOTERO_INTEGRATION.md`
  - Document Zotero API key generation
  - Document configuration options
  - Document CLI commands and flags
  - Document batch processing workflow
  - Add troubleshooting section

- [x] **T036** [P] Create developer documentation in `docs/ZOTERO_ARCHITECTURE.md`
  - Document module architecture
  - Document data flow diagrams
  - Document API contracts
  - Document extension points

- [x] **T037** [P] Update main README.md
  - Add Zotero integration section
  - Add installation instructions for pyzotero
  - Add quick start example with Zotero
  - Update feature list

- [x] **T038** Add performance tests in `tests/performance/`
  - Test batch processing of 100 items (< 2 minutes)
  - Test cache hit ratio (> 70%)
  - Test API rate limit compliance
  - Test memory usage during large batches

- [x] **T039** Code cleanup and refactoring
  - Remove code duplication
  - Add type hints to all functions
  - Run black formatter
  - Run mypy type checker
  - Run pytest with coverage (target >80%)

---

## Dependencies

**Setup Phase (T001-T005)**: Must complete before tests
**Test Phase (T006-T015)**: Must complete before implementation
**Implementation Phase (T016-T024)**:
- T020 blocks T018, T019 (extends PaperMetadata)
- T016, T017 block T021 (client needed for batch processor)
- T018, T019 block T023, T024 (mapper needed for formatter)

**Integration Phase (T025-T028)**:
- T025 depends on T017, T021
- T026 depends on T019, T023
- T027 can run in parallel
- T028 depends on T025, T026

**Citation Network (T029-T031)**:
- T029 depends on T016, T017
- T030 depends on T029
- T031 depends on T030

**Polish Phase (T032-T039)**: Can run after T028

---

## Parallel Execution Examples

### Setup Phase (T001, T002 sequential, then parallel)
```bash
# T001 and T002 first (create directories)
# Then parallel:
Task: "Add pyzotero dependency to pyproject.toml and install" (T003)
Task: "Create configuration schema in src/models.py" (T004)
Task: "Create test directory structure" (T005)
```

### Test Phase (All parallel - different files)
```bash
Task: "Unit test for Zotero client connection in tests/unit/test_zotero_client.py" (T006)
Task: "Unit test for fetching items in tests/unit/test_zotero_client.py" (T007)
Task: "Unit test for Zotero → ScholarsQuill mapping in tests/unit/test_zotero_mapper.py" (T008)
Task: "Unit test for citekey collision handling in tests/unit/test_zotero_mapper.py" (T009)
Task: "Unit test for batch processor in tests/unit/test_zotero_batch_processor.py" (T010)
Task: "Unit test for cache operations in tests/unit/test_zotero_batch_processor.py" (T011)
Task: "Unit test for Obsidian formatter in tests/unit/test_obsidian_formatter.py" (T012)
Task: "Unit test for markdown writer in tests/unit/test_obsidian_formatter.py" (T013)
Task: "Integration test for end-to-end workflow in tests/integration/test_zotero_integration.py" (T014)
Task: "Integration test for batch processing in tests/integration/test_batch_workflow.py" (T015)
```

### Implementation Phase (Parallel groups)
```bash
# Group 1 (After T020):
Task: "Implement ZoteroMetadataMapper class in src/zotero/mapper.py" (T018)
Task: "Implement citekey generation in src/zotero/mapper.py" (T019)
Task: "Implement ObsidianFormatter in src/obsidian/formatter.py" (T023)
Task: "Implement ObsidianWriter in src/obsidian/writer.py" (T024)

# Group 2 (After T016, T017):
Task: "Implement ZoteroBatchProcessor in src/zotero/batch_processor.py" (T021)
Task: "Implement caching in src/zotero/cache.py" (T022)
```

### Documentation Phase (All parallel)
```bash
Task: "Create user documentation in docs/ZOTERO_INTEGRATION.md" (T035)
Task: "Create developer documentation in docs/ZOTERO_ARCHITECTURE.md" (T036)
Task: "Update main README.md" (T037)
```

---

## Validation Checklist

- [x] All key entities have implementation tasks (Zotero Item, Collection, Enhanced Metadata, Literature Note, Citation Relationship, Batch Job)
- [x] All functional requirements covered (FR-001 through FR-038)
- [x] Tests come before implementation (TDD)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] Dependencies documented and enforced
- [x] Estimated 39 tasks matches scope (setup + tests + implementation + integration + polish)

---

## Notes

- **[P]** indicates tasks that can run in parallel (different files, no dependencies)
- Verify all tests fail before implementing corresponding features
- Commit after completing each task
- Run full test suite after each implementation task
- Update progress tracking in plan.md after major phases