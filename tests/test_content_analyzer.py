"""
Unit tests for ContentAnalyzer class
"""

import pytest
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from content_analyzer import ContentAnalyzer
from models import AnalysisResult, FocusType


class TestContentAnalyzer:
    """Test cases for ContentAnalyzer class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = ContentAnalyzer()
    
    def test_init(self):
        """Test ContentAnalyzer initialization"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, '_paper_type_keywords')
        assert hasattr(self.analyzer, '_section_patterns')
        assert hasattr(self.analyzer, '_focus_keywords')
        
        # Check that all expected paper types are present
        expected_types = ['research', 'theory', 'review', 'method']
        for paper_type in expected_types:
            assert paper_type in self.analyzer._paper_type_keywords
    
    def test_classify_paper_type_research(self):
        """Test classification of research papers"""
        research_text = """
        This study presents an experimental investigation of protein folding.
        We conducted experiments with 100 participants and analyzed the data
        using statistical methods. The results show significant findings
        that support our hypothesis. Our empirical observations demonstrate
        clear patterns in the experimental data.
        """
        
        paper_type, confidence = self.analyzer.classify_paper_type(research_text)
        
        assert paper_type == 'research'
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.3  # Should have reasonable confidence
    
    def test_classify_paper_type_theory(self):
        """Test classification of theoretical papers"""
        theory_text = """
        This paper presents a theoretical framework for understanding
        quantum mechanics. We derive mathematical equations and prove
        several theorems. The theoretical model is based on fundamental
        principles and provides analytical solutions. Our mathematical
        derivation shows that the theoretical predictions match observations.
        """
        
        paper_type, confidence = self.analyzer.classify_paper_type(theory_text)
        
        assert paper_type == 'theory'
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.3
    
    def test_classify_paper_type_review(self):
        """Test classification of review papers"""
        review_text = """
        This comprehensive review surveys recent advances in machine learning.
        We provide a systematic overview of the literature and synthesize
        findings from multiple studies. This meta-analysis covers the
        state-of-the-art methods and provides a comprehensive summary
        of recent progress in the field.
        """
        
        paper_type, confidence = self.analyzer.classify_paper_type(review_text)
        
        assert paper_type == 'review'
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.3
    
    def test_classify_paper_type_method(self):
        """Test classification of methodology papers"""
        method_text = """
        We present a new methodology for protein analysis. This technique
        improves upon existing approaches and provides better validation.
        Our algorithm implementation shows significant optimization over
        previous methods. The procedure involves several steps that we
        describe in detail, including protocol development and validation.
        """
        
        paper_type, confidence = self.analyzer.classify_paper_type(method_text)
        
        assert paper_type == 'method'
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.3
    
    def test_classify_paper_type_empty_text(self):
        """Test classification with empty text"""
        paper_type, confidence = self.analyzer.classify_paper_type("")
        
        assert paper_type == 'research'  # Default
        assert confidence == 0.5  # Default confidence
    
    def test_classify_paper_type_ambiguous(self):
        """Test classification with ambiguous text"""
        ambiguous_text = "This is a short text without clear indicators."
        
        paper_type, confidence = self.analyzer.classify_paper_type(ambiguous_text)
        
        assert paper_type in ['research', 'theory', 'review', 'method']
        assert 0.0 <= confidence <= 1.0
    
    def test_extract_sections_with_headers(self):
        """Test section extraction with clear headers"""
        text_with_sections = """
        Title: Test Paper
        
        Abstract
        This is the abstract section with important summary information.
        It describes the main contributions and findings of the paper.
        
        Introduction
        This is the introduction section that provides background information.
        It motivates the work and describes the problem being addressed.
        
        Methods
        This section describes the experimental methodology used in the study.
        It includes details about the experimental setup and procedures.
        
        Results
        This section presents the findings from the experiments.
        The data shows clear trends and significant results.
        
        Conclusion
        This section summarizes the main findings and their implications.
        It also discusses future work and limitations.
        """
        
        sections = self.analyzer.extract_sections(text_with_sections)
        
        assert isinstance(sections, dict)
        assert 'abstract' in sections
        assert 'introduction' in sections
        assert 'methods' in sections
        assert 'results' in sections
        assert 'conclusion' in sections
        
        # Check content quality
        assert len(sections['abstract']) > 50
        assert 'summary information' in sections['abstract']
        assert 'background information' in sections['introduction']
    
    def test_extract_sections_no_clear_headers(self):
        """Test section extraction without clear headers"""
        text_without_headers = """
        This is a paper without clear section headers. It contains
        various information but doesn't follow standard academic format.
        The content is mixed and doesn't have obvious section boundaries.
        """
        
        sections = self.analyzer.extract_sections(text_without_headers)
        
        assert isinstance(sections, dict)
        # Should handle gracefully, might be empty or have minimal sections
    
    def test_extract_key_concepts_research_focus(self):
        """Test key concept extraction with research focus"""
        research_text = """
        This experimental study analyzes data from statistical measurements.
        We conducted empirical observations and found significant results.
        The analysis shows clear patterns in the experimental findings.
        """
        
        concepts = self.analyzer.extract_key_concepts(research_text, 'research')
        
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        
        # Should include research-related concepts
        research_concepts = ['experimental', 'data', 'statistical', 'empirical', 'analysis']
        found_research_concepts = [c for c in concepts if c in research_concepts]
        assert len(found_research_concepts) > 0
    
    def test_extract_key_concepts_theory_focus(self):
        """Test key concept extraction with theory focus"""
        theory_text = """
        This theoretical framework presents mathematical equations and models.
        We derive theoretical principles and provide analytical proofs.
        The mathematical derivation shows theoretical predictions.
        """
        
        concepts = self.analyzer.extract_key_concepts(theory_text, 'theory')
        
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        
        # Should include theory-related concepts
        theory_concepts = ['theoretical', 'mathematical', 'equation', 'model', 'principle']
        found_theory_concepts = [c for c in concepts if c in theory_concepts]
        assert len(found_theory_concepts) > 0
    
    def test_extract_key_concepts_balanced_focus(self):
        """Test key concept extraction with balanced focus"""
        mixed_text = """
        This study combines theoretical models with experimental data.
        We use mathematical equations and conduct empirical analysis.
        The methodology involves both theoretical and practical approaches.
        """
        
        concepts = self.analyzer.extract_key_concepts(mixed_text, 'balanced')
        
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        
        # Should include concepts from multiple areas
        all_concepts = ['theoretical', 'experimental', 'mathematical', 'empirical', 'analysis', 'methodology']
        found_concepts = [c for c in concepts if c in all_concepts]
        assert len(found_concepts) > 2  # Should find concepts from multiple areas
    
    def test_extract_key_concepts_invalid_focus(self):
        """Test key concept extraction with invalid focus"""
        text = "This is a test text with various concepts."
        
        concepts = self.analyzer.extract_key_concepts(text, 'invalid_focus')
        
        assert isinstance(concepts, list)
        # Should default to balanced approach
    
    def test_analyze_content_complete(self):
        """Test complete content analysis"""
        test_text = """
        Abstract
        This experimental study investigates protein folding using statistical analysis.
        
        Introduction
        Protein folding is a fundamental process in biology. Previous theoretical
        models have provided mathematical frameworks for understanding this process.
        
        Methods
        We used molecular dynamics simulations and experimental validation.
        The methodology involves computational modeling and laboratory experiments.
        
        Results
        Our analysis shows E = mc² and other significant equations.
        The data demonstrates clear patterns with p < 0.05 statistical significance.
        
        Conclusion
        This study provides new insights into protein folding mechanisms.
        """
        
        result = self.analyzer.analyze_content(test_text, 'balanced')
        
        assert isinstance(result, AnalysisResult)
        assert result.paper_type in ['research', 'theory', 'review', 'method']
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.sections, dict)
        assert isinstance(result.key_concepts, list)
        assert isinstance(result.equations, list)
        assert isinstance(result.methodologies, list)
        
        # Should have found some sections
        assert len(result.sections) > 0
        
        # Should have found some concepts
        assert len(result.key_concepts) > 0
    
    def test_extract_equations(self):
        """Test equation extraction"""
        text_with_equations = """
        The fundamental equation is E = mc².
        We also have the Schrödinger equation: $\\hat{H}\\psi = E\\psi$.
        Display equation: $$F = ma$$
        Another equation: velocity = distance / time
        Function definition: f(x) = x² + 2x + 1
        """
        
        equations = self.analyzer._extract_equations(text_with_equations)
        
        assert isinstance(equations, list)
        assert len(equations) > 0
        
        # Should find various types of equations
        equation_text = ' '.join(equations)
        assert 'E = mc²' in equation_text or 'E=mc²' in equation_text
    
    def test_extract_methodologies(self):
        """Test methodology extraction"""
        text_with_methods = """
        We used machine learning techniques for analysis.
        The study employed statistical analysis and regression analysis.
        Authors applied molecular dynamics simulations.
        We utilized deep learning methods for classification.
        The methodology involved experimental design and monte carlo methods.
        """
        
        methodologies = self.analyzer._extract_methodologies(text_with_methods)
        
        assert isinstance(methodologies, list)
        assert len(methodologies) > 0
        
        # Should find specific methodologies
        method_text = ' '.join(methodologies).lower()
        expected_methods = ['machine learning', 'statistical analysis', 'molecular dynamics']
        found_methods = [m for m in expected_methods if m in method_text]
        assert len(found_methods) > 0
    
    def test_analyze_content_theory_focus(self):
        """Test analysis with theory focus"""
        theory_text = """
        This theoretical paper presents mathematical models and equations.
        We derive E = mc² and other fundamental equations.
        The theoretical framework provides analytical solutions.
        """
        
        result = self.analyzer.analyze_content(theory_text, 'theory')
        
        assert isinstance(result, AnalysisResult)
        assert len(result.equations) > 0  # Should extract equations for theory focus
        # Methodologies might be empty or minimal for theory focus
    
    def test_analyze_content_method_focus(self):
        """Test analysis with method focus"""
        method_text = """
        This paper presents a new methodology using machine learning.
        We employed statistical analysis and experimental validation.
        The technique involves computational modeling approaches.
        """
        
        result = self.analyzer.analyze_content(method_text, 'method')
        
        assert isinstance(result, AnalysisResult)
        assert len(result.methodologies) > 0  # Should extract methodologies for method focus
        # Equations might be empty or minimal for method focus
    
    def test_analyze_content_research_focus(self):
        """Test analysis with research focus"""
        research_text = """
        This experimental study analyzes data from 100 participants.
        We conducted statistical analysis and found significant results.
        The empirical findings demonstrate clear patterns.
        """
        
        result = self.analyzer.analyze_content(research_text, 'research')
        
        assert isinstance(result, AnalysisResult)
        # Should focus on research-related concepts
        research_concepts = [c for c in result.key_concepts if c in ['experimental', 'data', 'statistical', 'empirical']]
        assert len(research_concepts) > 0
    
    def test_section_extraction_edge_cases(self):
        """Test section extraction with edge cases"""
        # Test with very short text
        short_text = "Short text"
        sections = self.analyzer.extract_sections(short_text)
        assert isinstance(sections, dict)
        
        # Test with text containing section keywords but not as headers
        misleading_text = """
        This paper discusses the abstract concept of introduction to methods.
        The results of this analysis show that conclusion is important.
        We review the literature on abstract thinking.
        """
        sections = self.analyzer.extract_sections(misleading_text)
        assert isinstance(sections, dict)
    
    def test_key_concepts_extraction_limits(self):
        """Test that key concept extraction respects limits"""
        # Create text with many repeated concepts
        repeated_text = " ".join(["experimental data analysis"] * 100)
        
        concepts = self.analyzer.extract_key_concepts(repeated_text, 'research')
        
        assert isinstance(concepts, list)
        assert len(concepts) <= 20  # Should respect the limit
    
    def test_equations_extraction_limits(self):
        """Test that equation extraction respects limits"""
        # Create text with many equations
        equations_text = "\n".join([f"equation_{i} = x + {i}" for i in range(20)])
        
        equations = self.analyzer._extract_equations(equations_text)
        
        assert isinstance(equations, list)
        assert len(equations) <= 10  # Should respect the limit
    
    def test_methodologies_extraction_limits(self):
        """Test that methodology extraction respects limits"""
        # Create text with many methodologies
        methods_text = "\n".join([f"We used method_{i} for analysis." for i in range(30)])
        
        methodologies = self.analyzer._extract_methodologies(methods_text)
        
        assert isinstance(methodologies, list)
        assert len(methodologies) <= 15  # Should respect the limit


if __name__ == '__main__':
    pytest.main([__file__])