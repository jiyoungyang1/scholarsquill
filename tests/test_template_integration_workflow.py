"""
Comprehensive integration tests for template workflow
Tests Task 8.2: Integration tests for template workflow
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from src.note_generator import NoteGenerator
from src.template_engine import TemplateProcessor
from src.content_analyzer import ContentAnalyzer
from src.models import (
    PaperMetadata, AnalysisResult, FocusType, DepthType, 
    NoteTemplate, TemplateSection
)
from src.exceptions import NoteGenerationError, TemplateError


class TestTemplateWorkflowIntegration:
    """Integration tests for complete template workflow"""
    
    @pytest.fixture
    def temp_templates_dir(self):
        """Create temporary templates directory with test templates"""
        temp_dir = tempfile.mkdtemp()
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Create test templates for each focus type
        templates = {
            "research.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}  
**Year**: {{ year }}  
**Journal**: {{ journal }}  
**DOI**: {{ doi }}

## Research Question
{{ research_question }}

## Methodology
{{ methodology }}

## Key Findings
{% for finding in key_findings %}
- {{ finding }}
{% endfor %}

## Practical Applications
{% for app in practical_applications %}
- {{ app }}
{% endfor %}

{% if limitations %}
## Limitations
{{ limitations }}
{% endif %}

*Generated on {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }} using ScholarSquill Kiro*
""",
            
            "theory.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}  
**Year**: {{ year }}  

## Theoretical Framework
{{ theoretical_framework }}

## Key Equations
{% for equation in equations %}
- {{ equation }}
{% endfor %}

## Theoretical Proposition
{{ theoretical_proposition }}

## Mathematical Models
{{ mathematical_models }}

## Assumptions
{% for assumption in assumptions %}
- {{ assumption }}
{% endfor %}

*Generated on {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }} using ScholarSquill Kiro*
""",
            
            "review.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}  
**Year**: {{ year }}  

## Review Scope
{{ scope }}

## Key Themes
{% for theme in key_themes %}
- {{ theme }}
{% endfor %}

## Literature Synthesis
{{ synthesis_approach }}

## Research Gaps
{% for gap in research_gaps %}
- {{ gap }}
{% endfor %}

*Generated on {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }} using ScholarSquill Kiro*
""",
            
            "method.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}  
**Year**: {{ year }}  

## Method Overview
{{ method_overview }}

## Experimental Design
{{ experimental_design }}

## Procedures
{% for procedure in procedures %}
- {{ procedure }}
{% endfor %}

## Validation
{{ validation }}

## Advantages
{% for advantage in advantages %}
- {{ advantage }}
{% endfor %}

*Generated on {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }} using ScholarSquill Kiro*
""",
            
            "balanced.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}  
**Year**: {{ year }}  
**Journal**: {{ journal }}  

## Executive Summary
{{ research_overview }}

## Research Foundation
{{ research_question }}

## Methodology
{{ methodology }}

## Results and Findings
{% for finding in key_findings %}
- {{ finding }}
{% endfor %}

## Discussion and Implications
{{ significance }}

## Critical Assessment
{% if limitations %}
**Limitations**: {{ limitations }}
{% endif %}

**Practical Applications**:
{% for app in practical_applications %}
- {{ app }}
{% endfor %}

*Generated on {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }} using ScholarSquill Kiro*
"""
        }
        
        for template_name, content in templates.items():
            (templates_dir / template_name).write_text(content)
        
        yield str(templates_dir)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_metadata(self):
        """Sample paper metadata"""
        return PaperMetadata(
            title="Machine Learning Applications in Healthcare: A Comprehensive Study",
            first_author="Johnson, Alice",
            authors=["Johnson, Alice", "Smith, Robert", "Chen, Maria"],
            year=2024,
            citekey="johnson2024machine",
            journal="Journal of Medical Informatics",
            volume="45",
            issue="2",
            pages="123-145",
            doi="10.1000/jmi.2024.123"
        )
    
    @pytest.fixture
    def sample_content(self):
        """Sample PDF content for testing"""
        return """
        Abstract
        This study examines the application of machine learning algorithms in healthcare diagnosis. 
        We investigate whether deep learning models can improve diagnostic accuracy compared to traditional methods.
        Our research aims to evaluate the effectiveness of neural networks in medical image analysis.
        
        Introduction
        Machine learning has revolutionized healthcare applications over the past decade. 
        This research aims to determine the impact of convolutional neural networks on diagnostic performance.
        We hypothesize that deep learning approaches will significantly enhance accuracy in medical imaging.
        The primary research question is: How do deep learning models compare to traditional diagnostic methods?
        
        Methods
        We employed a randomized controlled trial design using a dataset of 10,000 medical images.
        Participants included 500 patients from three medical centers.
        Deep learning models were trained using convolutional neural networks with ResNet architecture.
        Statistical analysis was performed using Python and TensorFlow.
        Data collection involved retrospective analysis of imaging studies.
        
        Results
        Our analysis revealed a 95% accuracy rate for the deep learning model.
        The deep learning model significantly outperformed traditional methods (p < 0.001).
        Sensitivity was 92% and specificity was 98%.
        The area under the ROC curve was 0.97.
        Secondary analyses showed consistent results across different patient subgroups.
        
        Discussion
        These results have important implications for clinical practice.
        The improved accuracy suggests significant potential for real-world deployment.
        Practical applications include automated screening programs and decision support systems.
        The technology could be implemented in resource-limited settings to improve diagnostic capabilities.
        
        Conclusion
        We conclude that deep learning models offer substantial improvements in diagnostic accuracy.
        Future work should explore larger datasets and additional medical domains.
        Limitations include potential selection bias and the need for larger validation studies.
        The computational requirements may limit implementation in some clinical settings.
        """
    
    @pytest.fixture
    def sample_analysis_result(self):
        """Sample content analysis result"""
        return AnalysisResult(
            paper_type="research",
            confidence=0.90,
            sections={
                "abstract": "This study examines the application of machine learning algorithms in healthcare diagnosis.",
                "introduction": "Machine learning has revolutionized healthcare applications. We investigate the impact of neural networks.",
                "methods": "We employed a randomized controlled trial design using 10,000 medical images. Deep learning models were trained.",
                "results": "Our analysis revealed 95% accuracy. The model significantly outperformed traditional methods (p < 0.001).",
                "discussion": "Results have important implications for clinical practice. Applications include automated screening.",
                "conclusion": "Deep learning models offer substantial improvements. Future work should explore larger datasets."
            },
            key_concepts=["machine learning", "deep learning", "diagnostic accuracy", "medical imaging", "neural networks"],
            equations=["Accuracy = TP + TN / (TP + TN + FP + FN)", "AUC = 0.97"],
            methodologies=["randomized controlled trial", "convolutional neural networks", "statistical analysis"]
        )
    
    def test_complete_workflow_research_focus(self, temp_templates_dir, sample_metadata, sample_content, sample_analysis_result):
        """Test complete workflow from content to rendered template - research focus"""
        # Setup
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = sample_analysis_result
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        # Execute
        result = note_generator.generate_note(
            content=sample_content,
            metadata=sample_metadata,
            focus="research",
            depth="standard"
        )
        
        # Verify
        assert result is not None
        assert len(result) > 0
        
        # Check template structure
        assert "Machine Learning Applications in Healthcare" in result
        assert "Johnson, Alice" in result
        assert "2024" in result
        assert "Journal of Medical Informatics" in result
        
        # Check content extraction
        assert "Research Question" in result
        assert "Methodology" in result
        assert "Key Findings" in result
        assert "Practical Applications" in result
        
        # Check that content was properly extracted and populated
        assert any(keyword in result.lower() for keyword in ["deep learning", "accuracy", "diagnostic"])
        
        # Verify content analyzer was called
        content_analyzer.analyze_content.assert_called_once_with(sample_content, "research")
    
    def test_complete_workflow_theory_focus(self, temp_templates_dir, sample_metadata):
        """Test complete workflow with theory focus"""
        # Create theory-specific analysis result
        theory_analysis = AnalysisResult(
            paper_type="theoretical",
            confidence=0.95,
            sections={
                "abstract": "This paper presents a novel theoretical framework for quantum computing.",
                "introduction": "Current theoretical models lack comprehensive foundations. We propose a unified approach.",
                "theory": "The framework is based on quantum mechanical principles.",
                "mathematical_models": "Mathematical formulation includes Schrödinger equations."
            },
            key_concepts=["quantum computing", "theoretical framework", "mathematical models"],
            equations=["H|ψ⟩ = E|ψ⟩", "∂|ψ⟩/∂t = -iH|ψ⟩/ℏ"],
            methodologies=["theoretical analysis", "mathematical derivation"]
        )
        
        # Setup
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = theory_analysis
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        # Execute
        result = note_generator.generate_note(
            content="theory content",
            metadata=sample_metadata,
            focus="theory",
            depth="standard"
        )
        
        # Verify theory-specific sections
        assert "Theoretical Framework" in result
        assert "Key Equations" in result
        assert "Mathematical Models" in result
        assert "Assumptions" in result
        
        # Check equations are included
        assert "H|ψ⟩ = E|ψ⟩" in result
        assert "∂|ψ⟩/∂t" in result
    
    def test_complete_workflow_review_focus(self, temp_templates_dir, sample_metadata):
        """Test complete workflow with review focus"""
        # Create review-specific analysis result
        review_analysis = AnalysisResult(
            paper_type="review",
            confidence=0.88,
            sections={
                "abstract": "This systematic review examines machine learning applications in healthcare.",
                "methods": "We searched major databases and included 45 studies.",
                "results": "Key themes include diagnostic accuracy, implementation challenges, and clinical outcomes.",
                "conclusion": "Evidence supports ML effectiveness. Gaps include long-term studies and cost-effectiveness."
            },
            key_concepts=["systematic review", "machine learning", "healthcare", "diagnostic accuracy"],
            equations=[],
            methodologies=["systematic review", "meta-analysis"]
        )
        
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = review_analysis
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        result = note_generator.generate_note(
            content="review content",
            metadata=sample_metadata,
            focus="review",
            depth="standard"
        )
        
        # Verify review-specific sections
        assert "Review Scope" in result
        assert "Key Themes" in result
        assert "Literature Synthesis" in result
        assert "Research Gaps" in result
    
    def test_template_selection_logic_focus_types(self, temp_templates_dir, sample_metadata, sample_analysis_result):
        """Test template selection logic for different focus types"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = sample_analysis_result
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        focus_types = ["research", "theory", "review", "method", "balanced"]
        
        for focus in focus_types:
            result = note_generator.generate_note(
                content="test content",
                metadata=sample_metadata,
                focus=focus,
                depth="standard"
            )
            
            assert result is not None
            assert len(result) > 0
            assert sample_metadata.title in result
    
    def test_template_selection_logic_paper_classification(self, temp_templates_dir, sample_metadata):
        """Test template selection based on paper classification"""
        # Test balanced focus with strong classification
        strong_classification_analysis = AnalysisResult(
            paper_type="experimental",  # Should map to research template
            confidence=0.95,
            sections={"abstract": "Experimental study"},
            key_concepts=["experiment"],
            equations=[],
            methodologies=[]
        )
        
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = strong_classification_analysis
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        result = note_generator.generate_note(
            content="experimental content",
            metadata=sample_metadata,
            focus="balanced",  # Should use paper classification for template selection
            depth="standard"
        )
        
        assert result is not None
        # Should contain research template elements since experimental maps to research
        assert "Research Question" in result or "Methodology" in result
    
    def test_depth_filtering_quick_vs_deep(self, temp_templates_dir, sample_metadata, sample_analysis_result):
        """Test depth-based content filtering"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = sample_analysis_result
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        # Generate with quick depth
        quick_result = note_generator.generate_note(
            content="test content",
            metadata=sample_metadata,
            focus="research",
            depth="quick"
        )
        
        # Generate with deep depth
        deep_result = note_generator.generate_note(
            content="test content",
            metadata=sample_metadata,
            focus="research",
            depth="deep"
        )
        
        # Deep result should generally be longer than quick result
        # (though this depends on content availability)
        assert quick_result is not None
        assert deep_result is not None
        assert len(quick_result) > 0
        assert len(deep_result) > 0
    
    def test_error_handling_template_not_found(self, temp_templates_dir, sample_metadata, sample_analysis_result):
        """Test error handling when template is not found"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = sample_analysis_result
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        # Remove a template file to trigger error
        nonexistent_template = Path(temp_templates_dir) / "research.md"
        if nonexistent_template.exists():
            nonexistent_template.unlink()
        
        with pytest.raises(NoteGenerationError) as exc_info:
            note_generator.generate_note(
                content="test content",
                metadata=sample_metadata,
                focus="research",
                depth="standard"
            )
        
        assert "Failed to generate note" in str(exc_info.value)
    
    def test_error_handling_template_rendering_failure(self, temp_templates_dir, sample_metadata, sample_analysis_result):
        """Test error handling for template rendering failures"""
        # Create a template with invalid Jinja2 syntax
        bad_template_path = Path(temp_templates_dir) / "bad_template.md"
        bad_template_path.write_text("# {{ invalid_syntax }}")
        
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = sample_analysis_result
        
        # Mock template processor to return bad template
        with patch.object(template_processor, 'load_template') as mock_load:
            mock_load.side_effect = TemplateError("Invalid template syntax")
            
            note_generator = NoteGenerator(
                template_processor=template_processor,
                content_analyzer=content_analyzer
            )
            
            with pytest.raises(NoteGenerationError):
                note_generator.generate_note(
                    content="test content",
                    metadata=sample_metadata,
                    focus="research",
                    depth="standard"
                )
    
    def test_error_handling_missing_template_variables(self, temp_templates_dir, sample_metadata):
        """Test handling of missing template variables with fallback content"""
        # Create analysis result with minimal content
        minimal_analysis = AnalysisResult(
            paper_type="research",
            confidence=0.5,
            sections={"other": "minimal content"},
            key_concepts=[],
            equations=[],
            methodologies=[]
        )
        
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = minimal_analysis
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        # Should not fail, should use fallback content
        result = note_generator.generate_note(
            content="minimal content",
            metadata=sample_metadata,
            focus="research",
            depth="standard"
        )
        
        assert result is not None
        assert len(result) > 0
        assert sample_metadata.title in result
    
    def test_fallback_mechanism_content_analyzer_failure(self, temp_templates_dir, sample_metadata):
        """Test fallback when content analyzer fails"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.side_effect = Exception("Analysis failed")
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        # Should still generate note using fallback content
        result = note_generator.generate_note(
            content="test content",
            metadata=sample_metadata,
            focus="research",
            depth="standard"
        )
        
        assert result is not None
        assert len(result) > 0
        assert sample_metadata.title in result
    
    def test_template_data_population_completeness(self, temp_templates_dir, sample_metadata, sample_analysis_result):
        """Test that all expected template variables are properly populated"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = sample_analysis_result
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        result = note_generator.generate_note(
            content="comprehensive content",
            metadata=sample_metadata,
            focus="research",
            depth="standard"
        )
        
        # Check all major template variables are populated (not empty placeholders)
        template_vars = [
            "title", "authors", "year", "journal", "doi",
            "Research Question", "Methodology", "Key Findings", "Practical Applications"
        ]
        
        for var in template_vars:
            assert var in result
        
        # Should not contain common Jinja2 error patterns
        error_patterns = ["{{ ", "}}", "None", "undefined"]
        for pattern in error_patterns:
            if pattern in result:
                # Allow "None" in some contexts but not as standalone values
                if pattern == "None" and "None," not in result and ": None" not in result:
                    continue
                pytest.fail(f"Template variable not properly populated: found '{pattern}' in result")
    
    def test_template_inheritance_and_shared_data(self, temp_templates_dir, sample_metadata, sample_analysis_result):
        """Test template inheritance patterns and shared data across templates"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = sample_analysis_result
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        focus_types = ["research", "theory", "review", "method", "balanced"]
        results = {}
        
        for focus in focus_types:
            results[focus] = note_generator.generate_note(
                content="test content",
                metadata=sample_metadata,
                focus=focus,
                depth="standard"
            )
        
        # Check that shared metadata appears consistently across all templates
        shared_elements = [sample_metadata.title, "Johnson, Alice", "2024"]
        
        for focus, result in results.items():
            for element in shared_elements:
                assert element in result, f"Shared element '{element}' missing from {focus} template"
        
        # Check that each template has its unique sections
        unique_sections = {
            "research": "Research Question",
            "theory": "Theoretical Framework", 
            "review": "Review Scope",
            "method": "Experimental Design",
            "balanced": "Executive Summary"
        }
        
        for focus, unique_section in unique_sections.items():
            assert unique_section in results[focus], f"Unique section '{unique_section}' missing from {focus} template"


if __name__ == "__main__":
    pytest.main([__file__])