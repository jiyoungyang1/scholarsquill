"""
Unit tests for template engine
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.template_engine import TemplateProcessor
from src.models import NoteTemplate, TemplateSection, FocusType, PaperMetadata
from src.exceptions import TemplateError, ConfigurationError


class TestTemplateProcessor:
    """Test cases for TemplateProcessor class"""
    
    @pytest.fixture
    def temp_templates_dir(self):
        """Create temporary templates directory"""
        temp_dir = tempfile.mkdtemp()
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Create a simple test template
        test_template = templates_dir / "test.md"
        test_template.write_text("# {{ title }}\n\n{{ content }}")
        
        yield str(templates_dir)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_metadata(self):
        """Sample paper metadata for testing"""
        return PaperMetadata(
            title="Test Paper",
            first_author="Smith, John",
            authors=["Smith, John", "Doe, Jane"],
            year=2023,
            citekey="smith2023test",
            journal="Test Journal",
            doi="10.1000/test"
        )
    
    def test_init_valid_directory(self, temp_templates_dir):
        """Test initialization with valid templates directory"""
        processor = TemplateProcessor(temp_templates_dir)
        assert processor.templates_dir == Path(temp_templates_dir)
        assert processor.env is not None
    
    def test_init_invalid_directory(self):
        """Test initialization with invalid directory"""
        with pytest.raises(ConfigurationError):
            TemplateProcessor("/nonexistent/directory")
    
    def test_list_available_templates(self, temp_templates_dir):
        """Test listing available templates"""
        processor = TemplateProcessor(temp_templates_dir)
        templates = processor.list_available_templates()
        assert "test" in templates
    
    def test_list_available_templates_empty_directory(self):
        """Test listing templates in empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = TemplateProcessor(temp_dir)
            templates = processor.list_available_templates()
            assert templates == []
    
    def test_load_template_success(self, temp_templates_dir):
        """Test successful template loading"""
        processor = TemplateProcessor(temp_templates_dir)
        template = processor.load_template("test")
        
        assert isinstance(template, NoteTemplate)
        assert template.name == "test"
        assert template.description is not None
    
    def test_load_template_not_found(self, temp_templates_dir):
        """Test loading non-existent template"""
        processor = TemplateProcessor(temp_templates_dir)
        
        with pytest.raises(TemplateError) as exc_info:
            processor.load_template("nonexistent")
        
        assert "not found" in str(exc_info.value)
    
    def test_load_template_caching(self, temp_templates_dir):
        """Test template caching functionality"""
        processor = TemplateProcessor(temp_templates_dir)
        
        # Load template twice
        template1 = processor.load_template("test")
        template2 = processor.load_template("test")
        
        # Should be the same object from cache
        assert template1 is template2
    
    def test_render_template_success(self, temp_templates_dir, sample_metadata):
        """Test successful template rendering"""
        processor = TemplateProcessor(temp_templates_dir)
        template = processor.load_template("test")
        
        data = {
            "title": "Test Title",
            "content": "Test content",
            "first_author": sample_metadata.first_author,
            "authors": sample_metadata.authors,
            "year": sample_metadata.year,
            "citekey": sample_metadata.citekey,
            "item_type": sample_metadata.item_type,
            "journal": sample_metadata.journal,
            "doi": sample_metadata.doi,
            "generated_at": datetime.now()
        }
        
        result = processor.render_template(template, data)
        
        assert "Test Title" in result
        assert "Test content" in result
    
    def test_render_template_missing_data(self, temp_templates_dir):
        """Test template rendering with missing data"""
        processor = TemplateProcessor(temp_templates_dir)
        template = processor.load_template("test")
        
        # Missing required data
        data = {"title": "Test Title"}
        
        # Should not raise error, Jinja2 handles missing variables gracefully
        result = processor.render_template(template, data)
        assert "Test Title" in result
    
    def test_clear_cache(self, temp_templates_dir):
        """Test cache clearing functionality"""
        processor = TemplateProcessor(temp_templates_dir)
        
        # Load template to populate cache
        processor.load_template("test")
        assert len(processor._template_cache) > 0
        assert len(processor._note_template_cache) > 0
        
        # Clear cache
        processor.clear_cache()
        assert len(processor._template_cache) == 0
        assert len(processor._note_template_cache) == 0
    
    def test_validate_template_directory_valid(self, temp_templates_dir):
        """Test validation of valid template directory"""
        processor = TemplateProcessor(temp_templates_dir)
        assert processor.validate_template_directory() is True
    
    def test_validate_template_directory_nonexistent(self):
        """Test validation of non-existent directory"""
        processor = TemplateProcessor("/nonexistent")
        # Should not raise error during init, but validation should fail
        with patch.object(processor, 'templates_dir', Path("/nonexistent")):
            assert processor.validate_template_directory() is False
    
    def test_validate_template_directory_empty(self):
        """Test validation of empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = TemplateProcessor(temp_dir)
            assert processor.validate_template_directory() is False
    
    def test_create_note_template_research(self, temp_templates_dir):
        """Test creation of research note template"""
        # Create research template file
        research_template = Path(temp_templates_dir) / "research.md"
        research_template.write_text("# {{ title }}")
        
        processor = TemplateProcessor(temp_templates_dir)
        template = processor.load_template("research")
        
        assert template.name == "research"
        assert FocusType.RESEARCH in template.focus_areas
        assert len(template.sections) > 0
        
        # Check for expected sections
        section_titles = [section.title for section in template.sections]
        assert "Metadata" in section_titles
        assert "Summary" in section_titles
        assert "Research Question" in section_titles
        assert "Methodology" in section_titles
    
    def test_create_note_template_theory(self, temp_templates_dir):
        """Test creation of theory note template"""
        # Create theory template file
        theory_template = Path(temp_templates_dir) / "theory.md"
        theory_template.write_text("# {{ title }}")
        
        processor = TemplateProcessor(temp_templates_dir)
        template = processor.load_template("theory")
        
        assert template.name == "theory"
        assert FocusType.THEORY in template.focus_areas
        
        # Check for expected sections
        section_titles = [section.title for section in template.sections]
        assert "Key Equations" in section_titles
        assert "Mathematical Models" in section_titles
        assert "Theoretical Framework" in section_titles
    
    def test_create_note_template_review(self, temp_templates_dir):
        """Test creation of review note template"""
        # Create review template file
        review_template = Path(temp_templates_dir) / "review.md"
        review_template.write_text("# {{ title }}")
        
        processor = TemplateProcessor(temp_templates_dir)
        template = processor.load_template("review")
        
        assert template.name == "review"
        assert FocusType.REVIEW in template.focus_areas
        
        # Check for expected sections
        section_titles = [section.title for section in template.sections]
        assert "Scope" in section_titles
        assert "Literature Synthesis" in section_titles
        assert "Research Gaps" in section_titles
    
    def test_create_note_template_method(self, temp_templates_dir):
        """Test creation of method note template"""
        # Create method template file
        method_template = Path(temp_templates_dir) / "method.md"
        method_template.write_text("# {{ title }}")
        
        processor = TemplateProcessor(temp_templates_dir)
        template = processor.load_template("method")
        
        assert template.name == "method"
        assert FocusType.METHOD in template.focus_areas
        
        # Check for expected sections
        section_titles = [section.title for section in template.sections]
        assert "Method Overview" in section_titles
        assert "Experimental Design" in section_titles
        assert "Procedures" in section_titles
    
    def test_create_note_template_balanced(self, temp_templates_dir):
        """Test creation of balanced note template"""
        # Create balanced template file
        balanced_template = Path(temp_templates_dir) / "balanced.md"
        balanced_template.write_text("# {{ title }}")
        
        processor = TemplateProcessor(temp_templates_dir)
        template = processor.load_template("balanced")
        
        assert template.name == "balanced"
        assert FocusType.BALANCED in template.focus_areas
        
        # Check for expected sections
        section_titles = [section.title for section in template.sections]
        assert "Key Contributions" in section_titles
        assert "Methodology" in section_titles
        assert "Results" in section_titles
    
    def test_create_note_template_unknown(self, temp_templates_dir):
        """Test creation of unknown template defaults to balanced"""
        # Create unknown template file
        unknown_template = Path(temp_templates_dir) / "unknown.md"
        unknown_template.write_text("# {{ title }}")
        
        processor = TemplateProcessor(temp_templates_dir)
        template = processor.load_template("unknown")
        
        assert template.name == "unknown"
        # Should default to balanced template structure
        assert FocusType.BALANCED in template.focus_areas


if __name__ == "__main__":
    pytest.main([__file__])