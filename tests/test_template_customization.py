"""
Unit tests for template customization and dynamic content features
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from pathlib import Path

from src.template_engine import TemplateProcessor
from src.models import (
    FocusType, DepthType, NoteTemplate, TemplateSection, 
    AnalysisResult, PaperMetadata
)
from src.exceptions import TemplateError, ConfigurationError


class TestTemplateSelection:
    """Test template selection logic"""
    
    @pytest.fixture
    def template_processor(self, tmp_path):
        """Create template processor with test templates"""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        # Create test templates
        for template_name in ["research", "theory", "review", "method", "balanced"]:
            template_file = templates_dir / f"{template_name}.md"
            template_file.write_text(f"# Test {template_name} template\n{{{{ title }}}}")
        
        return TemplateProcessor(str(templates_dir))
    
    def test_select_template_focus_based(self, template_processor):
        """Test template selection based on focus type"""
        # Test each focus type
        assert template_processor.select_template(FocusType.RESEARCH) == "research"
        assert template_processor.select_template(FocusType.THEORY) == "theory"
        assert template_processor.select_template(FocusType.REVIEW) == "review"
        assert template_processor.select_template(FocusType.METHOD) == "method"
    
    def test_select_template_classification_based(self, template_processor):
        """Test template selection based on paper classification"""
        # High confidence classification should override balanced focus
        classification = ("theoretical", 0.85)
        template_name = template_processor.select_template(
            FocusType.BALANCED, classification
        )
        assert template_name == "theory"
        
        # Low confidence should fall back to balanced
        classification = ("research", 0.5)
        template_name = template_processor.select_template(
            FocusType.BALANCED, classification
        )
        assert template_name == "balanced"
    
    def test_select_template_content_inference(self, template_processor):
        """Test template selection based on content analysis"""
        # Create analysis result with equations (should suggest theory template)
        analysis_result = AnalysisResult(
            paper_type="unknown",
            confidence=0.5,
            sections={"introduction": "test"},
            key_concepts=["concept1"],
            equations=["E = mc^2", "F = ma"],
            methodologies=[]
        )
        
        template_name = template_processor.select_template(
            FocusType.BALANCED, None, analysis_result
        )
        assert template_name == "theory"
        
        # Create analysis result with methodologies (should suggest method template)
        analysis_result = AnalysisResult(
            paper_type="unknown",
            confidence=0.5,
            sections={"methods": "detailed methodology"},
            key_concepts=["method1"],
            equations=[],
            methodologies=["experimental design", "statistical analysis"]
        )
        
        template_name = template_processor.select_template(
            FocusType.BALANCED, None, analysis_result
        )
        assert template_name == "method"
    
    def test_select_template_fallback(self, template_processor):
        """Test template selection fallback to balanced"""
        # No classification or analysis should default to balanced
        template_name = template_processor.select_template(FocusType.BALANCED)
        assert template_name == "balanced"


class TestDynamicContent:
    """Test dynamic content inclusion and depth filtering"""
    
    @pytest.fixture
    def template_processor(self, tmp_path):
        """Create template processor with test templates"""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        # Create test template with dynamic content
        template_content = """
# {{ title }}

{% if content_flags.has_equations %}
## Equations
{% for equation in equations | filter_by_depth(depth_type, 'equations') %}
- {{ equation }}
{% endfor %}
{% endif %}

{% if content_flags.section_availability.methods %}
## Methodology
{{ methodology | truncate_smart(depth_limits.max_text_length, depth_type) }}
{% endif %}

## Key Points
{% for point in key_points | filter_by_depth(depth_type, 'items') %}
- {{ point }}
{% endfor %}
"""
        
        template_file = templates_dir / "test.md"
        template_file.write_text(template_content)
        
        return TemplateProcessor(str(templates_dir))
    
    def test_dynamic_content_with_equations(self, template_processor):
        """Test dynamic content inclusion when equations are available"""
        analysis_result = AnalysisResult(
            paper_type="theory",
            confidence=0.8,
            sections={"methods": "This is a detailed methodology section."},
            key_concepts=["concept1", "concept2"],
            equations=["E = mc^2", "F = ma", "a = v^2/r"],
            methodologies=[]
        )
        
        template_data = {
            "title": "Test Paper",
            "equations": analysis_result.equations,
            "methodology": analysis_result.sections["methods"],
            "key_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"]
        }
        
        template = template_processor.load_template("test")
        rendered = template_processor.render_template_with_dynamic_content(
            template, template_data, DepthType.QUICK, analysis_result
        )
        
        # Should include equations section
        assert "## Equations" in rendered
        assert "E = mc^2" in rendered
        
        # Should include methodology section
        assert "## Methodology" in rendered
        assert "detailed methodology" in rendered
        
        # Should limit key points based on depth (quick = 3 items)
        lines = rendered.split('\n')
        key_point_lines = [line for line in lines if line.startswith('- Point')]
        assert len(key_point_lines) == 3
    
    def test_dynamic_content_without_equations(self, template_processor):
        """Test dynamic content exclusion when equations are not available"""
        analysis_result = AnalysisResult(
            paper_type="research",
            confidence=0.8,
            sections={},
            key_concepts=["concept1"],
            equations=[],
            methodologies=[]
        )
        
        template_data = {
            "title": "Test Paper",
            "equations": [],
            "methodology": "",
            "key_points": ["Point 1", "Point 2"]
        }
        
        template = template_processor.load_template("test")
        rendered = template_processor.render_template_with_dynamic_content(
            template, template_data, DepthType.STANDARD, analysis_result
        )
        
        # Should not include equations section
        assert "## Equations" not in rendered
        
        # Should not include methodology section (no content)
        assert "## Methodology" not in rendered
    
    def test_depth_based_filtering(self, template_processor):
        """Test content filtering based on depth type"""
        analysis_result = AnalysisResult(
            paper_type="research",
            confidence=0.8,
            sections={"methods": "A very long methodology section that should be truncated based on depth settings."},
            key_concepts=["concept1"],
            equations=["eq1", "eq2", "eq3", "eq4", "eq5", "eq6"],
            methodologies=[]
        )
        
        template_data = {
            "title": "Test Paper",
            "equations": analysis_result.equations,
            "methodology": analysis_result.sections["methods"],
            "key_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5", "Point 6", "Point 7"]
        }
        
        template = template_processor.load_template("test")
        
        # Test QUICK depth (should limit to 2 equations, 3 key points)
        rendered_quick = template_processor.render_template_with_dynamic_content(
            template, template_data, DepthType.QUICK, analysis_result
        )
        
        # Count equations in rendered output
        eq_lines = [line for line in rendered_quick.split('\n') if line.startswith('- eq')]
        assert len(eq_lines) == 2  # Quick depth limit
        
        # Count key points
        point_lines = [line for line in rendered_quick.split('\n') if line.startswith('- Point')]
        assert len(point_lines) == 3  # Quick depth limit
        
        # Test DEEP depth (should allow more content)
        rendered_deep = template_processor.render_template_with_dynamic_content(
            template, template_data, DepthType.DEEP, analysis_result
        )
        
        eq_lines_deep = [line for line in rendered_deep.split('\n') if line.startswith('- eq')]
        assert len(eq_lines_deep) > len(eq_lines)  # Should have more equations


class TestTemplateInheritance:
    """Test template inheritance system"""
    
    @pytest.fixture
    def template_processor(self, tmp_path):
        """Create template processor for inheritance testing"""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        template_file = templates_dir / "test.md"
        template_file.write_text("# {{ title }}\n{{ formatted_citation }}")
        
        return TemplateProcessor(str(templates_dir))
    
    def test_create_template_inheritance_data(self, template_processor):
        """Test creation of shared template inheritance data"""
        base_data = {
            "title": "Test Paper",
            "first_author": "Smith, John",
            "authors": ["Smith, John", "Doe, Jane"],
            "year": 2023,
            "journal": "Test Journal",
            "volume": "10",
            "issue": "2",
            "pages": "123-145",
            "doi": "10.1000/test",
            "generated_at": datetime.now()
        }
        
        enhanced_data = template_processor.create_template_inheritance_data(base_data)
        
        # Check metadata section
        assert "metadata_section" in enhanced_data
        assert enhanced_data["metadata_section"]["title"] == "Test Paper"
        assert enhanced_data["metadata_section"]["first_author"] == "Smith, John"
        
        # Check formatted citation
        assert "formatted_citation" in enhanced_data
        citation = enhanced_data["formatted_citation"]
        assert "Smith, John and Doe, Jane" in citation
        assert "(2023)" in citation
        assert "Test Journal" in citation
        
        # Check generation info
        assert "generation_info" in enhanced_data
        assert enhanced_data["generation_info"]["generator"] == "ScholarSquill Kiro"


class TestTemplateHelperFunctions:
    """Test Jinja2 template helper functions"""
    
    @pytest.fixture
    def template_processor(self, tmp_path):
        """Create template processor for helper function testing"""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        return TemplateProcessor(str(templates_dir))
    
    def test_has_content_function(self, template_processor):
        """Test has_content helper function"""
        assert template_processor._has_content("test content") == True
        assert template_processor._has_content("") == False
        assert template_processor._has_content("   ") == False
        assert template_processor._has_content(None) == False
        assert template_processor._has_content([1, 2, 3]) == True
        assert template_processor._has_content([]) == False
        assert template_processor._has_content({"key": "value"}) == True
        assert template_processor._has_content({}) == False
    
    def test_filter_by_depth_function(self, template_processor):
        """Test filter_by_depth helper function"""
        items = ["item1", "item2", "item3", "item4", "item5"]
        
        # Test quick depth
        filtered_quick = template_processor._filter_by_depth(items, "quick", "items")
        assert len(filtered_quick) == 3
        
        # Test standard depth
        filtered_standard = template_processor._filter_by_depth(items, "standard", "items")
        assert len(filtered_standard) == 5
        
        # Test deep depth
        filtered_deep = template_processor._filter_by_depth(items, "deep", "items")
        assert len(filtered_deep) == 5  # All items since list is shorter than limit
    
    def test_format_list_function(self, template_processor):
        """Test format_list helper function"""
        items = ["item1", "item2", "item3"]
        
        # Test bullet format
        bullet_list = template_processor._format_list(items, "bullet")
        assert bullet_list == "- item1\n- item2\n- item3"
        
        # Test numbered format
        numbered_list = template_processor._format_list(items, "numbered")
        assert numbered_list == "1. item1\n2. item2\n3. item3"
        
        # Test default format
        default_list = template_processor._format_list(items)
        assert default_list == "- item1\n- item2\n- item3"
    
    def test_truncate_smart_function(self, template_processor):
        """Test truncate_smart helper function"""
        text = "This is a test sentence. This is another sentence. And one more."
        
        # Test truncation at sentence boundary
        truncated = template_processor._truncate_smart(text, 30)
        assert truncated == "This is a test sentence."
        
        # Test truncation when no good boundary exists
        short_text = "This is a very short text"
        truncated_short = template_processor._truncate_smart(short_text, 100)
        assert truncated_short == short_text  # Should not truncate
        
        # Test truncation with ellipsis
        truncated_ellipsis = template_processor._truncate_smart(text, 15)
        assert truncated_ellipsis.endswith("...")
    
    def test_conditional_section_function(self, template_processor):
        """Test conditional_section helper function"""
        content = "This is the main content"
        fallback = "This is fallback content"
        
        # Test with true condition
        result_true = template_processor._conditional_section(True, content, fallback)
        assert result_true == content
        
        # Test with false condition
        result_false = template_processor._conditional_section(False, content, fallback)
        assert result_false == fallback
        
        # Test with false condition and no fallback
        result_no_fallback = template_processor._conditional_section(False, content)
        assert result_no_fallback == ""


class TestTemplateCustomizationIntegration:
    """Integration tests for template customization features"""
    
    @pytest.fixture
    def template_processor(self, tmp_path):
        """Create template processor with realistic templates"""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        # Create a realistic template with dynamic content
        template_content = """
# {{ title }}

> [!Metadata]
> **Title**:: {{ title }}
> **Authors**:: {{ authors | join(', ') }}
> **Year**:: {{ year }}

## Summary
{{ summary | truncate_smart(depth_limits.max_text_length, depth_type) }}

{% if content_flags.has_equations and equations %}
## Key Equations
{% for equation in equations | filter_by_depth(depth_type, 'equations') %}
- {{ equation }}
{% endfor %}
{% endif %}

{% if content_flags.section_availability.methods %}
## Methodology
{{ methodology }}
{% endif %}

## Key Findings
{% for finding in key_findings | filter_by_depth(depth_type, 'items') %}
- {{ finding }}
{% endfor %}

---
*Generated on {{ generated_at.strftime('%Y-%m-%d') }} using {{ generation_info.generator }}*
"""
        
        template_file = templates_dir / "research.md"
        template_file.write_text(template_content)
        
        return TemplateProcessor(str(templates_dir))
    
    def test_full_template_customization_workflow(self, template_processor):
        """Test complete template customization workflow"""
        # Create realistic analysis result
        analysis_result = AnalysisResult(
            paper_type="research",
            confidence=0.9,
            sections={
                "methods": "We used a randomized controlled trial design...",
                "results": "The results showed significant improvements..."
            },
            key_concepts=["machine learning", "neural networks", "classification"],
            equations=["loss = -log(p)", "accuracy = TP/(TP+FP)"],
            methodologies=["cross-validation", "statistical testing"]
        )
        
        # Create template data
        template_data = {
            "title": "Advanced Machine Learning Techniques",
            "authors": ["Smith, John", "Doe, Jane", "Johnson, Bob"],
            "year": 2023,
            "summary": "This paper presents novel machine learning techniques for classification tasks. The proposed methods show significant improvements over existing approaches.",
            "equations": analysis_result.equations,
            "methodology": analysis_result.sections["methods"],
            "key_findings": [
                "Improved accuracy by 15%",
                "Reduced training time by 30%",
                "Better generalization performance",
                "Robust to noisy data",
                "Scalable to large datasets"
            ],
            "generated_at": datetime(2023, 12, 1, 10, 30, 0)
        }
        
        # Test with different depth levels
        template = template_processor.load_template("research")
        
        # Quick depth - should limit content
        rendered_quick = template_processor.render_template_with_dynamic_content(
            template, template_data, DepthType.QUICK, analysis_result
        )
        
        assert "Advanced Machine Learning Techniques" in rendered_quick
        assert "Smith, John, Doe, Jane, Johnson, Bob" in rendered_quick
        assert "## Key Equations" in rendered_quick
        assert "loss = -log(p)" in rendered_quick
        assert "## Methodology" in rendered_quick
        assert "randomized controlled trial" in rendered_quick
        
        # Check that key findings are limited (quick = 3 items)
        finding_lines = [line for line in rendered_quick.split('\n') if line.startswith('- Improved') or line.startswith('- Reduced') or line.startswith('- Better')]
        assert len(finding_lines) <= 3
        
        # Deep depth - should include more content
        rendered_deep = template_processor.render_template_with_dynamic_content(
            template, template_data, DepthType.DEEP, analysis_result
        )
        
        # Should have more key findings
        finding_lines_deep = [line for line in rendered_deep.split('\n') if line.startswith('- Improved') or line.startswith('- Reduced') or line.startswith('- Better') or line.startswith('- Robust') or line.startswith('- Scalable')]
        assert len(finding_lines_deep) > len(finding_lines)
        
        # Check generation metadata
        assert "Generated on 2023-12-01" in rendered_deep
        assert "ScholarSquill Kiro" in rendered_deep
    
    def test_template_without_optional_content(self, template_processor):
        """Test template rendering when optional content is missing"""
        # Analysis result without equations
        analysis_result = AnalysisResult(
            paper_type="research",
            confidence=0.8,
            sections={},  # No methods section
            key_concepts=["concept1"],
            equations=[],  # No equations
            methodologies=[]
        )
        
        template_data = {
            "title": "Simple Research Paper",
            "authors": ["Author, Test"],
            "year": 2023,
            "summary": "A simple research paper without complex content.",
            "equations": [],
            "methodology": "",
            "key_findings": ["Finding 1", "Finding 2"],
            "generated_at": datetime.now()
        }
        
        template = template_processor.load_template("research")
        rendered = template_processor.render_template_with_dynamic_content(
            template, template_data, DepthType.STANDARD, analysis_result
        )
        
        # Should not include equations section
        assert "## Key Equations" not in rendered
        
        # Should not include methodology section
        assert "## Methodology" not in rendered
        
        # Should still include basic content
        assert "Simple Research Paper" in rendered
        assert "Finding 1" in rendered
        assert "Finding 2" in rendered


if __name__ == "__main__":
    pytest.main([__file__])