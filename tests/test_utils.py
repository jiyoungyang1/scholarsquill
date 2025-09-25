"""
Tests for utility functions
"""

import pytest
from src.utils import (
    sanitize_filename, generate_citekey, extract_first_author_lastname,
    format_file_size, validate_pdf_path, format_metadata_for_citation,
    truncate_text
)
from src.models import PaperMetadata


class TestSanitizeFilename:
    """Test sanitize_filename function"""
    
    def test_sanitize_basic(self):
        """Test basic filename sanitization"""
        result = sanitize_filename("Normal Filename.pdf")
        assert result == "Normal Filename.pdf"
    
    def test_sanitize_invalid_chars(self):
        """Test removal of invalid characters"""
        result = sanitize_filename('File<>:"/\\|?*Name.pdf')
        assert result == "FileName.pdf"
    
    def test_sanitize_multiple_spaces(self):
        """Test multiple space replacement"""
        result = sanitize_filename("File   with    spaces.pdf")
        assert result == "File with spaces.pdf"
    
    def test_sanitize_length_limit(self):
        """Test length limiting"""
        long_name = "a" * 150 + ".pdf"
        result = sanitize_filename(long_name, max_length=50)
        assert len(result) <= 50
    
    def test_sanitize_empty_fallback(self):
        """Test empty filename fallback"""
        result = sanitize_filename("")
        assert result == "untitled"
        
        result = sanitize_filename("   ")
        assert result == "untitled"


class TestGenerateCitekey:
    """Test generate_citekey function"""
    
    def test_generate_citekey_basic(self):
        """Test basic citekey generation"""
        result = generate_citekey("Smith, John", 2023, "Machine Learning Applications")
        assert result == "smith2023machine"
    
    def test_generate_citekey_no_year(self):
        """Test citekey generation without year"""
        result = generate_citekey("Doe, Jane", None, "Deep Learning Methods")
        assert result == "doeunknowndeep"
    
    def test_generate_citekey_single_name(self):
        """Test citekey generation with single name"""
        result = generate_citekey("Einstein", 1905, "Relativity Theory")
        assert result == "einstein1905relativity"
    
    def test_generate_citekey_short_title(self):
        """Test citekey generation with short title"""
        result = generate_citekey("Newton, Isaac", 1687, "On Motion")
        assert result == "newton1687motion"
    
    def test_generate_citekey_no_meaningful_words(self):
        """Test citekey generation with no meaningful title words"""
        result = generate_citekey("Author, Test", 2023, "A An The")
        assert result == "author2023paper"


class TestExtractFirstAuthorLastname:
    """Test extract_first_author_lastname function"""
    
    def test_extract_lastname_comma_format(self):
        """Test extraction from 'LastName, FirstName' format"""
        result = extract_first_author_lastname(["Smith, John"])
        assert result == "Smith"
    
    def test_extract_lastname_space_format(self):
        """Test extraction from 'FirstName LastName' format"""
        result = extract_first_author_lastname(["John Smith"])
        assert result == "Smith"
    
    def test_extract_lastname_multiple_names(self):
        """Test extraction with multiple names"""
        result = extract_first_author_lastname(["John Michael Smith"])
        assert result == "Smith"
    
    def test_extract_lastname_empty_list(self):
        """Test extraction with empty author list"""
        result = extract_first_author_lastname([])
        assert result == "Unknown"
    
    def test_extract_lastname_empty_string(self):
        """Test extraction with empty author string"""
        result = extract_first_author_lastname([""])
        assert result == "Unknown"


class TestFormatFileSize:
    """Test format_file_size function"""
    
    def test_format_bytes(self):
        """Test formatting bytes"""
        assert format_file_size(512) == "512.0 B"
    
    def test_format_kilobytes(self):
        """Test formatting kilobytes"""
        assert format_file_size(1536) == "1.5 KB"
    
    def test_format_megabytes(self):
        """Test formatting megabytes"""
        assert format_file_size(2097152) == "2.0 MB"
    
    def test_format_gigabytes(self):
        """Test formatting gigabytes"""
        assert format_file_size(3221225472) == "3.0 GB"


class TestValidatePdfPath:
    """Test validate_pdf_path function"""
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file"""
        result = validate_pdf_path("nonexistent.pdf")
        assert result is False
    
    def test_validate_wrong_extension(self):
        """Test validation of wrong file extension"""
        # This would fail because file doesn't exist, but tests the logic
        result = validate_pdf_path("document.txt")
        assert result is False


class TestFormatMetadataForCitation:
    """Test format_metadata_for_citation function"""
    
    def test_format_single_author(self):
        """Test citation formatting with single author"""
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John"],
            year=2023,
            journal="Test Journal"
        )
        
        result = format_metadata_for_citation(metadata)
        expected = 'Smith, John. (2023). "Test Paper". Test Journal'
        assert result == expected
    
    def test_format_two_authors(self):
        """Test citation formatting with two authors"""
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John", "Doe, Jane"],
            year=2023
        )
        
        result = format_metadata_for_citation(metadata)
        expected = 'Smith, John and Doe, Jane. (2023). "Test Paper"'
        assert result == expected
    
    def test_format_multiple_authors(self):
        """Test citation formatting with multiple authors"""
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John", "Doe, Jane", "Brown, Bob"],
            year=2023
        )
        
        result = format_metadata_for_citation(metadata)
        expected = 'Smith, John et al.. (2023). "Test Paper"'
        assert result == expected
    
    def test_format_with_journal_details(self):
        """Test citation formatting with journal details"""
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John"],
            year=2023,
            journal="Nature",
            volume="123",
            issue="4",
            pages="45-67"
        )
        
        result = format_metadata_for_citation(metadata)
        expected = 'Smith, John. (2023). "Test Paper". Nature, 123(4), 45-67'
        assert result == expected


class TestTruncateText:
    """Test truncate_text function"""
    
    def test_truncate_short_text(self):
        """Test truncation of short text"""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        assert result == "Short text"
    
    def test_truncate_long_text(self):
        """Test truncation of long text"""
        text = "This is a very long text that should be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) == 20
        assert result.endswith("...")
    
    def test_truncate_custom_suffix(self):
        """Test truncation with custom suffix"""
        text = "This is a long text"
        result = truncate_text(text, max_length=10, suffix="[...]")
        assert result.endswith("[...]")
        assert len(result) == 10