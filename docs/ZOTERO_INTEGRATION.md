# Zotero Integration Guide

Complete guide for integrating ScholarsQuill with Zotero and Obsidian.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Features](#features)
- [Metadata Mapping](#metadata-mapping)
- [Batch Processing](#batch-processing)
- [Troubleshooting](#troubleshooting)

## Overview

ScholarsQuill's Zotero integration allows you to automatically sync your Zotero library to Obsidian with full metadata mapping, batch processing, and bidirectional linking.

**What it does:**
- Fetches items from Zotero via API
- Maps metadata (authors, year, DOI, tags, collections) to ScholarsQuill format
- Generates structured literature notes using templates
- Creates Obsidian-compatible markdown with YAML frontmatter
- Organizes notes by Zotero collection hierarchy
- Handles large batches with progress tracking and checkpoints

## Prerequisites

1. **Zotero Account** with library (user or group)
2. **Zotero API Key** with read permissions
3. **Python 3.8+** with pyzotero installed
4. **Obsidian Vault** (optional, can write to any directory)

## Setup

### Step 1: Get Zotero Credentials

#### Find Your Library ID

1. Log in to [Zotero.org](https://www.zotero.org/)
2. Go to **Settings → Feeds/API**
3. Your **Library ID** is shown at the top (e.g., `1234567`)
4. Note your **Library Type**:
   - `user` for personal library
   - `group` for group library

#### Generate API Key

1. Go to [https://www.zotero.org/settings/keys/new](https://www.zotero.org/settings/keys/new)
2. Enter a descriptive name (e.g., "ScholarsQuill Integration")
3. Set permissions:
   - **Personal Library**: Check "Allow library access" → "Read Only"
   - **Group Library**: Select specific groups
4. Click **Save Key**
5. **Copy the API key immediately** (it won't be shown again)

### Step 2: Configure Credentials

#### Option A: Environment Variables (Recommended)

```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.bash_profile
export ZOTERO_LIBRARY_ID=1234567
export ZOTERO_LIBRARY_TYPE=user
export ZOTERO_API_KEY=your_api_key_here

# Reload shell
source ~/.zshrc
```

#### Option B: Configuration File

Create `zotero_config.yml` in project root:

```yaml
zotero:
  library_id: "1234567"
  library_type: "user"  # or "group"
  api_key: "your_api_key_here"

obsidian:
  vault_path: "~/Documents/Obsidian/Vault"
  create_folders: true
  use_rest_api: false

batch:
  batch_size: 50
  checkpoint_interval: 10
  cache_ttl: 86400  # 24 hours
```

### Step 3: Install pyzotero

```bash
pip install pyzotero>=1.5.0
```

### Step 4: Verify Setup

```bash
# Test connection (in Claude Code)
/zotero --limit 1
```

If successful, you should see 1 item processed.

## Usage

### Basic Commands

#### Process Specific Collection

```bash
/zotero --collection ABC123 --template research
```

**Output**: Notes in `obsidian_vault/` organized by collection

#### Process Entire Library

```bash
/zotero --all --limit 100 --template balanced
```

**Output**: First 100 items from library

#### Process Single Item

```bash
/zotero --item XYZ789 --template theory
```

**Output**: Single note for specified item

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--collection <id>` | Process specific collection | - |
| `--all` | Process entire library | - |
| `--item <key>` | Process single item | - |
| `--limit <n>` | Limit number of items | None (all) |
| `--template <name>` | Template choice | `balanced` |
| `--output <path>` | Output directory | `./obsidian_vault` |

### Template Choices

- **balanced**: Comprehensive coverage of all aspects
- **research**: Focus on methodology and findings
- **theory**: Emphasis on theoretical contributions
- **method**: Deep dive into methodology
- **review**: Literature review and synthesis

## Features

### Metadata Mapping

Zotero fields automatically mapped to ScholarsQuill metadata:

| Zotero Field | ScholarsQuill Field | Notes |
|--------------|---------------------|-------|
| `title` | `title` | Direct mapping |
| `creators` | `authors`, `first_author` | Formatted as "Last, First" |
| `date` | `year` | Extracted as integer |
| `DOI` | `doi` | Direct mapping |
| `publicationTitle` | `journal` | For articles |
| `volume`, `issue`, `pages` | `volume`, `issue`, `pages` | Direct mapping |
| `abstractNote` | `abstract` | Direct mapping |
| `tags` | `zotero_tags` | Array of tag strings |
| `collections` | `zotero_collections` | Collection names |
| `key` | `zotero_key` | Zotero item key |
| `dateAdded`, `dateModified` | `date_added`, `date_modified` | ISO format |

### Citekey Generation

Format: `authorYEARkeyword`

**Examples:**
- `smith2023machine` (Smith, 2023, "Machine Learning...")
- `doe2022neural` (Doe, 2022, "Neural Networks...")
- `chen2024deep-2` (collision handled with suffix)

**Collision Handling:**
- First occurrence: `smith2023machine`
- Second: `smith2023machine-2`
- Third: `smith2023machine-3`

### Obsidian YAML Frontmatter

```yaml
---
title: Machine Learning for Protein Stability
citekey: smith2023machine
authors:
  - Smith, John
  - Doe, Jane
year: 2023
journal: Nature
volume: 42
pages: 123-145
doi: 10.1234/example
item_type: journalArticle
zotero_key: ABC123
zotero_url: zotero://select/library/items/ABC123
tags:
  - machine-learning
  - protein-stability
collections:
  - Machine Learning
  - Protein Science
date_added: 2024-01-15T10:00:00Z
date_modified: 2024-01-20T15:30:00Z
---
```

### Bidirectional Linking

**In Obsidian Note:**
```markdown
**Zotero**: [Open in Zotero](zotero://select/library/items/ABC123)
```

Clicking this link opens the item in Zotero desktop app.

**In Zotero:**
Store Obsidian note path in Zotero "Notes" or "Extra" field for reverse linking.

## Batch Processing

### Progress Tracking

```
Processing Zotero Collection: Machine Learning Papers
========================================================
Progress: [████████████████████░░░░] 80% (40/50 items)

Current: smith2023machine.md
Elapsed: 1m 23s
Remaining: ~21s
```

### Checkpoints

Checkpoints saved every 10 items (configurable):

```bash
# Resume from checkpoint if interrupted
/zotero --collection ABC123 --resume
```

**Checkpoint Location:** `./checkpoints/collection_ABC123_40.json`

### Caching

**Benefits:**
- Reduces API calls by 70%+
- Faster re-processing of same items
- Automatic cache expiration (24 hours)

**Cache Location:** `./.zotero_cache/`

**Clear Cache:**
```bash
rm -rf .zotero_cache/
```

### Performance

**Typical Rates:**
- 50 items: ~1-2 minutes
- 100 items: ~2-3 minutes
- 500 items: ~10-15 minutes

**Optimizations:**
- Batch size: 50 items per API request (Zotero limit)
- Parallel processing where possible
- Smart caching to minimize API calls
- Checkpoint intervals: Every 10 items

## Troubleshooting

### Invalid API Key

**Error:** `ZoteroAuthenticationError: Invalid API credentials`

**Solutions:**
1. Verify API key is correct (check for trailing spaces)
2. Ensure API key has "Read Only" permissions
3. Check library ID and type are correct
4. Regenerate API key if needed

### Rate Limit Exceeded

**Error:** `ZoteroRateLimitError: Rate limit exceeded after 3 retries`

**Solutions:**
1. Wait a few minutes and try again
2. Reduce batch size: `--limit 25`
3. System automatically retries with exponential backoff

### Collection Not Found

**Error:** `Failed to fetch collection: Collection ABC123 not found`

**Solutions:**
1. Verify collection ID is correct
2. Check collection access permissions
3. List collections: `/zotero --list-collections`

### Missing Items

**Problem:** Some items not processed

**Causes:**
- Item type not supported (e.g., attachments, notes)
- Missing required fields (title, authors)
- API access restrictions

**Solution:** Check processing report for skipped items and errors

### Citekey Collisions

**Problem:** Multiple papers generate same citekey

**Behavior:** Automatic suffix appending (`-2`, `-3`, etc.)

**Prevention:** Not needed - system handles automatically

### Slow Performance

**Problem:** Processing takes too long

**Solutions:**
1. Enable caching (on by default)
2. Process smaller batches: `--limit 50`
3. Use faster template: `--template balanced`
4. Check network connection
5. Verify Zotero API status

### Cache Issues

**Problem:** Outdated cached data

**Solution:**
```bash
# Clear cache
rm -rf .zotero_cache/

# Or set shorter TTL in config
cache_ttl: 3600  # 1 hour instead of 24
```

## Advanced Usage

### Custom Output Structure

```python
from src.models import ObsidianConfig

config = ObsidianConfig(
    vault_path="~/Obsidian/Research",
    create_folders=True,
    use_rest_api=False
)
```

### Filtering by Item Type

```python
# Filter in workflow
items = [item for item in all_items
         if item['data']['itemType'] == 'journalArticle']
```

### Custom Template Variables

Extend templates with custom Jinja2 variables for Zotero-specific fields.

### Citation Network Integration

When processing papers from Zotero with `/citemap`, the network visualization automatically includes:

**Enhanced Node Metadata**:
- Zotero collections shown in hover tooltips
- Zotero tags (first 5) displayed on hover
- Clickable "Open in Zotero" links for each node
- Color-coding by Zotero collection (optional)

**Relationship Extraction**:
- Extracts citation relationships from Zotero item relations (dc:relation field)
- Merges Zotero relationship data with PDF-extracted citations
- Builds comprehensive citation network combining both sources

**Usage**:
```bash
# Generate citation map from Zotero-processed PDFs
/citemap zotero_papers/ --batch

# Output includes Zotero metadata in interactive visualization
# Hover over nodes to see collections, tags, and Zotero links
```

## Best Practices

1. **Test with Small Batch First**
   ```bash
   /zotero --collection ABC123 --limit 5
   ```

2. **Use Meaningful Collection Names**
   - Collections become folder names
   - Use descriptive names without special characters

3. **Regular Syncs**
   - Run weekly or monthly to keep Obsidian vault updated
   - Use `--limit` to process only recent additions

4. **Backup Before Large Batches**
   ```bash
   cp -r obsidian_vault obsidian_vault.backup
   ```

5. **Monitor API Usage**
   - Zotero free tier: Generous limits
   - Check cache hit rate in processing reports

## Next Steps

- **[README.md](../README.md)** - Main documentation
- **[QUICK_START.md](../QUICK_START.md)** - Quick start guide
- **[TROUBLESHOOTING.md](../TROUBLESHOOTING.md)** - General troubleshooting

---

*For questions or issues, please see [GitHub Issues](https://github.com/scholarsquill/scholarsquill/issues)*
