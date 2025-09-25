"""
Unit tests for PDFProcessor class
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import PyPDF2

from src.pdf_processor import PDFProcessor
from src.models import PaperMetadata
from src.exceptions import FileError, ProcessingError, ErrorCode


class TestPDFProcessor:
    """Test cases for PDFProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Create PDFProcessor instance for testing"""
        return PDFProcessor(max_file_size_mb=10)
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Create a temporary file path for testing"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n')
            return tmp.name
    
    @pytest.fixture
    def sample_text(self):
        """Sample extracted text for testing"""
        return """
        Machine Learning Applications in Bioinformatics: A Comprehensive Review
        
        John A. Smith, Mary B. Johnson, Robert C. Davis
        
        Department of Computer Science, University of Example
        
        Abstract
        This paper presents a comprehensive review of machine learning applications
        in bioinformatics, covering recent advances and future directions.
        
        Keywords: machine learning, bioinformatics, data analysis
        
        1. Introduction
        Machine learning has become increasingly important in bioinformatics...
        
        Journal of Computational Biology, Vol. 25, No. 3, pp. 123-145
        DOI: 10.1089/cmb.2023.0123
        2023
        """
    
    def test_init(self):
        """Test PDFProcessor initialization"""
        processor = PDFProcessor(max_file_size_mb=20)
        assert processor.max_file_size_mb == 20
        assert processor.logger is not None
    
    def test_validate_pdf_file_not_found(self, processor):
        """Test validation with non-existent file"""
        with pytest.raises(FileError) as exc_info:
            processor.validate_pdf("nonexistent.pdf")
        
        assert exc_info.value.error_code == ErrorCode.FILE_NOT_FOUND
        assert "nonexistent.pdf" in str(exc_info.value)
    
    def test_validate_pdf_not_pdf_extension(self, processor):
        """Test validation with non-PDF file"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
            with pytest.raises(FileError) as exc_info:
                processor.validate_pdf(tmp.name)
            
            assert exc_info.value.error_code == ErrorCode.INVALID_PDF
    
    def test_validate_pdf_file_too_large(self, processor):
        """Test validation with file too large"""
        processor.max_file_size_mb = 0.001  # Very small limit
        
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            tmp.write(b'x' * 2000)  # Write 2KB
            tmp.flush()
            
            with pytest.raises(FileError) as exc_info:
                processor.validate_pdf(tmp.name)
            
            assert exc_info.value.error_code == ErrorCode.FILE_TOO_LARGE
    
    @patch('PyPDF2.PdfReader')
    def test_validate_pdf_success(self, mock_reader, processor, sample_pdf_path):
        """Test successful PDF validation"""
        # Mock successful PDF reading
        mock_reader.return_value.pages = [Mock()]
        
        with patch('builtins.open', mock_open(read_data=b'%PDF-1.4')):
            result = processor.validate_pdf(sample_pdf_path)
            assert result is True
    
    @patch('PyPDF2.PdfReader')
    def test_validate_pdf_corrupted(self, mock_reader, processor, sample_pdf_path):
        """Test validation with corrupted PDF"""
        # Mock PDF reading failure
        mock_reader.side_effect = Exception("Corrupted PDF")
        
        with patch('builtins.open', mock_open(read_data=b'%PDF-1.4')):
            result = processor.validate_pdf(sample_pdf_path)
            assert result is False
    
    @patch('PyPDF2.PdfReader')
    def test_get_page_count_success(self, mock_reader, processor, sample_pdf_path):
        """Test successful page count extraction"""
        # Mock PDF with 5 pages
        mock_reader.return_value.pages = [Mock() for _ in range(5)]
        
        with patch.object(processor, 'validate_pdf', return_value=True):
            with patch('builtins.open', mock_open()):
                count = processor.get_page_count(sample_pdf_path)
                assert count == 5
    
    @patch('PyPDF2.PdfReader')
    def test_get_page_count_failure(self, mock_reader, processor, sample_pdf_path):
        """Test page count extraction failure"""
        mock_reader.side_effect = Exception("Read error")
        
        with patch.object(processor, 'validate_pdf', return_value=True):
            with patch('builtins.open', mock_open()):
                with pytest.raises(ProcessingError) as exc_info:
                    processor.get_page_count(sample_pdf_path)
                
                assert exc_info.value.error_code == ErrorCode.PROCESSING_TIMEOUT
    
    @patch('pdfplumber.open')
    def test_extract_text_with_pdfplumber_success(self, mock_pdfplumber, processor, sample_pdf_path):
        """Test successful text extraction with pdfplumber"""
        # Mock pdfplumber
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample text from page"
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf
        
        with patch.object(processor, 'validate_pdf', return_value=True):
            text = processor.extract_text(sample_pdf_path)
            assert text == "Sample text from page"
    
    @patch('pdfplumber.open')
    @patch('PyPDF2.PdfReader')
    def test_extract_text_fallback_to_pypdf2(self, mock_reader, mock_pdfplumber, processor, sample_pdf_path):
        """Test fallback to PyPDF2 when pdfplumber fails"""
        # Mock pdfplumber failure
        mock_pdfplumber.side_effect = Exception("pdfplumber failed")
        
        # Mock PyPDF2 success
        mock_page = Mock()
        mock_page.extract_text.return_value = "PyPDF2 extracted text"
        mock_reader.return_value.pages = [mock_page]
        
        with patch.object(processor, 'validate_pdf', return_value=True):
            with patch('builtins.open', mock_open()):
                text = processor.extract_text(sample_pdf_path)
                assert text == "PyPDF2 extracted text"
    
    @patch('pdfplumber.open')
    @patch('PyPDF2.PdfReader')
    def test_extract_text_both_methods_fail(self, mock_reader, mock_pdfplumber, processor, sample_pdf_path):
        """Test when both extraction methods fail"""
        # Mock both methods failing
        mock_pdfplumber.side_effect = Exception("pdfplumber failed")
        mock_reader.side_effect = Exception("PyPDF2 failed")
        
        with patch.object(processor, 'validate_pdf', return_value=True):
            with patch('builtins.open', mock_open()):
                with pytest.raises(ProcessingError) as exc_info:
                    processor.extract_text(sample_pdf_path)
                
                assert exc_info.value.error_code == ErrorCode.TEXT_EXTRACTION_FAILED
    
    def test_extract_title_from_text(self, processor, sample_text):
        """Test title extraction from text"""
        title = processor._extract_title_from_text(sample_text)
        assert "Machine Learning Applications in Bioinformatics" in title
    
    def test_extract_authors_from_text(self, processor, sample_text):
        """Test author extraction from text"""
        authors = processor._extract_authors_from_text(sample_text)
        assert len(authors) > 0
        assert any("Smith" in author for author in authors)
    
    def test_extract_year_from_text(self, processor, sample_text):
        """Test year extraction from text"""
        year = processor._extract_year_from_text(sample_text)
        assert year == 2023
    
    def test_extract_doi_from_text(self, processor, sample_text):
        """Test DOI extraction from text"""
        doi = processor._extract_doi_from_text(sample_text)
        assert doi == "10.1089/cmb.2023.0123"
    
    def test_extract_journal_info_from_text(self, processor, sample_text):
        """Test journal information extraction"""
        info = processor._extract_journal_info_from_text(sample_text)
        assert info.get('volume') == '25'
        assert info.get('issue') == '3'
        assert info.get('pages') == '123-145'
    
    def test_extract_abstract_from_text(self, processor, sample_text):
        """Test abstract extraction from text"""
        abstract = processor._extract_abstract_from_text(sample_text)
        assert abstract is not None
        assert "comprehensive review" in abstract.lower()
    
    def test_generate_citekey_full_metadata(self, processor):
        """Test citekey generation with complete metadata"""
        metadata = PaperMetadata(
            title="Machine Learning Applications in Bioinformatics",
            first_author="Smith, John A.",
            authors=["Smith, John A.", "Johnson, Mary B."],
            year=2023
        )
        
        citekey = processor.generate_citekey(metadata)
        assert citekey == "Smith2023Machine"
    
    def test_generate_citekey_minimal_metadata(self, processor):
        """Test citekey generation with minimal metadata"""
        metadata = PaperMetadata(
            title="",
            first_author="Unknown",
            authors=[],
            year=None
        )
        
        citekey = processor.generate_citekey(metadata)
        assert citekey == "UnknownYYYYpaper"
    
    def test_generate_citekey_different_author_format(self, processor):
        """Test citekey generation with different author formats"""
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="John Smith",  # First Last format
            authors=["John Smith"],
            year=2023
        )
        
        citekey = processor.generate_citekey(metadata)
        assert citekey == "Smith2023Test"
    
    def test_generate_keyword_from_title(self, processor):
        """Test keyword generation from title"""
        # Test with meaningful words
        keyword = processor._generate_keyword_from_title("Machine Learning Applications in Bioinformatics")
        assert keyword == "Machine"
        
        # Test with stop words only
        keyword = processor._generate_keyword_from_title("A Study of the Analysis")
        assert keyword == "paper"
        
        # Test with empty title
        keyword = processor._generate_keyword_from_title("")
        assert keyword == "paper"
    
    @patch.object(PDFProcessor, 'validate_pdf')
    @patch.object(PDFProcessor, 'get_page_count')
    @patch.object(PDFProcessor, '_extract_pdf_metadata')
    @patch.object(PDFProcessor, 'extract_text')
    @patch.object(PDFProcessor, '_extract_content_metadata')
    def test_extract_metadata_success(self, mock_content_meta, mock_extract_text, 
                                    mock_pdf_meta, mock_page_count, mock_validate, 
                                    processor, sample_pdf_path):
        """Test successful metadata extraction"""
        # Setup mocks
        mock_validate.return_value = True
        mock_page_count.return_value = 10
        mock_pdf_meta.return_value = {'title': 'PDF Title'}
        mock_extract_text.return_value = "Sample text"
        mock_content_meta.return_value = {
            'content_title': 'Content Title',
            'content_authors': ['Smith, John'],
            'content_year': 2023
        }
        
        metadata = processor.extract_metadata(sample_pdf_path)
        
        assert isinstance(metadata, PaperMetadata)
        assert metadata.title == 'Content Title'
        assert metadata.first_author == 'Smith, John'
        assert metadata.year == 2023
        assert metadata.page_count == 10
        assert metadata.citekey  # Should be generated
    
    @patch.object(PDFProcessor, 'validate_pdf')
    def test_extract_metadata_invalid_pdf(self, mock_validate, processor, sample_pdf_path):
        """Test metadata extraction with invalid PDF"""
        mock_validate.side_effect = FileError(
            message="Invalid PDF",
            error_code=ErrorCode.INVALID_PDF,
            file_path=sample_pdf_path
        )
        
        with pytest.raises(FileError):
            processor.extract_metadata(sample_pdf_path)
    
    def test_combine_metadata(self, processor):
        """Test metadata combination from different sources"""
        pdf_metadata = {'title': 'PDF Title', 'author': 'Smith, John; Johnson, Mary'}
        content_metadata = {
            'content_title': 'Content Title',
            'content_authors': ['Smith, John A.'],
            'content_year': 2023,
            'content_doi': '10.1000/test'
        }
        
        metadata = processor._combine_metadata(
            pdf_metadata, content_metadata, '/path/test.pdf', 5
        )
        
        assert metadata.title == 'Content Title'  # Content preferred over PDF
        assert metadata.first_author == 'Smith, John A.'
        assert metadata.year == 2023
        assert metadata.doi == '10.1000/test'
        assert metadata.page_count == 5
        assert metadata.file_path == '/path/test.pdf'
    
    def test_combine_metadata_fallback_to_pdf(self, processor):
        """Test metadata combination when content extraction fails"""
        pdf_metadata = {'title': 'PDF Title', 'author': 'Smith, John'}
        content_metadata = {}  # Empty content metadata
        
        metadata = processor._combine_metadata(
            pdf_metadata, content_metadata, '/path/test.pdf', 3
        )
        
        assert metadata.title == 'PDF Title'  # Falls back to PDF metadata
        assert metadata.first_author == 'Smith, John'
    
    def test_combine_metadata_fallback_to_filename(self, processor):
        """Test metadata combination when both sources fail"""
        pdf_metadata = {}
        content_metadata = {}
        
        metadata = processor._combine_metadata(
            pdf_metadata, content_metadata, '/path/test_paper.pdf', 1
        )
        
        assert metadata.title == 'test_paper'  # Falls back to filename
        assert metadata.first_author == 'Unknown'


class TestPDFProcessorIntegration:
    """Integration tests for PDFProcessor"""
    
    @pytest.fixture
    def processor(self):
        return PDFProcessor()
    
    def test_full_workflow_with_mock_pdf(self, processor):
        """Test complete workflow with mocked PDF operations"""
        with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
            # Mock all PDF operations for integration test
            with patch.object(processor, 'validate_pdf', return_value=True), \
                 patch.object(processor, 'get_page_count', return_value=5), \
                 patch.object(processor, 'extract_text', return_value="Sample paper text"), \
                 patch.object(processor, '_extract_pdf_metadata', return_value={}), \
                 patch.object(processor, '_extract_content_metadata', return_value={
                     'content_title': 'Test Paper',
                     'content_authors': ['Smith, John'],
                     'content_year': 2023
                 }):
                
                # Test the full workflow
                assert processor.validate_pdf(tmp.name) is True
                assert processor.get_page_count(tmp.name) == 5
                text = processor.extract_text(tmp.name)
                assert text == "Sample paper text"
                
                metadata = processor.extract_metadata(tmp.name)
                assert metadata.title == 'Test Paper'
                assert metadata.first_author == 'Smith, John'
                assert metadata.year == 2023
                assert metadata.citekey == 'Smith2023Test'


if __name__ == '__main__':
    pytest.main([__file__])