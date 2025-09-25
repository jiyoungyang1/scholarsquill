"""
Tests for core data models
"""

import pytest
from datetime import datetime
from src.models import (
    PaperMetadata, ProcessingOptions, NoteContent, AnalysisResult,
    CommandArgs, FocusType, DepthType, FormatType
)


class TestPaperMetadata:
    """Test PaperMetadata model"""
    
    def test_paper_metadata_creation(self):
        """Test creating PaperMetadata instance"""
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John", "Doe, Jane"],
            year=2023,
            journal="Test Journal"
        )
        
        assert metadata.title == "Test Paper"
        assert metadata.first_author == "Smith, John"
        assert len(metadata.authors) == 2
        assert metadata.year == 2023
        assert metadata.journal == "Test Journal"
        assert metadata.item_type == "journalArticle"  # default value
    
    def test_paper_metadata_defaults(self):
        """Test PaperMetadata with minimal required fields"""
        metadata = PaperMetadata(
            title="Minimal Paper",
            first_author="Author, Test",
            authors=["Author, Test"]
        )
        
        assert metadata.title == "Minimal Paper"
        assert metadata.year is None
        assert metadata.citekey == ""
        assert metadata.page_count == 0


class TestProcessingOptions:
    """Test ProcessingOptions model"""
    
    def test_processing_options_defaults(self):
        """Test ProcessingOptions with default values"""
        options = ProcessingOptions()
        
        assert options.focus == FocusType.BALANCED
        assert options.depth == DepthType.STANDARD
        assert options.format == FormatType.MARKDOWN
        assert options.batch is False
        assert options.output_dir is None
    
    def test_processing_options_custom(self):
        """Test ProcessingOptions with custom values"""
        options = ProcessingOptions(
            focus=FocusType.RESEARCH,
            depth=DepthType.DEEP,
            batch=True,
            output_dir="/custom/output"
        )
        
        assert options.focus == FocusType.RESEARCH
        assert options.depth == DepthType.DEEP
        assert options.batch is True
        assert options.output_dir == "/custom/output"


class TestEnums:
    """Test enum types"""
    
    def test_focus_type_values(self):
        """Test FocusType enum values"""
        assert FocusType.RESEARCH.value == "research"
        assert FocusType.THEORY.value == "theory"
        assert FocusType.REVIEW.value == "review"
        assert FocusType.METHOD.value == "method"
        assert FocusType.BALANCED.value == "balanced"
    
    def test_depth_type_values(self):
        """Test DepthType enum values"""
        assert DepthType.QUICK.value == "quick"
        assert DepthType.STANDARD.value == "standard"
        assert DepthType.DEEP.value == "deep"
    
    def test_format_type_values(self):
        """Test FormatType enum values"""
        assert FormatType.MARKDOWN.value == "markdown"


class TestAnalysisResult:
    """Test AnalysisResult model"""
    
    def test_analysis_result_creation(self):
        """Test creating AnalysisResult instance"""
        result = AnalysisResult(
            paper_type="research",
            confidence=0.85,
            sections={"abstract": "Test abstract", "introduction": "Test intro"},
            key_concepts=["concept1", "concept2"],
            equations=["E=mc²"],
            methodologies=["experimental"]
        )
        
        assert result.paper_type == "research"
        assert result.confidence == 0.85
        assert len(result.sections) == 2
        assert len(result.key_concepts) == 2
        assert len(result.equations) == 1
        assert len(result.methodologies) == 1
    
    def test_analysis_result_defaults(self):
        """Test AnalysisResult with default lists"""
        result = AnalysisResult(
            paper_type="theory",
            confidence=0.9,
            sections={},
            key_concepts=[]
        )
        
        assert result.equations == []
        assert result.methodologies == []


class TestCommandArgs:
    """Test CommandArgs model"""
    
    def test_command_args_creation(self):
        """Test creating CommandArgs instance"""
        args = CommandArgs(
            target="test.pdf",
            focus=FocusType.THEORY,
            depth=DepthType.DEEP,
            batch=True
        )
        
        assert args.target == "test.pdf"
        assert args.focus == FocusType.THEORY
        assert args.depth == DepthType.DEEP
        assert args.batch is True
    
    def test_command_args_defaults(self):
        """Test CommandArgs with default values"""
        args = CommandArgs(target="test.pdf")
        
        assert args.target == "test.pdf"
        assert args.focus == FocusType.BALANCED
        assert args.depth == DepthType.STANDARD
        assert args.format == FormatType.MARKDOWN
        assert args.batch is False
        assert args.output_dir is None


class TestNoteContent:
    """Test NoteContent model"""
    
    def test_note_content_creation(self):
        """Test creating NoteContent instance"""
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John"]
        )
        
        options = ProcessingOptions(focus=FocusType.RESEARCH)
        
        content = NoteContent(
            title="Test Note",
            citation="Smith, J. (2023). Test Paper.",
            sections={"summary": "Test summary"},
            metadata=metadata,
            generated_at=datetime.now(),
            processing_options=options
        )
        
        assert content.title == "Test Note"
        assert content.citation == "Smith, J. (2023). Test Paper."
        assert len(content.sections) == 1
        assert content.metadata.title == "Test Paper"
        assert content.processing_options.focus == FocusType.RESEARCH