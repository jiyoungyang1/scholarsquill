# Feature Specification: Zotero and Obsidian Integration

**Feature Branch**: `002-zotero-and-obsidian`
**Created**: 2025-10-02
**Status**: Draft
**Input**: User description: "Zotero and Obsidian integration with metadata mapping, batch processing, and bidirectional sync"

## User Scenarios & Testing

### Primary User Story

As a researcher using Zotero for reference management and Obsidian for note-taking, I want to automatically generate literature notes from my Zotero library so that I can maintain a connected knowledge base without manual data entry.

**Current Workflow (Manual)**:
1. User reads PDF in Zotero
2. User manually creates note in Obsidian
3. User manually copies metadata (authors, year, title, DOI)
4. User manually types literature summary
5. User manually manages tags and collections
6. Repeat for every paper (time-consuming, error-prone)

**Desired Workflow (Automated)**:
1. User selects Zotero collection or item
2. ScholarsQuill fetches metadata from Zotero
3. ScholarsQuill generates structured literature notes
4. Notes appear in Obsidian with proper metadata, tags, and links
5. User can navigate between Zotero and Obsidian seamlessly

### Acceptance Scenarios

1. **Given** a Zotero library with 50 papers in a "Machine Learning" collection, **When** user runs batch processing, **Then** 50 literature notes are created in Obsidian with complete metadata
2. **Given** a Zotero item with tags "deep-learning" and "neural-networks", **When** note is generated, **Then** Obsidian note includes these tags in YAML frontmatter
3. **Given** a generated Obsidian note, **When** user clicks Zotero link in the note, **Then** the corresponding item opens in Zotero
4. **Given** multiple papers citing each other in Zotero, **When** citation network is generated, **Then** an interactive visualization shows the relationships
5. **Given** a Zotero item with attached PDF, **When** note is generated, **Then** note links to the PDF for easy access

### Edge Cases

- What happens when Zotero item has no DOI? → Use alternative identifiers or generate from metadata
- What happens when citekey collision occurs (same author/year)? → Append disambiguator
- How does system handle interrupted batch processing (500 items)? → Resume from checkpoint
- What happens when Zotero API rate limit is hit? → Implement exponential backoff and retry
- How does system handle missing author information? → Mark as "Unknown" with warning
- What happens when Obsidian vault doesn't exist? → Create folder structure automatically

## Requirements

### Functional Requirements

**Zotero Integration**:
- **FR-001**: System MUST connect to Zotero library using user credentials (library ID, library type, API key)
- **FR-002**: System MUST fetch item metadata including title, authors, year, DOI, abstract, tags, and collections
- **FR-003**: System MUST support both user libraries and group libraries
- **FR-004**: System MUST retrieve items from specific collections
- **FR-005**: System MUST retrieve all items from a library
- **FR-006**: System MUST handle Zotero API pagination for large collections (>100 items)
- **FR-007**: System MUST respect Zotero API rate limits and implement retry logic

**Metadata Mapping**:
- **FR-008**: System MUST map Zotero item fields to ScholarsQuill metadata structure
- **FR-009**: System MUST generate citekeys in authorYEARkeyword format
- **FR-010**: System MUST preserve Zotero tags in output notes
- **FR-011**: System MUST preserve Zotero collection organization
- **FR-012**: System MUST create bidirectional links (Zotero URL in notes, notes reference Zotero key)
- **FR-013**: System MUST handle all common Zotero item types (journalArticle, book, conferencePaper, thesis, etc.)
- **FR-014**: System MUST include Zotero modification dates for sync tracking

**Batch Processing**:
- **FR-015**: System MUST process multiple items in a single batch operation
- **FR-016**: System MUST show progress indicator during batch processing
- **FR-017**: System MUST save checkpoints during batch processing for error recovery
- **FR-018**: System MUST allow resuming interrupted batch operations
- **FR-019**: System MUST report success/failure status for each processed item
- **FR-020**: System MUST generate summary report after batch completion

**Obsidian Output**:
- **FR-021**: System MUST generate markdown files with Obsidian-compatible YAML frontmatter
- **FR-022**: System MUST use wikilink syntax for internal note references
- **FR-023**: System MUST organize output files by Zotero collections (folders)
- **FR-024**: System MUST handle filename conflicts (duplicate citekeys)
- **FR-025**: System MUST include clickable Zotero URLs for opening items in Zotero
- **FR-026**: System MUST format tags in Obsidian-compatible syntax

**Citation Network Enhancement**:
- **FR-027**: System MUST extract citation relationships from Zotero item relations
- **FR-028**: System MUST build citation network graph from Zotero data
- **FR-029**: System MUST generate interactive citation network visualization
- **FR-030**: System MUST enhance existing citemap feature with Zotero relationships

**User Configuration**:
- **FR-031**: System MUST support configuration via environment variables
- **FR-032**: System MUST support configuration via YAML config file
- **FR-033**: System MUST validate configuration before processing
- **FR-034**: System MUST provide clear error messages for configuration issues

**Performance & Reliability**:
- **FR-035**: System MUST process at least 50 items per API call (Zotero batch limit)
- **FR-036**: System MUST complete processing of 100 items within 2 minutes
- **FR-037**: System MUST cache Zotero data to reduce redundant API calls
- **FR-038**: System MUST use secure API key storage (environment variables or keyring)

### Key Entities

- **Zotero Item**: Represents a bibliographic entry in Zotero with metadata (title, authors, year, DOI, abstract, tags, collections, relations, attachments)
- **Zotero Collection**: Represents a folder/grouping of items in Zotero with name and hierarchy
- **Enhanced Paper Metadata**: ScholarsQuill metadata structure extended with Zotero-specific fields (zotero_key, zotero_url, zotero_tags, zotero_collections, date_added, date_modified)
- **Literature Note**: Markdown file generated by ScholarsQuill with YAML frontmatter and structured content
- **Citation Relationship**: Link between two papers representing citation/reference relationship
- **Batch Processing Job**: Collection of items to be processed together with progress tracking and checkpoint data

## Clarifications

### Session 1: 2025-10-02 (Initial Requirements Gathering)

**Q1: What Zotero item types should be supported initially?**
A: Support the most common academic item types: journalArticle, book, bookSection, conferencePaper, thesis, report. Other types can use a generic handler.

**Q2: How should the system handle Zotero items without PDFs?**
A: Generate notes with metadata only. Include note in frontmatter indicating PDF status. User can add PDF later.

**Q3: Should the system support two-way sync (Obsidian → Zotero)?**
A: Not in initial version. Focus on one-way: Zotero → ScholarsQuill → Obsidian. Two-way sync is a future enhancement.

**Q4: How should citekey collisions be handled?**
A: Append numeric suffix (e.g., smith2023neural, smith2023neural-2, smith2023neural-3). Include warning in processing report.

**Q5: Should Obsidian Local REST API be used for direct note creation?**
A: Optional feature. Default to file-based approach (write markdown files). REST API can be enabled via configuration for users who want it.

**Q6: What level of caching is needed?**
A: Cache Zotero items for 24 hours by default. Allow cache invalidation and TTL configuration. Cache should reduce API calls by >70% for repeated operations.

**Q7: How should collection hierarchy be represented in Obsidian?**
A: Map to folder structure. Top-level collection → top-level folder. Nested collections → nested folders. Preserve full hierarchy.

**Q8: Should the system auto-update notes when Zotero items change?**
A: Not in initial version. Focus on initial generation. Auto-sync/update is a future enhancement requiring change detection.

**Q9: What citation network analysis features are needed?**
A: Extract Zotero relations, build NetworkX graph, calculate centrality measures, identify key papers, generate interactive Plotly visualization. Integrate with existing `/citemap` command.

**Q10: How should API authentication be secured?**
A: Support environment variables (ZOTERO_API_KEY) as primary method. Optional keyring/keychain integration for enhanced security. Never store in config files. Clear documentation on key generation.

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain (all clarified in session 1)
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked and resolved
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
