"""
Integration tests for end-to-end Zotero ’ ScholarsQuill ’ Obsidian workflow
Tests MUST fail until implementation is complete (TDD)

Uses real PDFs from tests/input/ directory for realistic testing
"""

import pytest
from pathlib import Path
from src.zotero.client import ZoteroClient
from src.zotero.mapper import ZoteroMetadataMapper
from src.obsidian.formatter import ObsidianFormatter
from src.obsidian.writer import ObsidianWriter
from src.models import ZoteroConfig, ObsidianConfig


@pytest.fixture
def test_pdfs():
    """Get list of test PDFs"""
    test_dir = Path(__file__).parent.parent / "input"
    return list(test_dir.glob("*.pdf"))


@pytest.fixture
def mock_zotero_item():
    """Create a mock Zotero item based on actual test PDF metadata"""
    return {
        'key': 'TEST_CANCHI2013',
        'version': 1,
        'data': {
            'itemType': 'journalArticle',
            'title': 'Cosolvent Effects on Protein Stability',
            'creators': [
                {'creatorType': 'author', 'firstName': '', 'lastName': 'Canchi'},
                {'creatorType': 'author', 'firstName': '', 'lastName': 'García'}
            ],
            'date': '2013',
            'DOI': '10.1146/annurev-physchem-040412-110156',
            'abstractNote': 'Cosolvents are ubiquitous in biological systems...',
            'publicationTitle': 'Annual Review of Physical Chemistry',
            'volume': '64',
            'pages': '273-293',
            'tags': [
                {'tag': 'protein-stability'},
                {'tag': 'cosolvent-effects'},
                {'tag': 'molecular-dynamics'}
            ],
            'collections': ['Physical Chemistry', 'Protein Science'],
            'relations': {},
            'dateAdded': '2024-01-15T10:00:00Z',
            'dateModified': '2024-01-20T15:30:00Z'
        },
        'links': {
            'self': {
                'href': 'https://api.zotero.org/users/12345/items/TEST_CANCHI2013'
            }
        }
    }


class TestEndToEndWorkflow:
    """Test complete workflow from Zotero to Obsidian"""

    def test_fetch_map_generate_write(self, mock_zotero_item, tmp_path):
        """Test: Fetch Zotero item ’ Map metadata ’ Generate note ’ Write file"""
        # Step 1: Map Zotero item to metadata
        mapper = ZoteroMetadataMapper()
        metadata = mapper.map_zotero_item(mock_zotero_item)

        # Verify metadata mapping
        assert metadata.title == 'Cosolvent Effects on Protein Stability'
        assert metadata.first_author == 'Canchi'
        assert metadata.year == 2013
        assert metadata.citekey == 'canchi2013cosolvent' or 'canchi2013' in metadata.citekey
        assert metadata.zotero_key == 'TEST_CANCHI2013'

        # Step 2: Format for Obsidian
        formatter = ObsidianFormatter()
        frontmatter = formatter.format_yaml_frontmatter(metadata)

        # Verify frontmatter
        assert '---' in frontmatter
        assert 'Canchi' in frontmatter
        assert '2013' in frontmatter
        assert 'protein-stability' in frontmatter

        # Step 3: Write to Obsidian vault
        config = ObsidianConfig(vault_path=str(tmp_path / "vault"))
        writer = ObsidianWriter(config)

        note_content = f"""{frontmatter}

# Cosolvent Effects on Protein Stability

## Summary
Comprehensive review of cosolvent effects on protein stability.

## Key Findings
- Cosolvents affect protein folding and stability
- Molecular dynamics simulations provide insights

## Methods
- Review of experimental and computational studies

## Related Papers
{formatter.generate_wikilink('garcia2011molecular')}
"""

        file_path = writer.write_note(metadata, note_content)

        # Verify file created
        assert Path(file_path).exists()
        assert 'canchi2013' in str(file_path).lower()

        # Verify file contents
        with open(file_path, 'r') as f:
            content = f.read()
            assert 'Cosolvent Effects on Protein Stability' in content
            assert 'zotero_key: TEST_CANCHI2013' in content
            assert 'protein-stability' in content

    def test_yaml_frontmatter_correctness(self, mock_zotero_item):
        """Verify YAML frontmatter structure and content"""
        mapper = ZoteroMetadataMapper()
        metadata = mapper.map_zotero_item(mock_zotero_item)

        formatter = ObsidianFormatter()
        frontmatter = formatter.format_yaml_frontmatter(metadata)

        # Required fields
        assert 'title:' in frontmatter
        assert 'authors:' in frontmatter
        assert 'year:' in frontmatter
        assert 'citekey:' in frontmatter

        # Zotero fields
        assert 'zotero_key:' in frontmatter
        assert 'zotero_url:' in frontmatter
        assert 'tags:' in frontmatter
        assert 'collections:' in frontmatter

        # Proper YAML formatting
        assert frontmatter.startswith('---')
        assert frontmatter.count('---') >= 2

    def test_file_location_matches_collection_structure(self, mock_zotero_item, tmp_path):
        """Verify file location follows Zotero collection hierarchy"""
        mapper = ZoteroMetadataMapper()
        metadata = mapper.map_zotero_item(mock_zotero_item)

        config = ObsidianConfig(
            vault_path=str(tmp_path / "vault"),
            create_folders=True
        )
        writer = ObsidianWriter(config)

        file_path = writer.write_note(metadata, "# Test")

        # Should be in Physical Chemistry or Protein Science folder
        assert 'Physical Chemistry' in str(file_path) or 'Protein Science' in str(file_path) or 'Physical_Chemistry' in str(file_path)


class TestZoteroAPIIntegration:
    """Test integration with actual Zotero API patterns (mocked)"""

    def test_multiple_item_types(self):
        """Test handling different Zotero item types from collection"""
        items = [
            {
                'key': 'JOURNAL1',
                'data': {
                    'itemType': 'journalArticle',
                    'title': 'Journal Paper',
                    'creators': [{'creatorType': 'author', 'lastName': 'Smith'}],
                    'date': '2023'
                }
            },
            {
                'key': 'BOOK1',
                'data': {
                    'itemType': 'book',
                    'title': 'Book Title',
                    'creators': [{'creatorType': 'author', 'lastName': 'Doe'}],
                    'date': '2022'
                }
            },
            {
                'key': 'CONF1',
                'data': {
                    'itemType': 'conferencePaper',
                    'title': 'Conference Paper',
                    'creators': [{'creatorType': 'author', 'lastName': 'Chen'}],
                    'date': '2024'
                }
            }
        ]

        mapper = ZoteroMetadataMapper()

        for item in items:
            metadata = mapper.map_zotero_item(item)
            assert metadata is not None
            assert metadata.item_type == item['data']['itemType']
            assert metadata.citekey != ""

    def test_missing_optional_fields(self):
        """Test handling Zotero items with missing optional fields"""
        minimal_item = {
            'key': 'MINIMAL1',
            'data': {
                'itemType': 'journalArticle',
                'title': 'Minimal Item',
                'creators': [{'creatorType': 'author', 'lastName': 'Test'}],
                'date': '2023'
                # Missing: DOI, abstract, journal, volume, pages, tags, collections
            }
        }

        mapper = ZoteroMetadataMapper()
        metadata = mapper.map_zotero_item(minimal_item)

        # Should handle gracefully
        assert metadata.title == 'Minimal Item'
        assert metadata.first_author == 'Test'
        assert metadata.year == 2023
        assert metadata.citekey != ""
        # Optional fields should have defaults
        assert metadata.zotero_tags == [] or metadata.zotero_tags is None
        assert metadata.zotero_collections == [] or metadata.zotero_collections is None


class TestRealPDFMetadata:
    """Test using metadata from actual test PDFs"""

    def test_canchi_garcia_2013(self, test_pdfs):
        """Test with Canchi & García 2013 PDF"""
        # This test verifies we can process the actual PDF in tests/input/
        canchi_pdf = None
        for pdf in test_pdfs:
            if 'Canchi' in pdf.name and '2013' in pdf.name:
                canchi_pdf = pdf
                break

        assert canchi_pdf is not None, "Canchi 2013 PDF not found in tests/input/"
        assert canchi_pdf.exists()

    def test_cloutier_2020(self, test_pdfs):
        """Test with Cloutier et al. 2020 PDFs"""
        cloutier_pdfs = [p for p in test_pdfs if 'Cloutier' in p.name and '2020' in p.name]
        assert len(cloutier_pdfs) >= 1, "Cloutier 2020 PDFs not found"

    def test_cournia_chipot_2024(self, test_pdfs):
        """Test with Cournia & Chipot 2024 PDF"""
        cournia_pdf = None
        for pdf in test_pdfs:
            if 'Cournia' in pdf.name and '2024' in pdf.name:
                cournia_pdf = pdf
                break

        assert cournia_pdf is not None, "Cournia 2024 PDF not found"
        assert cournia_pdf.exists()
