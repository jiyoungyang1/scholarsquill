"""
Unit tests for Obsidian formatting and markdown writing
Tests MUST fail until implementation is complete (TDD)
"""

import pytest
from pathlib import Path
from src.obsidian.formatter import ObsidianFormatter
from src.obsidian.writer import ObsidianWriter
from src.models import PaperMetadata, ObsidianConfig


class TestObsidianFormatter:
    """Test Obsidian-specific formatting"""

    @pytest.fixture
    def formatter(self):
        """Create formatter instance"""
        return ObsidianFormatter()

    @pytest.fixture
    def sample_metadata(self):
        """Create sample paper metadata with Zotero fields"""
        return PaperMetadata(
            title="Machine Learning for Protein Stability",
            first_author="Smith",
            authors=["Smith, John", "Doe, Jane"],
            year=2023,
            citekey="smith2023machine",
            doi="10.1234/example",
            journal="Nature",
            volume="42",
            pages="123-145",
            abstract="This paper investigates...",
            zotero_key="ABC123",
            zotero_url="zotero://select/library/items/ABC123",
            zotero_tags=["machine-learning", "protein-stability", "deep-learning"],
            zotero_collections=["Machine Learning", "Protein Science"],
            date_added="2024-01-15",
            date_modified="2024-01-20"
        )

    def test_format_yaml_frontmatter(self, formatter, sample_metadata):
        """Test format_yaml_frontmatter() with Zotero metadata"""
        frontmatter = formatter.format_yaml_frontmatter(sample_metadata)

        assert "---" in frontmatter
        assert "title: Machine Learning for Protein Stability" in frontmatter
        assert "authors:" in frontmatter
        assert "year: 2023" in frontmatter
        assert "citekey: smith2023machine" in frontmatter
        assert "doi: 10.1234/example" in frontmatter

        # Zotero-specific fields
        assert "zotero_key: ABC123" in frontmatter
        assert "zotero_url: zotero://select/library/items/ABC123" in frontmatter
        assert "tags:" in frontmatter
        assert "  - machine-learning" in frontmatter
        assert "collections:" in frontmatter
        assert "  - Machine Learning" in frontmatter

    def test_wikilink_generation_for_references(self, formatter):
        """Test wikilink generation for note references"""
        ref_citekey = "doe2022neural"
        wikilink = formatter.generate_wikilink(ref_citekey)

        assert wikilink == "[[doe2022neural]]"

    def test_wikilink_with_display_text(self, formatter):
        """Test wikilink with custom display text"""
        ref_citekey = "doe2022neural"
        display_text = "Doe et al. 2022"
        wikilink = formatter.generate_wikilink(ref_citekey, display_text)

        assert wikilink == "[[doe2022neural|Doe et al. 2022]]"

    def test_zotero_url_formatting(self, formatter):
        """Test Zotero URL formatting (zotero://select/...)"""
        zotero_key = "ABC123"
        library_type = "user"
        library_id = "12345"

        url = formatter.format_zotero_url(zotero_key, library_type, library_id)

        assert url == "zotero://select/library/items/ABC123"

    def test_tag_formatting_for_obsidian(self, formatter):
        """Test tag formatting for Obsidian syntax"""
        tags = ["machine-learning", "protein-stability", "deep-learning"]
        formatted = formatter.format_tags(tags)

        # Obsidian uses #tag or YAML array format
        assert "machine-learning" in formatted
        assert "protein-stability" in formatted

    def test_collection_folder_path_generation(self, formatter):
        """Test collection folder path mapping"""
        collections = ["Machine Learning", "Machine Learning/Neural Networks"]
        path = formatter.generate_collection_path(collections)

        # Should use deepest collection for folder structure
        assert "Machine Learning/Neural Networks" in path or "Machine_Learning/Neural_Networks" in path


class TestObsidianWriter:
    """Test markdown file writing for Obsidian"""

    @pytest.fixture
    def config(self, tmp_path):
        """Create Obsidian configuration"""
        return ObsidianConfig(
            vault_path=str(tmp_path / "vault"),
            create_folders=True
        )

    @pytest.fixture
    def writer(self, config):
        """Create writer instance"""
        return ObsidianWriter(config)

    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata"""
        return PaperMetadata(
            title="Test Paper",
            first_author="Smith",
            authors=["Smith, J."],
            year=2023,
            citekey="smith2023test",
            zotero_key="TEST123",
            zotero_url="zotero://select/library/items/TEST123",
            zotero_tags=["test"],
            zotero_collections=["Test Collection"]
        )

    def test_write_note_creates_file(self, writer, sample_metadata, tmp_path):
        """Test write_note() creates file with proper structure"""
        content = """# Test Paper

## Summary
This is a test paper.
"""

        file_path = writer.write_note(sample_metadata, content)

        assert Path(file_path).exists()
        assert Path(file_path).name == "smith2023test.md"

    def test_filename_conflict_handling(self, writer, sample_metadata, tmp_path):
        """Test filename conflict resolution for duplicate citekeys"""
        content = "# Test"

        # Create first file
        file1 = writer.write_note(sample_metadata, content)
        assert Path(file1).exists()

        # Try to create file with same citekey
        file2 = writer.write_note(sample_metadata, content)

        # Should append suffix: smith2023test-2.md
        assert Path(file2).exists()
        assert "smith2023test" in str(file2)
        assert file1 != file2

    def test_nested_folder_creation_for_collections(self, writer, sample_metadata, tmp_path):
        """Test folder creation for nested collections"""
        sample_metadata.zotero_collections = ["Parent", "Parent/Child", "Parent/Child/Deep"]

        content = "# Test"
        file_path = writer.write_note(sample_metadata, content)

        # Should create nested folder structure
        parent_dir = Path(file_path).parent
        assert parent_dir.exists()
        # Check if nested structure was created
        assert "Deep" in str(parent_dir) or "Child" in str(parent_dir)

    def test_file_write_error_handling(self, writer, sample_metadata):
        """Test error handling for write failures"""
        # Simulate read-only directory
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Read-only")):
            with pytest.raises(Exception):  # Will be ObsidianWriteError
                writer.write_note(sample_metadata, "# Test")
