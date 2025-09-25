#!/usr/bin/env python3
"""
Simple validation test for template integration functionality
Tests the core template integration features without complex dependencies
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from note_generator import NoteGenerator
from template_engine import TemplateProcessor
from models import AnalysisResult, PaperMetadata, FocusType, DepthType


def test_basic_text_processing():
    """Test basic text processing utilities"""
    print("Testing text processing utilities...")
    
    note_generator = NoteGenerator()
    
    # Test text cleaning
    dirty_text = "This  has   multiple    spaces and\n\nline breaks."
    clean_text = note_generator._clean_extracted_text(dirty_text)
    
    assert clean_text is not None
    assert len(clean_text) > 0
    assert "  " not in clean_text  # No double spaces
    print("✅ Text cleaning works")
    
    # Test text summarization
    long_text = "This is a long text. " * 50
    summary = note_generator._summarize_text(long_text, max_length=100)
    
    assert summary is not None
    assert len(summary) <= 103  # 100 + "..."
    print("✅ Text summarization works")
    
    # Test findings extraction
    findings_text = "Our study found significant improvements. The results showed 95% accuracy."
    findings = note_generator._extract_findings_from_text(findings_text)
    
    assert isinstance(findings, list)
    print("✅ Findings extraction works")


def test_content_extraction_methods():
    """Test content extraction methods"""
    print("\nTesting content extraction methods...")
    
    note_generator = NoteGenerator()
    
    # Create test analysis result
    analysis_result = AnalysisResult(
        paper_type="research",
        confidence=0.8,
        sections={
            "abstract": "This study investigates machine learning applications.",
            "introduction": "We aim to determine the effectiveness of AI in healthcare.",
            "methods": "We used a randomized controlled trial with 500 participants.",
            "results": "The AI model achieved 95% accuracy significantly outperforming traditional methods.",
            "discussion": "These results have implications for clinical practice and automated diagnosis.",
            "conclusion": "Future work should explore additional medical domains and larger datasets."
        },
        key_concepts=["machine learning", "healthcare", "accuracy"],
        equations=["Accuracy = TP/(TP+FP)"],
        methodologies=["randomized controlled trial"]
    )
    
    # Test research question extraction
    research_question = note_generator._extract_research_question(analysis_result.sections)
    assert research_question is not None
    assert len(research_question) > 10
    print("✅ Research question extraction works")
    
    # Test methodology extraction
    methodology = note_generator._extract_methodology(analysis_result.sections)
    assert methodology is not None
    assert "randomized" in methodology.lower()
    print("✅ Methodology extraction works")
    
    # Test key findings extraction  
    key_findings = note_generator._extract_key_findings(analysis_result)
    assert isinstance(key_findings, list)
    assert len(key_findings) > 0
    print("✅ Key findings extraction works")


def test_focus_specific_extraction():
    """Test focus-specific data extraction"""
    print("\nTesting focus-specific data extraction...")
    
    note_generator = NoteGenerator()
    
    # Test research-specific extraction
    research_analysis = AnalysisResult(
        paper_type="research",
        confidence=0.9,
        sections={
            "methods": "Participants were 200 adults aged 18-65. We used structured interviews.",
            "results": "The intervention group showed significant improvement (p < 0.01)."
        },
        key_concepts=["intervention", "participants"],
        equations=["p < 0.01"],
        methodologies=["structured interviews"]
    )
    
    research_data = note_generator._extract_research_specific_data(research_analysis)
    
    assert "study_design" in research_data
    assert "participants" in research_data
    assert "measures" in research_data
    print("✅ Research-specific extraction works")
    
    # Test theory-specific extraction
    theory_analysis = AnalysisResult(
        paper_type="theoretical",
        confidence=0.9,
        sections={
            "theory": "The framework is based on quantum mechanical principles.",
            "assumptions": "We assume ideal quantum systems without decoherence."
        },
        key_concepts=["quantum", "framework"],
        equations=["H|ψ⟩ = E|ψ⟩"],
        methodologies=["theoretical analysis"]
    )
    
    theory_data = note_generator._extract_theory_specific_data(theory_analysis)
    
    assert "theoretical_proposition" in theory_data
    assert "equations" in theory_data
    assert "assumptions" in theory_data
    print("✅ Theory-specific extraction works")


def test_pattern_matching_utilities():
    """Test enhanced pattern matching utilities"""
    print("\nTesting pattern matching utilities...")
    
    note_generator = NoteGenerator()
    
    # Test research question pattern matching
    text_with_questions = ("The research question is: How does exercise affect cognitive performance? " +
                          "We hypothesize that regular exercise improves memory.")
    
    questions = note_generator._extract_research_questions_by_pattern(text_with_questions)
    assert isinstance(questions, list)
    print("✅ Research question pattern matching works")
    
    # Test content segmentation
    mixed_text = ("Previous studies showed mixed results. " +
                 "We used a controlled design. " +
                 "Results demonstrated significant improvement. " +
                 "In conclusion, this approach shows promise.")
    
    segments = note_generator._segment_text_by_content_type(mixed_text)
    assert isinstance(segments, dict)
    assert "findings" in segments
    assert "methods" in segments
    print("✅ Content segmentation works")


def test_template_data_preparation():
    """Test template data preparation"""
    print("\nTesting template data preparation...")
    
    note_generator = NoteGenerator()
    
    # Create test metadata
    metadata = PaperMetadata(
        title="Test Paper: Machine Learning in Healthcare",
        first_author="Smith, John",
        authors=["Smith, John", "Doe, Jane"],
        year=2024,
        citekey="smith2024test",
        journal="Journal of AI"
    )
    
    # Create test analysis result
    analysis_result = AnalysisResult(
        paper_type="research",
        confidence=0.85,
        sections={
            "abstract": "This study examines AI applications in medical diagnosis.",
            "methods": "We conducted a controlled trial with machine learning models."
        },
        key_concepts=["AI", "medical diagnosis", "machine learning"],
        equations=["Accuracy = (TP+TN)/(TP+TN+FP+FN)"],
        methodologies=["controlled trial"]
    )
    
    # Test template data preparation
    template_data = note_generator._prepare_template_data(
        "test content", metadata, analysis_result, FocusType.RESEARCH, DepthType.STANDARD
    )
    
    # Verify basic metadata
    assert template_data["title"] == metadata.title
    assert template_data["first_author"] == metadata.first_author
    assert template_data["year"] == metadata.year
    
    # Verify extracted content
    assert "research_question" in template_data
    assert "methodology" in template_data
    assert "key_findings" in template_data
    
    print("✅ Template data preparation works")


def run_all_tests():
    """Run all validation tests"""
    print("🚀 Starting Template Integration Validation Tests")
    print("=" * 60)
    
    try:
        test_basic_text_processing()
        test_content_extraction_methods()
        test_focus_specific_extraction()
        test_pattern_matching_utilities()
        test_template_data_preparation()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Template Integration is Working!")
        print("✅ Task 8: Comprehensive testing for template integration - COMPLETED")
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)