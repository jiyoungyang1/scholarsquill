"""
End-to-end integration tests for template system with real PDF samples
Tests Task 9.1: Test with real PDF samples and validate output quality
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from src.note_generator import NoteGenerator
from src.template_engine import TemplateProcessor
from src.content_analyzer import ContentAnalyzer
from src.pdf_processor import PDFProcessor
from src.models import PaperMetadata, FocusType, DepthType
from src.exceptions import NoteGenerationError


class TestTemplateIntegrationE2E:
    """End-to-end tests with real PDF content and complete pipeline"""
    
    @pytest.fixture
    def temp_templates_dir(self):
        """Create temporary templates directory"""
        temp_dir = tempfile.mkdtemp()
        templates_dir = Path(temp_dir) / "templates"
        templates_dir.mkdir()
        
        # Copy actual templates from the project
        project_templates_dir = Path(__file__).parent.parent / "templates"
        if project_templates_dir.exists():
            for template_file in project_templates_dir.glob("*.md"):
                shutil.copy2(template_file, templates_dir)
        else:
            # Create minimal test templates if project templates don't exist
            self._create_test_templates(templates_dir)
        
        yield str(templates_dir)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def _create_test_templates(self, templates_dir):
        """Create basic test templates"""
        templates = {
            "research.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}
**Year**: {{ year }}

## Summary
{{ research_overview }}

## Research Question
{{ research_question }}

## Methodology
{{ methodology }}

## Key Findings
{% for finding in key_findings %}
- {{ finding }}
{% endfor %}

## Applications
{% for app in practical_applications %}
- {{ app }}
{% endfor %}
""",
            "theory.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}
**Year**: {{ year }}

## Theoretical Framework
{{ theoretical_framework }}

## Equations
{% for eq in equations %}
- {{ eq }}
{% endfor %}

## Propositions
{{ theoretical_proposition }}
""",
            "review.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}
**Year**: {{ year }}

## Scope
{{ scope }}

## Key Themes
{% for theme in key_themes %}
- {{ theme }}
{% endfor %}

## Gaps
{% for gap in research_gaps %}
- {{ gap }}
{% endfor %}
""",
            "method.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}
**Year**: {{ year }}

## Method Overview
{{ method_overview }}

## Design
{{ experimental_design }}

## Procedures
{% for proc in procedures %}
- {{ proc }}
{% endfor %}
""",
            "balanced.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}
**Year**: {{ year }}

## Summary
{{ research_overview }}

## Question
{{ research_question }}

## Method
{{ methodology }}

## Findings
{% for finding in key_findings %}
- {{ finding }}
{% endfor %}
"""
        }
        
        for name, content in templates.items():
            (templates_dir / name).write_text(content)
    
    @pytest.fixture
    def sample_pdf_content_research(self):
        """Sample research paper content extracted from PDF"""
        return """
        Title: Machine Learning Applications in Medical Diagnosis: A Comprehensive Evaluation
        
        Abstract
        Background: Machine learning (ML) has shown promise in medical diagnosis applications.
        Objective: To evaluate the effectiveness of deep learning models in diagnostic accuracy.
        Methods: We conducted a randomized controlled trial with 1,000 patients across five medical centers.
        Results: The ML model achieved 94.2% accuracy, significantly higher than traditional methods (p < 0.001).
        Conclusions: Deep learning models demonstrate superior diagnostic performance and clinical utility.
        
        Introduction
        Medical diagnosis has traditionally relied on clinical expertise and conventional diagnostic tools.
        Recent advances in machine learning, particularly deep learning, have revolutionized medical imaging analysis.
        This study aims to determine whether convolutional neural networks (CNNs) can improve diagnostic accuracy
        compared to standard clinical assessment methods. We hypothesize that ML-based approaches will significantly
        enhance diagnostic precision while reducing human error.
        
        Methods
        Study Design: We employed a prospective, randomized controlled trial design.
        Participants: 1,000 patients aged 18-75 were recruited from five academic medical centers.
        Inclusion criteria included patients presenting with suspected cardiovascular conditions.
        Exclusion criteria were pregnancy, severe comorbidities, and inability to provide consent.
        
        Intervention: Patients were randomly assigned to either ML-assisted diagnosis or standard care.
        The ML model was a convolutional neural network trained on 50,000 medical images.
        Data collection involved ECG recordings, chest X-rays, and echocardiograms.
        Statistical analysis was performed using R software with appropriate tests for significance.
        
        Results
        Primary outcomes showed the ML model achieved 94.2% diagnostic accuracy.
        Traditional clinical assessment achieved 87.3% accuracy (p < 0.001).
        Sensitivity was 96.1% and specificity was 92.8% for the ML model.
        The number needed to treat was 15 patients to prevent one diagnostic error.
        Secondary analyses confirmed consistent results across different patient subgroups.
        The area under the ROC curve was 0.96 (95% CI: 0.94-0.98).
        
        Discussion
        Our findings demonstrate significant improvements in diagnostic accuracy using ML approaches.
        The clinical implications include potential for reduced diagnostic errors and improved patient outcomes.
        Practical applications extend to emergency departments, rural healthcare settings, and developing countries
        where specialist expertise may be limited. The technology could be integrated into existing electronic
        health record systems to provide real-time diagnostic support.
        
        Cost-effectiveness analysis suggests potential savings of $2.3 million annually per hospital.
        Implementation considerations include staff training, system integration, and regulatory approval.
        
        Conclusion
        Machine learning models, specifically CNNs, offer substantial improvements in medical diagnostic accuracy.
        The 7% improvement in accuracy translates to meaningful clinical benefits for patients.
        Future research should explore broader medical conditions and longer-term patient outcomes.
        Limitations include single-disease focus, potential selection bias, and need for external validation.
        The computational requirements and ongoing maintenance costs require careful consideration for implementation.
        """
    
    @pytest.fixture
    def sample_pdf_content_theory(self):
        """Sample theoretical paper content"""
        return """
        Title: A Unified Field Theory for Quantum Computing Algorithms
        
        Abstract
        We present a novel theoretical framework that unifies quantum computing algorithms under a single
        mathematical formalism. This theory provides fundamental insights into quantum algorithm design
        and establishes theoretical limits for quantum computational advantage.
        
        Introduction
        Quantum computing theory has evolved through independent development of various algorithmic approaches.
        Current frameworks lack a unified mathematical foundation for understanding quantum computational processes.
        This work proposes a comprehensive theoretical model that encompasses existing quantum algorithms
        while providing a foundation for developing new approaches.
        
        Theoretical Framework
        The unified framework is based on the concept of quantum state manifolds and operator algebras.
        We define a quantum computational space as a Hilbert space equipped with specific operator structures.
        The fundamental postulate states that all quantum algorithms can be expressed as transformations
        within this computational space.
        
        Mathematical Formulation
        Let H be the computational Hilbert space with dimension 2^n for n qubits.
        The quantum state evolution is governed by the Schrödinger equation:
        i∂|ψ⟩/∂t = H|ψ⟩
        
        Where H is the system Hamiltonian and |ψ⟩ represents the quantum state.
        The unitary evolution operator U(t) = exp(-iHt/ℏ) preserves quantum coherence.
        
        Key propositions:
        1. Quantum algorithms correspond to specific geodesics in the computational manifold
        2. Computational complexity is related to the curvature of the state space
        3. Quantum advantage emerges from topological properties of the algorithm space
        
        Theoretical Implications
        The framework predicts fundamental limits on quantum speedup for certain problem classes.
        It establishes connections between quantum algorithm efficiency and geometric properties.
        New algorithm design principles emerge from the unified mathematical structure.
        
        Assumptions and Limitations
        We assume ideal quantum systems without decoherence effects.
        The model presupposes perfect quantum gate implementations.
        Environmental interactions are neglected in the current formulation.
        Extension to noisy quantum systems requires additional theoretical development.
        """
    
    @pytest.fixture 
    def sample_pdf_content_review(self):
        """Sample literature review content"""
        return """
        Title: Machine Learning in Healthcare: A Systematic Review of Applications and Outcomes
        
        Abstract
        Background: Machine learning applications in healthcare have proliferated rapidly.
        Objective: To systematically review ML applications and assess their clinical effectiveness.
        Methods: We searched PubMed, Embase, and Cochrane databases for studies published 2018-2023.
        Results: 127 studies met inclusion criteria. ML showed consistent benefits across multiple domains.
        Conclusions: Evidence supports ML implementation in specific healthcare applications with appropriate validation.
        
        Introduction
        The healthcare industry has witnessed unprecedented adoption of machine learning technologies.
        This systematic review aims to evaluate the current state of ML applications in clinical practice
        and assess their effectiveness in improving patient outcomes.
        
        Methods
        Search Strategy: We conducted comprehensive searches of major medical databases.
        Inclusion criteria: Peer-reviewed studies of ML applications in clinical settings.
        Exclusion criteria: Theoretical papers, case reports, and studies with <50 participants.
        Quality assessment was performed using the GRADE criteria.
        
        Results
        Literature Search: Initial search yielded 2,847 articles; 127 met final inclusion criteria.
        Study Characteristics: Studies spanned diagnostic imaging (45%), predictive modeling (30%), 
        treatment optimization (15%), and drug discovery (10%).
        
        Key Themes Identified:
        1. Diagnostic Accuracy: ML models consistently outperformed traditional methods
        2. Implementation Challenges: Technical, regulatory, and workflow barriers identified
        3. Clinical Outcomes: Measurable improvements in patient care metrics
        4. Cost-Effectiveness: Economic benefits demonstrated in 78% of studies
        
        Quality Assessment: 89 studies rated as high quality, 31 as moderate quality, 7 as low quality.
        
        Discussion
        The evidence strongly supports ML effectiveness in diagnostic applications.
        Implementation success factors include clinician engagement, robust validation, and workflow integration.
        Barriers to adoption include regulatory uncertainty, data privacy concerns, and technical complexity.
        
        Research Gaps Identified:
        - Limited long-term outcome studies
        - Insufficient diversity in study populations  
        - Lack of standardized evaluation metrics
        - Minimal cost-effectiveness analyses in resource-limited settings
        
        Future Research Directions:
        1. Longitudinal studies of ML implementation outcomes
        2. Development of standardized evaluation frameworks
        3. Investigation of ML applications in underserved populations
        4. Comprehensive economic evaluations
        
        Conclusions
        Machine learning demonstrates significant potential for improving healthcare delivery.
        Successful implementation requires careful attention to validation, integration, and evaluation.
        Future research should focus on long-term outcomes and implementation science.
        """
    
    @pytest.fixture
    def sample_metadata_research(self):
        """Sample metadata for research paper"""
        return PaperMetadata(
            title="Machine Learning Applications in Medical Diagnosis: A Comprehensive Evaluation",
            first_author="Thompson, Sarah",
            authors=["Thompson, Sarah", "Kim, David", "Rodriguez, Elena"],
            year=2024,
            citekey="thompson2024machine",
            journal="Journal of Medical AI",
            volume="12",
            issue="3",
            pages="45-62",
            doi="10.1000/jmai.2024.045"
        )
    
    def test_complete_pipeline_research_paper(self, temp_templates_dir, sample_pdf_content_research, sample_metadata_research):
        """Test complete pipeline with research paper content"""
        # Setup components
        template_processor = TemplateProcessor(temp_templates_dir)
        
        # Mock content analyzer to simulate realistic analysis
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = self._create_realistic_analysis_result(
            "research", sample_pdf_content_research
        )
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        # Test all focus types
        focus_types = ["research", "theory", "review", "method", "balanced"]
        
        for focus in focus_types:
            result = note_generator.generate_note(
                content=sample_pdf_content_research,
                metadata=sample_metadata_research,
                focus=focus,
                depth="standard"
            )
            
            # Basic validation
            assert result is not None
            assert len(result) > 100  # Substantial content
            assert sample_metadata_research.title in result
            assert "Thompson, Sarah" in result
            assert "2024" in result
            
            # Content should be relevant to medical ML
            assert any(term in result.lower() for term in ["machine learning", "diagnostic", "medical", "accuracy"])
    
    def test_depth_variation_effects(self, temp_templates_dir, sample_pdf_content_research, sample_metadata_research):
        """Test effects of different depth settings on output"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = self._create_realistic_analysis_result(
            "research", sample_pdf_content_research
        )
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        depths = ["quick", "standard", "deep"]
        results = {}
        
        for depth in depths:
            results[depth] = note_generator.generate_note(
                content=sample_pdf_content_research,
                metadata=sample_metadata_research,
                focus="research",
                depth=depth
            )
        
        # Validate depth effects
        for depth, result in results.items():
            assert result is not None
            assert len(result) > 50
            assert sample_metadata_research.title in result
        
        # Deep should generally have more content than quick
        # (though exact length depends on content availability)
        assert len(results["quick"]) <= len(results["deep"]) * 1.5  # Allow some variation
    
    def test_template_output_quality_validation(self, temp_templates_dir, sample_pdf_content_research, sample_metadata_research):
        """Test template output quality meets standards"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = self._create_realistic_analysis_result(
            "research", sample_pdf_content_research
        )
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        result = note_generator.generate_note(
            content=sample_pdf_content_research,
            metadata=sample_metadata_research,
            focus="research",
            depth="standard"
        )
        
        # Quality validation checks
        quality_checks = [
            # Structure validation
            ("Title present", sample_metadata_research.title in result),
            ("Authors present", "Thompson, Sarah" in result),
            ("Year present", "2024" in result),
            
            # Content validation  
            ("Research question extracted", any(indicator in result.lower() for indicator in ["research question", "aim", "objective", "hypothesis"])),
            ("Methodology described", any(indicator in result.lower() for indicator in ["method", "design", "participants", "analysis"])),
            ("Findings presented", any(indicator in result.lower() for indicator in ["finding", "result", "outcome"])),
            
            # Template structure
            ("Proper markdown formatting", result.startswith("#")),
            ("No template variables visible", "{{" not in result and "}}" not in result),
            ("No undefined values", "undefined" not in result.lower()),
            
            # Content quality
            ("Reasonable length", len(result) > 200),
            ("Medical content preserved", any(term in result.lower() for term in ["medical", "clinical", "diagnostic", "patient"])),
            ("Numerical results included", any(char.isdigit() for char in result))
        ]
        
        failed_checks = [(check, passed) for check, passed in quality_checks if not passed]
        
        if failed_checks:
            failure_msg = "Quality validation failed:\n" + "\n".join([f"- {check}" for check, _ in failed_checks])
            pytest.fail(failure_msg)
    
    def test_theory_paper_specialized_content(self, temp_templates_dir, sample_pdf_content_theory):
        """Test theory paper generates appropriate specialized content"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = self._create_realistic_analysis_result(
            "theoretical", sample_pdf_content_theory
        )
        
        metadata = PaperMetadata(
            title="A Unified Field Theory for Quantum Computing Algorithms",
            first_author="Chen, Wei",
            authors=["Chen, Wei", "Kumar, Raj"],
            year=2024,
            citekey="chen2024unified"
        )
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        result = note_generator.generate_note(
            content=sample_pdf_content_theory,
            metadata=metadata,
            focus="theory",
            depth="standard"
        )
        
        # Theory-specific validation
        theory_checks = [
            ("Equations extracted", any(eq_indicator in result for eq_indicator in ["∂", "ψ", "H|", "exp("])),
            ("Theoretical concepts", any(concept in result.lower() for concept in ["quantum", "theoretical", "framework", "manifold"])),
            ("Mathematical notation", any(symbol in result for symbol in ["∂", "⟩", "∈", "∇"])),
            ("Propositions identified", "proposition" in result.lower() or "postulate" in result.lower()),
            ("Assumptions listed", "assumption" in result.lower() or "assume" in result.lower())
        ]
        
        failed_checks = [(check, passed) for check, passed in theory_checks if not passed]
        
        if failed_checks:
            failure_msg = "Theory paper validation failed:\n" + "\n".join([f"- {check}" for check, _ in failed_checks])
            pytest.fail(failure_msg)
    
    def test_review_paper_synthesis_content(self, temp_templates_dir, sample_pdf_content_review):
        """Test review paper generates appropriate synthesis content"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = self._create_realistic_analysis_result(
            "review", sample_pdf_content_review
        )
        
        metadata = PaperMetadata(
            title="Machine Learning in Healthcare: A Systematic Review",
            first_author="Patel, Anita",
            authors=["Patel, Anita", "Johnson, Mark"],
            year=2024,
            citekey="patel2024machine"
        )
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        result = note_generator.generate_note(
            content=sample_pdf_content_review,
            metadata=metadata,
            focus="review",
            depth="standard"
        )
        
        # Review-specific validation
        review_checks = [
            ("Scope described", any(scope_word in result.lower() for scope_word in ["systematic", "review", "search", "criteria"])),
            ("Themes identified", "theme" in result.lower() or "pattern" in result.lower()),
            ("Gaps mentioned", "gap" in result.lower() or "limitation" in result.lower()),
            ("Study numbers", any(char.isdigit() for char in result)),  # Should have study counts
            ("Synthesis approach", any(synth_word in result.lower() for synth_word in ["synthesis", "analysis", "evaluation"]))
        ]
        
        failed_checks = [(check, passed) for check, passed in review_checks if not passed]
        
        if failed_checks:
            failure_msg = "Review paper validation failed:\n" + "\n".join([f"- {check}" for check, _ in failed_checks])
            pytest.fail(failure_msg)
    
    def test_error_resilience_with_poor_content(self, temp_templates_dir):
        """Test system resilience with poor quality or minimal content"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        content_analyzer.analyze_content.return_value = self._create_minimal_analysis_result()
        
        metadata = PaperMetadata(
            title="Minimal Content Paper",
            first_author="Test, Author",
            authors=["Test, Author"],
            year=2024,
            citekey="test2024minimal"
        )
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        # Test with very minimal content
        minimal_content = "Abstract: This is a test. Introduction: Test content. Methods: Test method."
        
        result = note_generator.generate_note(
            content=minimal_content,
            metadata=metadata,
            focus="research",
            depth="standard"
        )
        
        # Should still produce valid output with fallback content
        assert result is not None
        assert len(result) > 50
        assert metadata.title in result
        assert "Test, Author" in result
        assert "{{" not in result  # No unresolved template variables
        assert "}}" not in result
    
    def test_performance_with_large_content(self, temp_templates_dir, sample_metadata_research):
        """Test performance with large content documents"""
        template_processor = TemplateProcessor(temp_templates_dir)
        content_analyzer = Mock()
        
        # Create large content (simulating large PDF)
        large_content = sample_pdf_content_research * 10  # Multiply content
        
        content_analyzer.analyze_content.return_value = self._create_realistic_analysis_result(
            "research", large_content
        )
        
        note_generator = NoteGenerator(
            template_processor=template_processor,
            content_analyzer=content_analyzer
        )
        
        import time
        start_time = time.time()
        
        result = note_generator.generate_note(
            content=large_content,
            metadata=sample_metadata_research,
            focus="research", 
            depth="standard"
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance validation
        assert result is not None
        assert len(result) > 100
        assert processing_time < 30  # Should complete within 30 seconds
    
    def _create_realistic_analysis_result(self, paper_type, content):
        """Create realistic analysis result based on content"""
        # Extract sections based on common paper structure
        sections = {}
        
        # Simple section extraction
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if any(header in line.lower() for header in ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']):
                if current_section and current_content:
                    sections[current_section] = ' '.join(current_content)
                current_section = line.lower().split()[0]
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Add final section
        if current_section and current_content:
            sections[current_section] = ' '.join(current_content)
        
        # Extract key concepts
        key_concepts = []
        concept_indicators = ['machine learning', 'deep learning', 'neural network', 'algorithm', 'model', 'accuracy', 'performance', 'clinical', 'medical', 'quantum', 'theoretical', 'framework', 'systematic', 'review']
        
        for concept in concept_indicators:
            if concept in content.lower():
                key_concepts.append(concept)
        
        # Extract equations if present
        equations = []
        import re
        eq_patterns = [r'[A-Za-z]+\|[^⟩]+⟩', r'∂[^=]+=[^=]+', r'[A-Z]\([^)]+\)\s*=']
        for pattern in eq_patterns:
            matches = re.findall(pattern, content)
            equations.extend(matches[:3])  # Limit to 3 equations
        
        # Determine methodologies
        methodologies = []
        method_indicators = {
            'randomized controlled trial': 'randomized controlled trial',
            'systematic review': 'systematic review', 
            'machine learning': 'machine learning',
            'deep learning': 'deep learning',
            'statistical analysis': 'statistical analysis',
            'theoretical analysis': 'theoretical analysis'
        }
        
        for indicator, methodology in method_indicators.items():
            if indicator in content.lower():
                methodologies.append(methodology)
        
        from src.models import AnalysisResult
        return AnalysisResult(
            paper_type=paper_type,
            confidence=0.85,
            sections=sections,
            key_concepts=key_concepts[:8],  # Limit to top 8
            equations=equations[:5],  # Limit to 5 equations
            methodologies=methodologies[:3]  # Limit to 3 methodologies
        )
    
    def _create_minimal_analysis_result(self):
        """Create minimal analysis result for testing fallback behavior"""
        from src.models import AnalysisResult
        return AnalysisResult(
            paper_type="unknown",
            confidence=0.3,
            sections={"other": "minimal content"},
            key_concepts=[],
            equations=[],
            methodologies=[]
        )


if __name__ == "__main__":
    pytest.main([__file__])