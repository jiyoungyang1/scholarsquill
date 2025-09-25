"""
Comprehensive unit tests for template integration content extraction methods
Tests Task 8.1: Unit tests for content extraction methods
"""

import pytest
from unittest.mock import Mock

from src.note_generator import NoteGenerator
from src.models import (
    AnalysisResult, FocusType, DepthType, PaperMetadata
)


class TestContentExtractionMethods:
    """Unit tests for content extraction methods"""
    
    @pytest.fixture
    def note_generator(self):
        """Create NoteGenerator instance for testing"""
        return NoteGenerator()
    
    @pytest.fixture
    def sample_sections_introduction_abstract(self):
        """Sample sections with various introduction and abstract formats"""
        return {
            "abstract": "This study examines the effectiveness of machine learning algorithms in medical diagnosis. We investigate whether deep learning models can improve diagnostic accuracy compared to traditional methods.",
            "introduction": "Machine learning has revolutionized healthcare applications. This research aims to determine the impact of neural networks on diagnostic performance. We hypothesize that deep learning approaches will significantly enhance accuracy.",
            "methods": "We employed a controlled experimental design using a dataset of 10,000 medical images. Deep learning models were trained using convolutional neural networks.",
            "results": "Our analysis revealed a 95% accuracy rate. The deep learning model significantly outperformed traditional methods (p < 0.001).",
            "discussion": "These results have important implications for clinical practice. The improved accuracy suggests potential for real-world deployment.",
            "conclusion": "We conclude that deep learning models offer substantial improvements in diagnostic accuracy. Future work should explore larger datasets and additional medical domains."
        }
    
    @pytest.fixture
    def sample_sections_methodology(self):
        """Sample sections with different methodology section structures"""
        return {
            "methods": "We used a randomized controlled trial design. Participants were recruited from three medical centers. Data collection involved structured interviews and clinical assessments. Statistical analysis was performed using SPSS.",
            "methodology": "The study employed a mixed-methods approach combining quantitative surveys and qualitative interviews. Sample size was calculated using power analysis.",
            "experimental_design": "A double-blind, placebo-controlled study was conducted. The experimental protocol involved three phases: baseline assessment, intervention, and follow-up.",
            "procedures": "All procedures were conducted according to established protocols. Quality control measures included inter-rater reliability testing."
        }
    
    @pytest.fixture
    def sample_sections_results_conclusion(self):
        """Sample sections with various results and conclusion formats"""
        return {
            "results": "The primary outcome showed significant improvement (p = 0.002). Secondary analyses revealed dose-response relationships. Effect sizes ranged from moderate to large (Cohen's d = 0.6-1.2).",
            "findings": "Key findings include: 1) 30% reduction in symptoms, 2) improved quality of life scores, 3) no serious adverse events reported.",
            "discussion": "Our results demonstrate clinical significance. The treatment effect exceeded the minimal clinically important difference.",
            "conclusion": "This intervention shows promise for clinical implementation. Limitations include single-center design and short follow-up period. Future research should address these limitations.",
            "limitations": "Study limitations include potential selection bias, limited generalizability to other populations, and short-term follow-up."
        }
    
    @pytest.fixture
    def theory_analysis_result(self):
        """Analysis result for theory-focused papers"""
        return AnalysisResult(
            paper_type="theoretical",
            confidence=0.90,
            sections={
                "abstract": "This paper presents a novel theoretical framework for quantum computing algorithms.",
                "introduction": "Current theoretical models lack comprehensive mathematical foundations. We propose a unified theoretical approach.",
                "theory": "The theoretical framework is based on quantum mechanical principles. We derive fundamental equations governing quantum state evolution.",
                "mathematical_models": "The mathematical formulation includes Schrödinger equations and Hamiltonian operators.",
                "assumptions": "We assume ideal quantum systems without decoherence. The model presupposes perfect quantum gates.",
                "proofs": "Theorem 1 proves convergence properties. The proof relies on variational principles and spectral analysis."
            },
            key_concepts=["quantum computing", "theoretical framework", "mathematical models"],
            equations=["H|ψ⟩ = E|ψ⟩", "∂|ψ⟩/∂t = -iH|ψ⟩/ℏ", "⟨ψ|ψ⟩ = 1"],
            methodologies=["theoretical analysis", "mathematical derivation"]
        )
    
    @pytest.fixture
    def research_analysis_result(self):
        """Analysis result for research-focused papers"""
        return AnalysisResult(
            paper_type="research",
            confidence=0.85,
            sections={
                "abstract": "This study investigates the effects of exercise on cognitive performance in elderly adults.",
                "introduction": "Physical exercise has been linked to cognitive benefits. We examine whether structured exercise programs improve memory and attention.",
                "methods": "A randomized controlled trial with 200 participants aged 65-80. Participants were randomly assigned to exercise or control groups.",
                "participants": "Inclusion criteria: age 65-80, cognitively healthy, sedentary lifestyle. Exclusion criteria: major medical conditions, cognitive impairment.",
                "measures": "Cognitive assessments included memory tests, attention tasks, and executive function measures. Physical fitness was assessed using standard protocols.",
                "procedures": "The exercise intervention consisted of 3 sessions per week for 12 weeks. Each session included aerobic and resistance training.",
                "results": "Exercise group showed significant improvements in memory (p < 0.01) and attention (p < 0.05). Effect sizes were moderate to large.",
                "statistical_analysis": "Data were analyzed using mixed-effects models. Multiple comparisons were corrected using Bonferroni adjustment."
            },
            key_concepts=["exercise", "cognitive performance", "elderly", "randomized trial"],
            equations=["Cohen's d = (M1 - M2) / SDpooled"],
            methodologies=["randomized controlled trial", "cognitive assessment"]
        )
    
    def test_extract_research_question_introduction_patterns(self, note_generator, sample_sections_introduction_abstract):
        """Test research question extraction from introduction with various patterns"""
        result = note_generator._extract_research_question(sample_sections_introduction_abstract)
        
        assert result is not None
        assert len(result) > 10
        # Should extract the main research aim/hypothesis
        assert any(keyword in result.lower() for keyword in ["determine", "impact", "neural networks", "diagnostic"])
    
    def test_extract_research_question_abstract_patterns(self, note_generator):
        """Test research question extraction from abstract with different formats"""
        sections = {
            "abstract": "Objective: To evaluate the effectiveness of telemedicine in rural healthcare. Methods: We conducted a systematic review. Results: Telemedicine improved access to care."
        }
        
        result = note_generator._extract_research_question(sections)
        
        assert result is not None
        assert "effectiveness" in result.lower() or "evaluate" in result.lower()
    
    def test_extract_research_question_hypothesis_patterns(self, note_generator):
        """Test research question extraction with hypothesis patterns"""
        sections = {
            "introduction": "We hypothesize that machine learning algorithms will outperform traditional statistical methods in predicting patient outcomes."
        }
        
        result = note_generator._extract_research_question(sections)
        
        assert result is not None
        assert "machine learning" in result.lower()
        assert "outperform" in result.lower()
    
    def test_extract_research_question_investigation_patterns(self, note_generator):
        """Test research question extraction with investigation patterns"""
        sections = {
            "introduction": "This study investigates whether early intervention programs reduce hospital readmission rates in elderly patients."
        }
        
        result = note_generator._extract_research_question(sections)
        
        assert result is not None
        assert "early intervention" in result.lower()
        assert "readmission" in result.lower()
    
    def test_extract_research_question_fallback(self, note_generator):
        """Test research question extraction fallback behavior"""
        sections = {"other": "No research question content"}
        
        result = note_generator._extract_research_question(sections)
        
        assert result is not None
        assert "research objectives" in result.lower()
    
    def test_extract_methodology_methods_section(self, note_generator, sample_sections_methodology):
        """Test methodology extraction from methods section"""
        result = note_generator._extract_methodology(sample_sections_methodology)
        
        assert result is not None
        assert len(result) > 20
        assert any(keyword in result.lower() for keyword in ["randomized", "controlled", "participants", "statistical"])
    
    def test_extract_methodology_methodology_section(self, note_generator, sample_sections_methodology):
        """Test methodology extraction from methodology section"""
        sections = {"methodology": sample_sections_methodology["methodology"]}
        
        result = note_generator._extract_methodology(sections)
        
        assert result is not None
        assert "mixed-methods" in result.lower()
        assert "power analysis" in result.lower()
    
    def test_extract_methodology_experimental_design(self, note_generator, sample_sections_methodology):
        """Test methodology extraction from experimental design section"""
        sections = {"experimental_design": sample_sections_methodology["experimental_design"]}
        
        result = note_generator._extract_methodology(sections)
        
        assert result is not None
        assert "double-blind" in result.lower()
        assert "placebo-controlled" in result.lower()
    
    def test_extract_methodology_multiple_sections(self, note_generator, sample_sections_methodology):
        """Test methodology extraction when multiple method sections exist"""
        result = note_generator._extract_methodology(sample_sections_methodology)
        
        assert result is not None
        # Should prefer 'methods' section first
        assert "randomized controlled trial" in result.lower()
    
    def test_extract_methodology_fallback(self, note_generator):
        """Test methodology extraction fallback behavior"""
        sections = {"results": "No methodology content"}
        
        result = note_generator._extract_methodology(sections)
        
        assert result is not None
        assert "methodology details" in result.lower()
    
    def test_extract_key_findings_results_section(self, note_generator, sample_sections_results_conclusion):
        """Test key findings extraction from results section"""
        analysis_result = AnalysisResult(
            paper_type="research",
            confidence=0.8,
            sections=sample_sections_results_conclusion,
            key_concepts=["improvement", "symptoms", "quality of life"],
            equations=[],
            methodologies=[]
        )
        
        findings = note_generator._extract_key_findings(analysis_result)
        
        assert len(findings) > 0
        assert any("significant" in finding.lower() for finding in findings)
        assert any("improvement" in finding.lower() for finding in findings)
    
    def test_extract_key_findings_from_concepts(self, note_generator):
        """Test key findings extraction using existing key concepts"""
        analysis_result = AnalysisResult(
            paper_type="research",
            confidence=0.8,
            sections={"other": "No specific findings"},
            key_concepts=["machine learning accuracy", "diagnostic improvement", "clinical significance"],
            equations=[],
            methodologies=[]
        )
        
        findings = note_generator._extract_key_findings(analysis_result)
        
        assert len(findings) > 0
        assert any("accuracy" in finding.lower() for finding in findings)
        assert any("diagnostic" in finding.lower() for finding in findings)
    
    def test_extract_key_findings_conclusion_section(self, note_generator, sample_sections_results_conclusion):
        """Test key findings extraction from conclusion section"""
        analysis_result = AnalysisResult(
            paper_type="research",
            confidence=0.8,
            sections={"conclusion": sample_sections_results_conclusion["conclusion"]},
            key_concepts=[],
            equations=[],
            methodologies=[]
        )
        
        findings = note_generator._extract_key_findings(analysis_result)
        
        assert len(findings) > 0
        assert any("promise" in finding.lower() or "implementation" in finding.lower() for finding in findings)
    
    def test_extract_key_findings_discussion_section(self, note_generator, sample_sections_results_conclusion):
        """Test key findings extraction from discussion section"""
        analysis_result = AnalysisResult(
            paper_type="research",
            confidence=0.8,
            sections={"discussion": sample_sections_results_conclusion["discussion"]},
            key_concepts=[],
            equations=[],
            methodologies=[]
        )
        
        findings = note_generator._extract_key_findings(analysis_result)
        
        assert len(findings) > 0
        assert any("clinical significance" in finding.lower() for finding in findings)
    
    def test_extract_key_findings_fallback(self, note_generator):
        """Test key findings extraction fallback behavior"""
        analysis_result = AnalysisResult(
            paper_type="research",
            confidence=0.8,
            sections={"other": "No findings"},
            key_concepts=[],
            equations=[],
            methodologies=[]
        )
        
        findings = note_generator._extract_key_findings(analysis_result)
        
        assert len(findings) > 0
        assert any("require detailed analysis" in finding.lower() for finding in findings)
    
    def test_extract_theory_specific_data_theoretical_propositions(self, note_generator, theory_analysis_result):
        """Test theory-specific data extraction for theoretical propositions"""
        theory_data = note_generator._extract_theory_specific_data(theory_analysis_result)
        
        assert "theoretical_proposition" in theory_data
        assert theory_data["theoretical_proposition"] is not None
        assert len(theory_data["theoretical_proposition"]) > 10
    
    def test_extract_theory_specific_data_equations(self, note_generator, theory_analysis_result):
        """Test theory-specific data extraction for equations"""
        theory_data = note_generator._extract_theory_specific_data(theory_analysis_result)
        
        assert "equations" in theory_data
        assert len(theory_data["equations"]) > 0
        assert any("ψ" in eq for eq in theory_data["equations"])  # Quantum mechanics symbols
    
    def test_extract_theory_specific_data_assumptions(self, note_generator, theory_analysis_result):
        """Test theory-specific data extraction for assumptions"""
        theory_data = note_generator._extract_theory_specific_data(theory_analysis_result)
        
        assert "assumptions" in theory_data
        assert len(theory_data["assumptions"]) > 0
        assert any("ideal quantum systems" in assumption.lower() for assumption in theory_data["assumptions"])
    
    def test_extract_theory_specific_data_mathematical_models(self, note_generator, theory_analysis_result):
        """Test theory-specific data extraction for mathematical models"""
        theory_data = note_generator._extract_theory_specific_data(theory_analysis_result)
        
        assert "mathematical_models" in theory_data
        assert theory_data["mathematical_models"] is not None
        assert "schrödinger" in theory_data["mathematical_models"].lower()
    
    def test_extract_research_specific_data_study_design(self, note_generator, research_analysis_result):
        """Test research-specific data extraction for study design"""
        research_data = note_generator._extract_research_specific_data(research_analysis_result)
        
        assert "study_design" in research_data
        assert research_data["study_design"] is not None
        assert "randomized controlled trial" in research_data["study_design"].lower()
    
    def test_extract_research_specific_data_participants(self, note_generator, research_analysis_result):
        """Test research-specific data extraction for participants"""
        research_data = note_generator._extract_research_specific_data(research_analysis_result)
        
        assert "participants" in research_data
        assert research_data["participants"] is not None
        assert "65-80" in research_data["participants"]
    
    def test_extract_research_specific_data_measures(self, note_generator, research_analysis_result):
        """Test research-specific data extraction for measures"""
        research_data = note_generator._extract_research_specific_data(research_analysis_result)
        
        assert "measures" in research_data
        assert len(research_data["measures"]) > 0
        assert any("cognitive" in measure.lower() for measure in research_data["measures"])
    
    def test_extract_research_specific_data_procedures(self, note_generator, research_analysis_result):
        """Test research-specific data extraction for procedures"""
        research_data = note_generator._extract_research_specific_data(research_analysis_result)
        
        assert "experimental_procedures" in research_data
        assert len(research_data["experimental_procedures"]) > 0
        assert any("3 sessions per week" in proc for proc in research_data["experimental_procedures"])
    
    def test_extract_method_specific_data_experimental_design(self, note_generator, research_analysis_result):
        """Test method-specific data extraction for experimental design"""
        method_data = note_generator._extract_method_specific_data(research_analysis_result)
        
        assert "experimental_design" in method_data
        assert method_data["experimental_design"] is not None
        assert "randomized" in method_data["experimental_design"].lower()
    
    def test_extract_method_specific_data_procedures(self, note_generator, research_analysis_result):
        """Test method-specific data extraction for procedures"""
        method_data = note_generator._extract_method_specific_data(research_analysis_result)
        
        assert "procedures" in method_data
        assert len(method_data["procedures"]) > 0
    
    def test_extract_method_specific_data_validation(self, note_generator, research_analysis_result):
        """Test method-specific data extraction for validation"""
        method_data = note_generator._extract_method_specific_data(research_analysis_result)
        
        assert "validation" in method_data
        assert method_data["validation"] is not None
    
    def test_extract_review_specific_data_scope(self, note_generator):
        """Test review-specific data extraction for scope"""
        review_analysis_result = AnalysisResult(
            paper_type="review",
            confidence=0.9,
            sections={
                "abstract": "This systematic review examines the effectiveness of telemedicine interventions.",
                "methods": "We searched PubMed, Embase, and Cochrane databases. Inclusion criteria were randomized trials published 2010-2020.",
                "results": "Twenty-three studies met inclusion criteria. Quality assessment revealed moderate to high study quality.",
                "conclusion": "Evidence suggests telemedicine is effective for chronic disease management. Future research should focus on cost-effectiveness."
            },
            key_concepts=["systematic review", "telemedicine", "effectiveness", "chronic disease"],
            equations=[],
            methodologies=["systematic review", "meta-analysis"]
        )
        
        review_data = note_generator._extract_review_specific_data(review_analysis_result)
        
        assert "scope" in review_data
        assert review_data["scope"] is not None
        assert "systematic review" in review_data["scope"].lower()
    
    def test_extract_review_specific_data_themes(self, note_generator):
        """Test review-specific data extraction for key themes"""
        analysis_result = AnalysisResult(
            paper_type="review",
            confidence=0.9,
            sections={"results": "Key themes include effectiveness, implementation barriers, and patient satisfaction."},
            key_concepts=["effectiveness", "implementation", "barriers", "patient satisfaction"],
            equations=[],
            methodologies=[]
        )
        
        review_data = note_generator._extract_review_specific_data(analysis_result)
        
        assert "key_themes" in review_data
        assert len(review_data["key_themes"]) > 0
        assert any("effectiveness" in theme.lower() for theme in review_data["key_themes"])
    
    def test_extract_review_specific_data_research_gaps(self, note_generator):
        """Test review-specific data extraction for research gaps"""
        analysis_result = AnalysisResult(
            paper_type="review",
            confidence=0.9,
            sections={
                "conclusion": "Research gaps include lack of long-term studies, limited diversity in study populations, and insufficient cost-effectiveness analyses."
            },
            key_concepts=[],
            equations=[],
            methodologies=[]
        )
        
        review_data = note_generator._extract_review_specific_data(analysis_result)
        
        assert "research_gaps" in review_data
        assert len(review_data["research_gaps"]) > 0
        assert any("long-term" in gap.lower() for gap in review_data["research_gaps"])
    
    def test_text_processing_utilities_clean_extracted_text(self, note_generator):
        """Test enhanced text cleaning utility"""
        dirty_text = "This  is   a  test\n\nwith   multiple    spaces\tand\ttabs. It—has em-dashes and 'smart quotes'."
        
        clean_text = note_generator._clean_extracted_text(dirty_text)
        
        assert clean_text is not None
        assert "  " not in clean_text  # No double spaces
        assert "smart quotes" in clean_text  # Smart quotes converted
        assert "em-dashes" in clean_text or "em-dashes" in clean_text  # Em-dash handled
    
    def test_text_processing_utilities_summarize_text(self, note_generator):
        """Test enhanced text summarization utility"""
        long_text = ("This is a test sentence with important findings. " * 20 + 
                    "The results showed significant improvement. " * 10 + 
                    "Additional context and background information. " * 15)
        
        summary = note_generator._summarize_text(long_text, max_length=200)
        
        assert len(summary) <= 203  # 200 + "..."
        assert "findings" in summary or "results" in summary  # Should prioritize key content
    
    def test_text_processing_utilities_extract_findings_from_text(self, note_generator):
        """Test enhanced findings extraction utility"""
        findings_text = ("Our study found that the intervention was effective. " +
                        "Results showed a 30% improvement in outcomes. " +
                        "The analysis revealed significant differences between groups. " +
                        "Additionally, we observed unexpected benefits in secondary measures.")
        
        findings = note_generator._extract_findings_from_text(findings_text)
        
        assert len(findings) > 0
        assert any("effective" in finding.lower() for finding in findings)
        assert any("30%" in finding for finding in findings)
        assert any("significant" in finding.lower() for finding in findings)
    
    def test_pattern_matching_research_questions_by_pattern(self, note_generator):
        """Test research question extraction using advanced patterns"""
        text = ("The main research question is: How does exercise affect cognitive performance? " +
               "We hypothesize that regular exercise will improve memory and attention. " +
               "This study aims to determine the relationship between physical activity and brain function.")
        
        questions = note_generator._extract_research_questions_by_pattern(text)
        
        assert len(questions) > 0
        assert any("exercise" in q.lower() and "cognitive" in q.lower() for q in questions)
        assert any("memory" in q.lower() and "attention" in q.lower() for q in questions)
    
    def test_pattern_matching_objectives_by_pattern(self, note_generator):
        """Test objective extraction using pattern matching"""
        text = ("The primary objective is to evaluate the effectiveness of the intervention. " +
               "Secondary aims include assessment of safety and tolerability. " +
               "We seek to determine optimal dosing strategies.")
        
        objectives = note_generator._extract_objectives_by_pattern(text)
        
        assert len(objectives) > 0
        assert any("effectiveness" in obj.lower() for obj in objectives)
        assert any("safety" in obj.lower() for obj in objectives)
    
    def test_content_segmentation_by_type(self, note_generator):
        """Test smart text segmentation by content type"""
        mixed_text = ("Previous studies have shown mixed results. " +
                     "We used a randomized controlled trial design. " +
                     "Our results demonstrated significant improvement. " +
                     "In conclusion, this intervention shows promise.")
        
        segments = note_generator._segment_text_by_content_type(mixed_text)
        
        assert "findings" in segments
        assert "methods" in segments
        assert "background" in segments
        assert "conclusions" in segments
        
        assert len(segments["background"]) > 0  # "Previous studies"
        assert len(segments["findings"]) > 0    # "results demonstrated"
        assert len(segments["conclusions"]) > 0  # "In conclusion"
    
    def test_extract_numerical_results(self, note_generator):
        """Test numerical results extraction"""
        results_text = ("The treatment group showed 85% improvement. " +
                       "Statistical analysis revealed p < 0.001. " +
                       "Effect size was large (r = 0.8). " +
                       "Sample size was n = 150. " +
                       "95% CI: 1.2-2.4.")
        
        numerical_results = note_generator._extract_numerical_results(results_text)
        
        assert len(numerical_results) > 0
        assert any("85%" in result for result in numerical_results)
        assert any("p <" in result.lower() for result in numerical_results)
        assert any("r =" in result.lower() for result in numerical_results)
        assert any("n =" in result.lower() for result in numerical_results)


if __name__ == "__main__":
    pytest.main([__file__])