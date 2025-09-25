"""
Unit tests for note generator
"""

import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock

from src.note_generator import NoteGenerator
from src.template_engine import TemplateProcessor
from src.models import (
    PaperMetadata, AnalysisResult, FocusType, DepthType, NoteTemplate, TemplateSection
)
from src.exceptions import NoteGenerationError


class TestNoteGenerator:
    """Test cases for NoteGenerator class"""
    
    @pytest.fixture
    def sample_metadata(self):
        """Sample paper metadata for testing"""
        return PaperMetadata(
            title="Test Paper: A Novel Approach",
            first_author="Smith, John",
            authors=["Smith, John", "Doe, Jane", "Johnson, Bob"],
            year=2023,
            citekey="smith2023novel",
            journal="Test Journal",
            volume="15",
            issue="3",
            pages="123-145",
            doi="10.1000/test.2023.123"
        )
    
    @pytest.fixture
    def sample_analysis_result(self):
        """Sample analysis result for testing"""
        return AnalysisResult(
            paper_type="research",
            confidence=0.85,
            sections={
                "abstract": "This paper presents a novel approach to machine learning.",
                "introduction": "Machine learning has become increasingly important. We investigate how to improve model performance.",
                "methods": "We used deep learning techniques with neural networks. The experimental design involved training on large datasets.",
                "results": "Our method achieved 95% accuracy. The results show significant improvement over baseline methods.",
                "discussion": "The practical applications include medical diagnosis and autonomous vehicles.",
                "conclusion": "Future work should explore additional datasets. There are limitations in computational complexity."
            },
            key_concepts=["machine learning", "neural networks", "accuracy", "performance"],
            equations=["y = wx + b", "loss = -log(p)"],
            methodologies=["deep learning", "supervised learning"]
        )
    
    @pytest.fixture
    def mock_template_processor(self):
        """Mock template processor"""
        processor = Mock(spec=TemplateProcessor)
        
        # Mock template
        template = NoteTemplate(
            name="research",
            description="Research template",
            sections=[
                TemplateSection("Metadata", "Paper metadata", True, "citation"),
                TemplateSection("Summary", "Paper summary", True, "text")
            ],
            focus_areas=[FocusType.RESEARCH]
        )
        
        processor.load_template.return_value = template
        processor.render_template.return_value = "# Test Paper\n\nGenerated note content"
        
        return processor
    
    @pytest.fixture
    def mock_content_analyzer(self):
        """Mock content analyzer"""
        analyzer = Mock()
        analyzer.analyze_content.return_value = AnalysisResult(
            paper_type="research",
            confidence=0.85,
            sections={"abstract": "Test abstract"},
            key_concepts=["test", "concept"],
            equations=[],
            methodologies=[]
        )
        return analyzer
    
    def test_init_with_processors(self, mock_template_processor, mock_content_analyzer):
        """Test initialization with provided processors"""
        generator = NoteGenerator(
            template_processor=mock_template_processor,
            content_analyzer=mock_content_analyzer
        )
        
        assert generator.template_processor is mock_template_processor
        assert generator.content_analyzer is mock_content_analyzer
    
    def test_init_without_processors(self):
        """Test initialization without processors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir) / "templates"
            templates_dir.mkdir()
            
            # Create a simple template
            (templates_dir / "balanced.md").write_text("# {{ title }}")
            
            generator = NoteGenerator(templates_dir=str(templates_dir))
            
            assert generator.template_processor is not None
            assert generator.content_analyzer is None
    
    def test_generate_note_with_analyzer(self, mock_template_processor, mock_content_analyzer, sample_metadata):
        """Test note generation with content analyzer"""
        generator = NoteGenerator(
            template_processor=mock_template_processor,
            content_analyzer=mock_content_analyzer
        )
        
        content = "This is test content for the paper."
        result = generator.generate_note(content, sample_metadata, "research", "standard")
        
        assert result == "# Test Paper\n\nGenerated note content"
        mock_content_analyzer.analyze_content.assert_called_once_with(content, "research")
        mock_template_processor.load_template.assert_called_once_with("research")
        mock_template_processor.render_template.assert_called_once()
    
    def test_generate_note_without_analyzer(self, mock_template_processor, sample_metadata):
        """Test note generation without content analyzer"""
        generator = NoteGenerator(template_processor=mock_template_processor)
        
        content = "This is test content for the paper."
        result = generator.generate_note(content, sample_metadata, "research", "standard")
        
        assert result == "# Test Paper\n\nGenerated note content"
        mock_template_processor.load_template.assert_called_once_with("research")
        mock_template_processor.render_template.assert_called_once()
    
    def test_generate_note_with_enum_types(self, mock_template_processor, sample_metadata):
        """Test note generation with enum types"""
        generator = NoteGenerator(template_processor=mock_template_processor)
        
        content = "This is test content for the paper."
        result = generator.generate_note(content, sample_metadata, FocusType.THEORY, DepthType.DEEP)
        
        assert result == "# Test Paper\n\nGenerated note content"
        mock_template_processor.load_template.assert_called_once_with("theory")
    
    def test_generate_note_error_handling(self, sample_metadata):
        """Test error handling in note generation"""
        mock_processor = Mock()
        mock_processor.load_template.side_effect = Exception("Template error")
        
        generator = NoteGenerator(template_processor=mock_processor)
        
        with pytest.raises(NoteGenerationError) as exc_info:
            generator.generate_note("content", sample_metadata, "research", "standard")
        
        assert "Failed to generate note" in str(exc_info.value)
    
    def test_apply_template_success(self, mock_template_processor):
        """Test successful template application"""
        generator = NoteGenerator(template_processor=mock_template_processor)
        
        content = {"title": "Test Title", "content": "Test content"}
        result = generator.apply_template("research", content)
        
        assert result == "# Test Paper\n\nGenerated note content"
        mock_template_processor.load_template.assert_called_once_with("research")
        mock_template_processor.render_template.assert_called_once()
    
    def test_apply_template_error(self):
        """Test template application error handling"""
        mock_processor = Mock()
        mock_processor.load_template.side_effect = Exception("Template not found")
        
        generator = NoteGenerator(template_processor=mock_processor)
        
        with pytest.raises(NoteGenerationError) as exc_info:
            generator.apply_template("nonexistent", {})
        
        assert "Template application failed" in str(exc_info.value)
    
    def test_format_citations_single_author(self):
        """Test citation formatting with single author"""
        generator = NoteGenerator()
        
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John"],
            year=2023,
            journal="Test Journal",
            doi="10.1000/test"
        )
        
        citation = generator.format_citations(metadata)
        
        assert "Smith, John" in citation
        assert "(2023)" in citation
        assert "Test Paper" in citation
        assert "Test Journal" in citation
        assert "10.1000/test" in citation
    
    def test_format_citations_two_authors(self):
        """Test citation formatting with two authors"""
        generator = NoteGenerator()
        
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John", "Doe, Jane"],
            year=2023
        )
        
        citation = generator.format_citations(metadata)
        
        assert "Smith, John and Doe, Jane" in citation
    
    def test_format_citations_multiple_authors(self):
        """Test citation formatting with multiple authors"""
        generator = NoteGenerator()
        
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John", "Doe, Jane", "Johnson, Bob"],
            year=2023
        )
        
        citation = generator.format_citations(metadata)
        
        assert "Smith, John et al." in citation
    
    def test_format_citations_with_volume_issue(self):
        """Test citation formatting with volume and issue"""
        generator = NoteGenerator()
        
        metadata = PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John"],
            year=2023,
            journal="Test Journal",
            volume="15",
            issue="3",
            pages="123-145"
        )
        
        citation = generator.format_citations(metadata)
        
        assert "Vol. 15, No. 3" in citation
        assert "pp. 123-145" in citation
    
    def test_prepare_template_data_with_analysis(self, sample_metadata, sample_analysis_result):
        """Test template data preparation with analysis results"""
        generator = NoteGenerator()
        
        data = generator._prepare_template_data(
            "test content", sample_metadata, sample_analysis_result, 
            FocusType.RESEARCH, DepthType.STANDARD
        )
        
        # Check metadata fields
        assert data["title"] == sample_metadata.title
        assert data["first_author"] == sample_metadata.first_author
        assert data["year"] == sample_metadata.year
        
        # Check analysis-derived fields
        assert "summary" in data
        assert "research_question" in data
        assert "methodology" in data
    
    def test_prepare_template_data_without_analysis(self, sample_metadata):
        """Test template data preparation without analysis results"""
        generator = NoteGenerator()
        
        data = generator._prepare_template_data(
            "test content", sample_metadata, None, 
            FocusType.RESEARCH, DepthType.STANDARD
        )
        
        # Check metadata fields
        assert data["title"] == sample_metadata.title
        assert data["first_author"] == sample_metadata.first_author
        
        # Check fallback fields
        assert "summary" in data
        assert "key_contributions" in data
    
    def test_extract_research_data(self, sample_analysis_result):
        """Test research data extraction"""
        generator = NoteGenerator()
        
        data = generator._extract_research_data(sample_analysis_result, DepthType.STANDARD)
        
        assert "research_question" in data
        assert "methodology" in data
        assert "key_findings" in data
        assert "practical_applications" in data
    
    def test_extract_theory_data(self, sample_analysis_result):
        """Test theory data extraction"""
        generator = NoteGenerator()
        
        data = generator._extract_theory_data(sample_analysis_result, DepthType.STANDARD)
        
        assert "theoretical_framework" in data
        assert "equations" in data
        assert "mathematical_models" in data
        assert "theoretical_contributions" in data
    
    def test_extract_review_data(self, sample_analysis_result):
        """Test review data extraction"""
        generator = NoteGenerator()
        
        data = generator._extract_review_data(sample_analysis_result, DepthType.STANDARD)
        
        assert "scope" in data
        assert "key_themes" in data
        assert "literature_synthesis" in data
        assert "research_gaps" in data
        assert "future_directions" in data
    
    def test_extract_method_data(self, sample_analysis_result):
        """Test method data extraction"""
        generator = NoteGenerator()
        
        data = generator._extract_method_data(sample_analysis_result, DepthType.STANDARD)
        
        assert "method_overview" in data
        assert "experimental_design" in data
        assert "procedures" in data
        assert "validation" in data
        assert "results" in data
    
    def test_extract_balanced_data(self, sample_analysis_result):
        """Test balanced data extraction"""
        generator = NoteGenerator()
        
        data = generator._extract_balanced_data(sample_analysis_result, DepthType.STANDARD)
        
        assert "key_contributions" in data
        assert "methodology" in data
        assert "results" in data
    
    def test_get_template_name_focus_mapping(self):
        """Test template name mapping based on focus"""
        generator = NoteGenerator()
        
        assert generator._get_template_name(FocusType.RESEARCH, None) == "research"
        assert generator._get_template_name(FocusType.THEORY, None) == "theory"
        assert generator._get_template_name(FocusType.REVIEW, None) == "review"
        assert generator._get_template_name(FocusType.METHOD, None) == "method"
        assert generator._get_template_name(FocusType.BALANCED, None) == "balanced"
    
    def test_depth_based_limits(self):
        """Test depth-based item and content limits"""
        generator = NoteGenerator()
        
        # Item limits
        assert generator._get_item_limit(DepthType.QUICK) == 3
        assert generator._get_item_limit(DepthType.STANDARD) == 5
        assert generator._get_item_limit(DepthType.DEEP) == 10
        
        # Content limits
        assert generator._get_content_length(DepthType.QUICK) == 500
        assert generator._get_content_length(DepthType.STANDARD) == 1000
        assert generator._get_content_length(DepthType.DEEP) == 2000
    
    def test_truncate_content(self):
        """Test content truncation"""
        generator = NoteGenerator()
        
        short_content = "Short content"
        long_content = "A" * 1500
        
        # Short content should not be truncated
        result = generator._truncate_content(short_content, DepthType.STANDARD)
        assert result == short_content
        
        # Long content should be truncated
        result = generator._truncate_content(long_content, DepthType.STANDARD)
        assert len(result) <= 1003  # 1000 + "..."
        assert result.endswith("...")
    
    def test_extract_key_points(self):
        """Test key points extraction"""
        generator = NoteGenerator()
        
        content = "First point. Second point. Third point. Fourth point. Fifth point."
        points = generator._extract_key_points(content, DepthType.QUICK)
        
        assert len(points) <= 3  # Quick depth limit
        assert "First point" in points[0]
    
    def test_extract_research_question(self):
        """Test research question extraction"""
        generator = NoteGenerator()
        
        introduction = "This paper investigates the effectiveness of machine learning. We examine how to improve performance."
        question = generator._extract_research_question(introduction)
        
        assert "investigate" in question.lower()
    
    def test_extract_applications(self):
        """Test practical applications extraction"""
        generator = NoteGenerator()
        
        content = "This method can be applied to medical diagnosis. The application in autonomous vehicles is promising."
        applications = generator._extract_applications(content, DepthType.STANDARD)
        
        assert len(applications) > 0
        assert any("medical" in app.lower() for app in applications)


if __name__ == "__main__":
    pytest.main([__file__])