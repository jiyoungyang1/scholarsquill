# Citekey-Based Filename Generation

## Overview

The ScholarSquill MCP Server now includes robust citekey-based filename generation for literature notes. This ensures consistent, predictable filenames that follow academic citation conventions.

## Citekey Format

The citekey format follows the pattern: `authorYEARkeyword`

- **author**: Last name of the first author (lowercase, no special characters)
- **YEAR**: Publication year (4 digits, or "unknown" if not available)
- **keyword**: First meaningful word from the title (3+ characters, lowercase)

### Examples

| PDF Filename | Authors | Year | Title | Generated Citekey |
|--------------|---------|------|-------|-------------------|
| Bonollo et al. - 2025 - Advancing... | Bonollo, M. | 2025 | Advancing Molecular Simulations... | `bonollo2025advancing` |
| Cloutier et al. - 2020 - Molecular... | Cloutier, T. | 2020 | Molecular computations of... | `cloutier2020molecular` |
| Kmiecik et al. - 2016 - Coarse-Grained... | Kmiecik, S. | 2016 | Coarse-Grained Protein Models... | `kmiecik2016coarse` |

## Implementation

### Core Functions

1. **`generate_citekey(first_author, year, title)`** in `utils.py`
   - Handles both "LastName, FirstName" and "FirstName LastName" formats
   - Removes special characters from author names
   - Extracts first meaningful word from title

2. **`generate_citekey_filename(metadata, format_type)`** in `file_writer.py`
   - Uses `generate_citekey()` to create the base filename
   - Adds appropriate file extension (.md for markdown)
   - Includes filename sanitization for filesystem safety

### Author Name Parsing

The system handles various author name formats:

```python
# "LastName, FirstName" format (common in academic papers)
"Bonollo, M." → "bonollo"

# "FirstName LastName" format
"John Smith" → "smith"

# Special characters are removed
"O'Connor, P." → "oconnor"
"van der Berg, M." → "vandenberg"
```

### Title Processing

The system extracts the first meaningful word from titles:

```python
# Meaningful words are 3+ characters
"Advancing Molecular Simulations..." → "advancing"
"A New AI ML Approach" → "new"  # Skips short words like "A"
"The Role of..." → "role"  # Skips articles
```

## Testing with Real PDF Files

### Sample Files

The testing uses real PDF files from `/Users/yyangg00/scholarsquill/examples/papers/`:

1. `Bonollo et al. - 2025 - Advancing Molecular Simulations...pdf`
2. `Cloutier et al. - 2020 - Molecular computations...pdf`
3. `Ganguly et al. - 2012 - Kirkwood–Buff Coarse-Grained...pdf`
4. `Kmiecik et al. - 2016 - Coarse-Grained Protein Models...pdf`
5. `Zidar et al. - 2020 - Control of viscosity...pdf`

### Reference Notes Comparison

The system compares generated notes with existing reference notes in:
`/Users/yyangg00/scholarsquill/examples/papers/output literature notes/`

Reference notes include:
- `bonollo2025advancing_review_analysis.md`
- `cloutier2020molecular.md`
- `kmiecik2016coarsegrained.md`
- `zidar2020control.md`
- `simon2022kirkwood.md`
- `wood2020hdx.md`

### Test Coverage

The test suite includes:

1. **Unit Tests** (`test_citekey_and_filename_generation.py`)
   - Citekey generation with various author formats
   - Edge cases (missing year, no authors, special characters)
   - Filename generation consistency

2. **Integration Tests** (`test_pdf_processing_integration.py`)
   - Real PDF metadata extraction
   - Content analysis with sample files
   - Full workflow testing (PDF → citekey → filename → note)
   - Comparison with reference notes

3. **Demo Scripts**
   - `test_citekey_generation.py`: Basic citekey testing
   - `demo_citekey_with_pdfs.py`: Real PDF demonstration

## Usage Examples

### Basic Usage

```python
from utils import generate_citekey
from file_writer import FileWriter

# Generate citekey
citekey = generate_citekey("Bonollo, M.", 2025, "Advancing Molecular Simulations")
# Returns: "bonollo2025advancing"

# Generate filename
file_writer = FileWriter()
filename = file_writer.generate_citekey_filename(metadata)
# Returns: "bonollo2025advancing.md"
```

### Integration with MCP Server

The MCP server automatically uses citekey-based filenames when processing PDFs:

```bash
/sq:note path/to/paper.pdf --focus research --depth standard
# Generates: bonollo2025advancing.md
```

## Validation and Quality Assurance

### Automated Testing

- **Citekey Accuracy**: Tests verify generated citekeys match expected format
- **Filename Safety**: Ensures generated filenames are filesystem-safe
- **Consistency**: Validates same input always produces same output
- **Edge Cases**: Handles missing metadata gracefully

### Manual Validation

- **Reference Comparison**: Generated notes compared with existing literature notes
- **Structure Analysis**: Validates note structure matches expected format
- **Content Quality**: Ensures generated content is meaningful and well-structured

## Error Handling

The system includes robust error handling:

1. **Missing Metadata**: Falls back to timestamp-based naming
2. **Invalid Characters**: Automatically sanitizes filenames
3. **Duplicate Files**: Handles file conflicts with rename/overwrite options
4. **Empty Fields**: Provides sensible defaults ("unknown", "paper", etc.)

## Future Enhancements

Potential improvements for the citekey system:

1. **Custom Formats**: Allow user-defined citekey patterns
2. **Disambiguation**: Handle duplicate citekeys with suffixes (a, b, c)
3. **Journal Integration**: Include journal abbreviations in citekeys
4. **Batch Validation**: Validate citekey uniqueness across collections
5. **Export Formats**: Support for BibTeX, EndNote, etc.

## Running Tests

To test the citekey functionality:

```bash
# Basic citekey testing
python test_citekey_generation.py

# Demo with real PDFs
python demo_citekey_with_pdfs.py

# Full test suite
pytest tests/test_citekey_and_filename_generation.py -v
pytest tests/test_pdf_processing_integration.py -v
```

## Configuration

Citekey generation can be configured through the `ServerConfig`:

```python
config = ServerConfig(
    default_output_dir="literature-notes",
    max_file_size_mb=50,
    # Future: citekey_format="author_year_keyword"
)
```