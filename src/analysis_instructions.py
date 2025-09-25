"""
Analysis instructions generator for Claude AI integration
"""

from typing import Dict, List, Any
import logging


class AnalysisInstructionsGenerator:
    """Generate comprehensive analysis instructions for Claude AI"""
    
    def __init__(self):
        """Initialize analysis instructions generator"""
        self.logger = logging.getLogger(__name__)
        
        # Enhanced focus-specific instructions with detailed guidance and examples
        self.focus_instructions = {
            "research": {
                "primary_focus": "Research methodology, experimental design, and empirical findings",
                "description": "Empirical research papers with data collection, analysis, and statistical findings",
                "key_sections": ["methodology", "results", "discussion", "limitations"],
                "extract": [
                    "Research questions and hypotheses",
                    "Study design and methodology",
                    "Sample characteristics and data collection methods",
                    "Statistical analysis methods and tools used",
                    "Key findings and quantitative results",
                    "Effect sizes and statistical significance",
                    "Practical implications and applications",
                    "Study limitations and potential biases"
                ],
                "analysis_approach": "Focus on the empirical aspects, data quality, methodology rigor, and the validity of conclusions drawn from the results.",
                "specific_targets": {
                    "methodology": {
                        "what_to_look_for": [
                            "Experimental vs. observational design",
                            "Randomization and control procedures",
                            "Sample size calculations and power analysis",
                            "Data collection instruments and validation",
                            "Inclusion/exclusion criteria",
                            "Ethical considerations and approvals"
                        ],
                        "extraction_examples": [
                            "\"This randomized controlled trial recruited 245 participants from 3 hospitals\"",
                            "\"Data was collected using the validated XYZ scale (Cronbach's α = 0.89)\"",
                            "\"Sample size was calculated to detect a medium effect size (d = 0.5) with 80% power\""
                        ]
                    },
                    "results": {
                        "what_to_look_for": [
                            "Primary and secondary outcome measures",
                            "Statistical significance levels and p-values",
                            "Effect sizes and confidence intervals",
                            "Descriptive statistics and demographics",
                            "Subgroup analyses and post-hoc tests",
                            "Missing data handling and sensitivity analyses"
                        ],
                        "extraction_examples": [
                            "\"Intervention group showed significantly higher scores (M = 85.4, SD = 12.3) vs control (M = 76.2, SD = 14.1), t(243) = 4.32, p < .001, Cohen's d = 0.68\"",
                            "\"Response rate was 87% with no significant differences between dropouts and completers\"",
                            "\"Sensitivity analysis excluding outliers confirmed the main findings\""
                        ]
                    },
                    "discussion": {
                        "what_to_look_for": [
                            "Interpretation of findings in context",
                            "Comparison with previous research",
                            "Clinical or practical significance",
                            "Mechanisms underlying observed effects",
                            "Generalizability considerations",
                            "Implications for practice and policy"
                        ],
                        "extraction_examples": [
                            "\"These findings support previous work by Smith et al. (2020) while extending to a clinical population\"",
                            "\"The large effect size suggests clinical significance beyond statistical significance\"",
                            "\"Results may not generalize to populations outside the 18-65 age range\""
                        ]
                    }
                },
                "critical_evaluation_areas": [
                    "Internal validity (controls, randomization, blinding)",
                    "External validity (generalizability, sample representativeness)", 
                    "Statistical validity (appropriate tests, assumptions met)",
                    "Construct validity (measures appropriate for constructs)",
                    "Reporting quality (CONSORT, STROBE compliance)"
                ],
                "red_flags_to_note": [
                    "Very small sample sizes without justification",
                    "Multiple comparisons without correction",
                    "Missing information about randomization or blinding",
                    "Selective reporting of results",
                    "Conflicts of interest not disclosed"
                ]
            },
            "theory": {
                "primary_focus": "Theoretical frameworks, mathematical models, and conceptual contributions",
                "description": "Theoretical papers that develop or extend conceptual frameworks, mathematical models, or abstract principles",
                "key_sections": ["theoretical framework", "model development", "equations", "proofs"],
                "extract": [
                    "Theoretical propositions and core assumptions",
                    "Mathematical equations and derivations",
                    "Conceptual relationships and frameworks",
                    "Model validation and theoretical applications",
                    "Theoretical implications and extensions",
                    "Connections to existing theoretical work",
                    "Novel theoretical contributions",
                    "Logical consistency and theoretical rigor"
                ],
                "analysis_approach": "Emphasize the theoretical contributions, mathematical rigor, and how the work advances conceptual understanding in the field.",
                "specific_targets": {
                    "theoretical_framework": {
                        "what_to_look_for": [
                            "Core theoretical propositions and axioms",
                            "Underlying assumptions and their justification",
                            "Conceptual definitions and operationalizations",
                            "Relationships between theoretical constructs",
                            "Boundary conditions and scope of theory",
                            "Integration with existing theoretical work"
                        ],
                        "extraction_examples": [
                            "\"We propose three fundamental axioms: (1) agents are rational, (2) information is costly, (3) markets clear\"",
                            "\"This framework extends Social Cognitive Theory by incorporating digital mediation effects\"",
                            "\"The model assumes perfect competition and symmetric information\""
                        ]
                    },
                    "mathematical_formulations": {
                        "what_to_look_for": [
                            "Mathematical equations and their derivations",
                            "Model parameters and their interpretations",
                            "Proofs and formal demonstrations",
                            "Optimization problems and solutions",
                            "Stability and equilibrium conditions",
                            "Numerical examples and simulations"
                        ],
                        "extraction_examples": [
                            "\"The utility function is defined as U(x,y) = αx^β + γy^δ where α,β,γ,δ > 0\"",
                            "\"Theorem 1: Under conditions A and B, the equilibrium is unique and stable (proof in Appendix)\"",
                            "\"Monte Carlo simulations (n=10,000) confirm the theoretical predictions\""
                        ]
                    },
                    "theoretical_implications": {
                        "what_to_look_for": [
                            "Novel insights generated by the theory",
                            "Predictions that can be empirically tested",
                            "Reconciliation of conflicting findings",
                            "Extension to new domains or contexts",
                            "Practical applications of theoretical insights",
                            "Future theoretical developments suggested"
                        ],
                        "extraction_examples": [
                            "\"The theory predicts that intervention effects should be strongest for medium-complexity tasks\"",
                            "\"This framework explains the seemingly contradictory findings in the literature\"",
                            "\"The model suggests three testable hypotheses for future empirical work\""
                        ]
                    }
                },
                "critical_evaluation_areas": [
                    "Logical consistency and internal coherence",
                    "Clarity and precision of theoretical constructs",
                    "Parsimony vs. explanatory power trade-offs",
                    "Falsifiability and empirical testability",
                    "Scope and generalizability of the theory",
                    "Novelty and theoretical contribution"
                ],
                "red_flags_to_note": [
                    "Circular reasoning or tautological statements",
                    "Undefined or poorly defined theoretical terms",
                    "Mathematical errors or unsupported derivations",
                    "Unrealistic assumptions without justification",
                    "Lack of connection to empirical reality",
                    "Overly complex models without added explanatory value"
                ]
            },
            "method": {
                "primary_focus": "Experimental methods, procedures, and technical approaches",
                "description": "Papers introducing new methods, techniques, protocols, or significant improvements to existing approaches",
                "key_sections": ["methods", "experimental setup", "validation", "performance"],
                "extract": [
                    "Experimental design and detailed procedures",
                    "Technical implementation and setup details",
                    "Validation approaches and evaluation metrics",
                    "Performance evaluation and benchmarking results",
                    "Method advantages and unique features",
                    "Limitations and potential improvements",
                    "Reproducibility considerations",
                    "Comparison with existing methods"
                ],
                "analysis_approach": "Focus on the technical details, methodological innovations, and the practical applicability of the proposed methods.",
                "specific_targets": {
                    "technical_details": {
                        "what_to_look_for": [
                            "Step-by-step procedural descriptions",
                            "Equipment specifications and requirements",
                            "Software tools and computational resources",
                            "Parameter settings and optimization",
                            "Quality control and calibration procedures",
                            "Troubleshooting and common pitfalls"
                        ],
                        "extraction_examples": [
                            "\"Samples were processed using a Zeiss LSM 880 confocal microscope with 63x oil immersion objective\"",
                            "\"The algorithm was implemented in Python 3.8 using NumPy 1.19.2 and SciPy 1.5.4\"",
                            "\"Optimal performance required batch size=32, learning rate=0.001, and dropout=0.2\""
                        ]
                    },
                    "validation_approach": {
                        "what_to_look_for": [
                            "Validation datasets and benchmarks used",
                            "Performance metrics and evaluation criteria",
                            "Cross-validation and robustness testing",
                            "Comparison with gold standard methods",
                            "Statistical tests for method comparison",
                            "Sensitivity analysis and parameter testing"
                        ],
                        "extraction_examples": [
                            "\"Method was validated on 3 independent datasets (n=150, 200, 175)\"",
                            "\"Performance was measured using accuracy, precision, recall, and F1-score\"",
                            "\"Our method achieved 95.2% accuracy vs. 87.1% for the previous best approach (p<0.001)\""
                        ]
                    },
                    "practical_considerations": {
                        "what_to_look_for": [
                            "Time and computational complexity",
                            "Resource requirements and costs",
                            "Scalability and throughput considerations",
                            "User expertise and training needed",
                            "Integration with existing workflows",
                            "Limitations and contraindications"
                        ],
                        "extraction_examples": [
                            "\"Processing time scales linearly with sample size (O(n))\"",
                            "\"Method requires 16GB RAM and CUDA-compatible GPU for real-time processing\"",
                            "\"Protocol can be completed by trained technicians in 2-3 hours\""
                        ]
                    }
                },
                "critical_evaluation_areas": [
                    "Methodological rigor and validity",
                    "Reproducibility and replicability",
                    "Comparison fairness and completeness",
                    "Practical feasibility and adoption barriers",
                    "Novelty vs. incremental improvement",
                    "Generalizability across contexts"
                ],
                "red_flags_to_note": [
                    "Insufficient methodological details for reproduction",
                    "Biased comparisons or cherry-picked baselines",
                    "Overfitting to specific datasets or conditions",
                    "Unrealistic assumptions about practical implementation",
                    "Missing negative results or failure cases",
                    "Inadequate validation or testing procedures"
                ]
            },
            "review": {
                "primary_focus": "Literature synthesis, research gaps, and comprehensive overview",
                "description": "Systematic reviews, meta-analyses, scoping reviews, and comprehensive literature surveys",
                "key_sections": ["literature review", "synthesis", "gaps", "future directions"],
                "extract": [
                    "Literature scope and systematic search strategy",
                    "Thematic analysis and knowledge synthesis",
                    "Identified research gaps and limitations",
                    "Future research directions and opportunities",
                    "Field advancement and emerging trends",
                    "Methodological considerations across studies",
                    "Consensus and disagreements in the literature",
                    "Practical implications for the field"
                ],
                "analysis_approach": "Emphasize the comprehensiveness of the review, quality of synthesis, and identification of research gaps and future directions.",
                "specific_targets": {
                    "search_strategy": {
                        "what_to_look_for": [
                            "Databases searched and search terms used",
                            "Inclusion and exclusion criteria",
                            "Time period and language restrictions",
                            "Study selection process and reviewers",
                            "Quality assessment criteria and tools",
                            "Data extraction procedures"
                        ],
                        "extraction_examples": [
                            "\"Searched PubMed, PsycINFO, and Web of Science from 2010-2023\"",
                            "\"Included RCTs with n≥50 published in English\"",
                            "\"Two independent reviewers screened 2,847 abstracts with 96% agreement (κ=0.92)\""
                        ]
                    },
                    "synthesis_quality": {
                        "what_to_look_for": [
                            "Narrative vs. quantitative synthesis approach",
                            "Meta-analysis procedures and statistics",
                            "Heterogeneity assessment and handling",
                            "Subgroup analyses and sensitivity tests",
                            "Risk of bias evaluation",
                            "Strength of evidence assessment"
                        ],
                        "extraction_examples": [
                            "\"Random effects meta-analysis revealed pooled effect size d=0.45 (95% CI: 0.32-0.58)\"",
                            "\"Substantial heterogeneity observed (I²=74%) due to methodological differences\"",
                            "\"GRADE assessment indicated moderate quality evidence\""
                        ]
                    },
                    "knowledge_gaps": {
                        "what_to_look_for": [
                            "Areas with insufficient evidence",
                            "Methodological limitations across studies",
                            "Inconsistent findings requiring resolution",
                            "Underrepresented populations or contexts",
                            "Emerging issues not yet well-studied",
                            "Translation gaps between research and practice"
                        ],
                        "extraction_examples": [
                            "\"Only 3 studies included participants over age 65, limiting generalizability\"",
                            "\"Long-term follow-up data (>1 year) was available for only 15% of studies\"",
                            "\"Conflicting results may be due to varying outcome measures across studies\""
                        ]
                    }
                },
                "critical_evaluation_areas": [
                    "Comprehensiveness of literature search",
                    "Appropriateness of inclusion/exclusion criteria",
                    "Quality of study selection and data extraction",
                    "Rigor of synthesis methods used",
                    "Transparency and reproducibility",
                    "Clinical or practical relevance of findings"
                ],
                "red_flags_to_note": [
                    "Narrow or biased search strategy",
                    "Lack of quality assessment for included studies",
                    "Inappropriate pooling of heterogeneous studies",
                    "Cherry-picking results to support conclusions",
                    "Outdated literature base or search cutoff",
                    "Conflicts of interest affecting review scope"
                ]
            },
            "balanced": {
                "primary_focus": "Comprehensive analysis covering all aspects of the paper",
                "description": "All-purpose analysis suitable for any paper type, providing balanced coverage of all major aspects",
                "key_sections": ["all sections"],
                "extract": [
                    "Research overview and main objectives",
                    "Methodology and analytical approach",
                    "Key findings and significant results",
                    "Theoretical contributions and frameworks",
                    "Practical applications and implications",
                    "Study limitations and methodological considerations",
                    "Future research directions",
                    "Overall contribution to the field"
                ],
                "analysis_approach": "Provide a well-rounded analysis that covers theoretical, methodological, and practical aspects equally.",
                "specific_targets": {
                    "comprehensive_overview": {
                        "what_to_look_for": [
                            "Main research purpose and significance",
                            "Key methodological approach used",
                            "Primary findings and conclusions",
                            "Theoretical framework or perspective",
                            "Practical implications and applications",
                            "Study limitations and constraints"
                        ],
                        "extraction_examples": [
                            "\"This mixed-methods study investigates the effectiveness of X intervention using RCT design (n=200) plus interviews\"",
                            "\"Results show significant improvement in primary outcome (p<0.001) with practical effect size (d=0.7)\"",
                            "\"Findings contribute to Y theory and have implications for Z practice\""
                        ]
                    },
                    "quality_assessment": {
                        "what_to_look_for": [
                            "Rigor of research design and methods",
                            "Strength of evidence provided",
                            "Clarity of presentation and writing",
                            "Appropriateness of conclusions",
                            "Ethical considerations addressed",
                            "Transparency and reproducibility"
                        ],
                        "extraction_examples": [
                            "\"Well-designed RCT with appropriate randomization and blinding procedures\"",
                            "\"Statistical analysis appropriate with effect sizes and confidence intervals reported\"",
                            "\"Conclusions well-supported by data with limitations appropriately acknowledged\""
                        ]
                    },
                    "broader_significance": {
                        "what_to_look_for": [
                            "Novelty and originality of contribution",
                            "Relevance to current knowledge and practice",
                            "Potential impact on field advancement",
                            "Connections to other research areas",
                            "Implications for policy or practice",
                            "Future research opportunities created"
                        ],
                        "extraction_examples": [
                            "\"First study to demonstrate X relationship in Y population\"",
                            "\"Findings challenge existing assumptions about Z and suggest need for revised guidelines\"",
                            "\"Opens new research directions in the intersection of A and B fields\""
                        ]
                    }
                },
                "critical_evaluation_areas": [
                    "Overall study quality and rigor",
                    "Appropriateness of methods for research questions",
                    "Strength and validity of conclusions",
                    "Practical significance and applicability",
                    "Contribution to existing knowledge",
                    "Clarity and completeness of reporting"
                ],
                "red_flags_to_note": [
                    "Mismatch between methods and research questions",
                    "Overgeneralization beyond study scope",
                    "Inadequate consideration of limitations",
                    "Poor integration of findings with existing literature",
                    "Unclear or unsupported conclusions",
                    "Significant methodological or ethical concerns"
                ]
            }
        }
        
        # Enhanced depth-specific instructions with detailed guidance for each level
        self.depth_instructions = {
            "quick": {
                "detail_level": "Concise summary focusing on key points only",
                "description": "Fast overview for quick understanding or screening purposes",
                "target_length": "500-800 words total",
                "time_estimate": "5-10 minutes to read",
                "length_guidance": "Brief bullet points and short paragraphs (2-3 sentences each)",
                "sections": "Focus on most important sections only (abstract, key findings, main conclusions)",
                "analysis_depth": "Surface-level analysis with main takeaways",
                "section_coverage": {
                    "required_sections": [
                        "Citation and metadata",
                        "Executive summary (2-3 sentences)",
                        "Key findings (3-5 bullet points)",
                        "Main conclusions (1-2 sentences)",
                        "Practical implications (1-2 sentences)"
                    ],
                    "optional_sections": [
                        "Brief methodology note if novel",
                        "Major limitations (1-2 key issues)",
                        "Future research (if explicitly stated)"
                    ],
                    "skip_sections": [
                        "Detailed literature review",
                        "In-depth methodology",
                        "Comprehensive statistical analysis",
                        "Extensive discussion"
                    ]
                },
                "writing_style": {
                    "tone": "Informative and direct",
                    "structure": "Bullet points and short paragraphs",
                    "detail_level": "High-level overview only",
                    "examples": "Minimal - only if crucial for understanding",
                    "quotes": "Sparingly - only for key findings",
                    "technical_detail": "Basic level - avoid complex terminology"
                },
                "quality_standards": {
                    "accuracy": "All information must be correct",
                    "completeness": "Cover essential points only",
                    "clarity": "Easily understood by non-experts",
                    "efficiency": "Maximum insight per word",
                    "actionability": "Clear takeaways for readers"
                }
            },
            "standard": {
                "detail_level": "Comprehensive analysis with detailed explanations",
                "description": "Thorough analysis suitable for most academic and professional purposes",
                "target_length": "1000-1500 words total",
                "time_estimate": "10-15 minutes to read",
                "length_guidance": "Full paragraphs with supporting details (4-6 sentences each)",
                "sections": "Cover all relevant sections thoroughly",
                "analysis_depth": "Moderate depth with explanations and context",
                "section_coverage": {
                    "required_sections": [
                        "Complete citation and metadata",
                        "Comprehensive executive summary",
                        "Research foundation and context",
                        "Methodology overview",
                        "Key findings with supporting details",
                        "Discussion and implications",
                        "Limitations and critiques",
                        "Future research directions"
                    ],
                    "detailed_sections": [
                        "Theoretical framework (if applicable)",
                        "Statistical results with interpretation",
                        "Practical applications",
                        "Connections to existing literature"
                    ],
                    "balanced_coverage": "All sections receive appropriate attention based on paper focus"
                },
                "writing_style": {
                    "tone": "Academic but accessible",
                    "structure": "Coherent paragraphs with logical flow",
                    "detail_level": "Sufficient depth for professional use",
                    "examples": "Include relevant examples to illustrate points",
                    "quotes": "Use direct quotes to support key arguments",
                    "technical_detail": "Appropriate complexity for target audience"
                },
                "quality_standards": {
                    "accuracy": "Precise representation of paper content",
                    "completeness": "Comprehensive coverage of important aspects",
                    "clarity": "Clear to specialists and informed readers",
                    "depth": "Sufficient detail for research and practice applications",
                    "integration": "Good connections between different aspects"
                }
            },
            "deep": {
                "detail_level": "In-depth analysis with extensive detail and critical evaluation",
                "description": "Comprehensive scholarly analysis for research, critical review, and advanced study purposes",
                "target_length": "1500-2500 words total",
                "time_estimate": "15-25 minutes to read",
                "length_guidance": "Detailed analysis with examples, context, and critical assessment",
                "sections": "Comprehensive coverage with critical analysis of all sections",
                "analysis_depth": "Deep analysis with critical evaluation, connections to broader literature, and detailed assessment",
                "section_coverage": {
                    "required_sections": [
                        "Complete bibliographic information",
                        "Detailed executive summary with context",
                        "Comprehensive research foundation",
                        "In-depth methodology analysis",
                        "Thorough results presentation and interpretation",
                        "Critical discussion and evaluation",
                        "Detailed limitations and critique",
                        "Extensive future research considerations",
                        "Personal research notes and connections"
                    ],
                    "critical_analysis": [
                        "Methodology strengths and weaknesses",
                        "Statistical appropriateness and interpretation",
                        "Theoretical contributions and innovations",
                        "Practical significance and applications",
                        "Integration with broader literature",
                        "Research quality and rigor assessment"
                    ],
                    "advanced_elements": [
                        "Cross-disciplinary connections",
                        "Methodological insights for future research",
                        "Theoretical implications and extensions",
                        "Policy and practice recommendations",
                        "Research replication and extension opportunities"
                    ]
                },
                "writing_style": {
                    "tone": "Scholarly and analytical",
                    "structure": "Detailed paragraphs with extensive supporting evidence",
                    "detail_level": "Comprehensive depth suitable for academic research",
                    "examples": "Multiple examples to illustrate complex points",
                    "quotes": "Extensive use of direct quotes with proper attribution",
                    "technical_detail": "Full technical complexity as appropriate"
                },
                "quality_standards": {
                    "accuracy": "Precise and nuanced representation",
                    "completeness": "Exhaustive coverage of all relevant aspects",
                    "clarity": "Clear to specialist audiences with complex content",
                    "depth": "Sufficient for advanced research and scholarly work",
                    "critique": "Thoughtful critical evaluation throughout",
                    "synthesis": "Strong integration and original insights"
                }
            }
        }
    
    def create_analysis_instructions(self, focus: str, depth: str) -> Dict[str, Any]:
        """
        Create comprehensive analysis instructions for Claude
        
        Args:
            focus: Analysis focus type (research, theory, method, review, balanced)
            depth: Analysis depth level (quick, standard, deep)
            
        Returns:
            Dict containing structured analysis instructions
        """
        focus_guidance = self.focus_instructions.get(focus, self.focus_instructions["balanced"])
        depth_guidance = self.depth_instructions.get(depth, self.depth_instructions["standard"])
        
        return {
            "focus_guidance": focus_guidance,
            "depth_guidance": depth_guidance,
            "general_instructions": self._get_general_instructions(),
            "template_filling_rules": self._get_template_filling_rules(),
            "extraction_guidelines": self._get_extraction_guidelines(focus, depth),
            "quality_criteria": self._get_quality_criteria(),
            "analysis_workflow": self._get_analysis_workflow(focus, depth)
        }
    
    def _get_general_instructions(self) -> List[str]:
        """Get general analysis instructions for Claude"""
        return [
            "Read and understand the entire paper content thoroughly before beginning analysis",
            "Extract information based on the specified focus area and depth level",
            "Fill the template with actual content from the paper, never use placeholder text",
            "Ensure all sections contain meaningful analysis derived from the paper",
            "Maintain academic tone and accuracy throughout the analysis",
            "Include specific examples and evidence from the paper to support your analysis",
            "Use direct quotes when they effectively illustrate key points",
            "Provide page references when possible for important claims or findings",
            "Ensure logical flow and coherence between different sections",
            "Adapt the analysis style to match the specified focus and depth requirements"
        ]
    
    def _get_template_filling_rules(self) -> List[str]:
        """Get template filling rules for Claude"""
        return [
            "Replace ALL placeholder text with actual content from the paper",
            "Use the paper's own terminology and concepts accurately",
            "Maintain consistent formatting throughout the document",
            "Include relevant figures, tables, and equation references where appropriate",
            "Ensure each section addresses its intended purpose based on the template structure",
            "Use bullet points and numbered lists where they improve readability",
            "Keep section lengths proportional to their importance and the specified depth level",
            "Cross-reference between sections when relevant connections exist",
            "Include proper citations and references as they appear in the original paper",
            "Ensure the final note is self-contained and comprehensible without the original paper"
        ]
    
    def _get_extraction_guidelines(self, focus: str, depth: str) -> Dict[str, Any]:
        """Get specific extraction guidelines based on focus and depth"""
        guidelines = {
            "content_priorities": self.focus_instructions.get(focus, self.focus_instructions["balanced"])["extract"],
            "section_emphasis": self.focus_instructions.get(focus, self.focus_instructions["balanced"])["key_sections"],
            "detail_requirements": self.depth_instructions.get(depth, self.depth_instructions["standard"]),
            "specific_elements": []
        }
        
        # Add focus-specific extraction elements
        if focus == "research":
            guidelines["specific_elements"] = [
                "Sample sizes and demographic information",
                "Statistical methods and significance levels",
                "Effect sizes and confidence intervals",
                "Control variables and experimental conditions"
            ]
        elif focus == "theory":
            guidelines["specific_elements"] = [
                "Mathematical formulations and proofs",
                "Theoretical assumptions and constraints",
                "Model parameters and variables",
                "Theoretical predictions and implications"
            ]
        elif focus == "method":
            guidelines["specific_elements"] = [
                "Step-by-step procedures",
                "Equipment and software specifications",
                "Validation protocols and benchmarks",
                "Performance metrics and evaluation criteria"
            ]
        elif focus == "review":
            guidelines["specific_elements"] = [
                "Search strategies and inclusion criteria",
                "Number of studies reviewed",
                "Synthesis methods and frameworks",
                "Identified trends and patterns"
            ]
        
        return guidelines
    
    def _get_quality_criteria(self) -> List[str]:
        """Get quality criteria for the analysis"""
        return [
            "Accuracy: All information must be accurately extracted from the paper",
            "Completeness: All relevant aspects should be covered based on focus and depth",
            "Clarity: Analysis should be clear and understandable to someone unfamiliar with the paper",
            "Relevance: Content should be relevant to the specified focus area",
            "Depth: Analysis depth should match the specified level (quick/standard/deep)",
            "Structure: Follow the template structure while ensuring logical flow",
            "Evidence: Support claims with specific evidence from the paper",
            "Objectivity: Maintain objective tone while providing critical analysis when appropriate"
        ]
    
    def _get_analysis_workflow(self, focus: str, depth: str) -> List[str]:
        """Get step-by-step analysis workflow for Claude"""
        workflow = [
            "1. Initial Reading: Read through the entire paper to understand the overall structure and content",
            "2. Focus Identification: Identify sections and content most relevant to the specified focus area",
            "3. Key Information Extraction: Extract key information based on the focus-specific guidelines",
            "4. Template Structure Review: Review the template structure to understand required sections",
            "5. Content Organization: Organize extracted information according to template sections",
            f"6. Depth Adjustment: Adjust detail level to match '{depth}' depth requirements",
            "7. Section-by-Section Filling: Fill each template section with relevant, accurate content",
            "8. Cross-Reference Check: Ensure consistency and logical connections between sections",
            "9. Quality Review: Review for accuracy, completeness, and adherence to guidelines",
            "10. Final Polish: Ensure proper formatting, flow, and academic tone"
        ]
        
        return workflow
    
    def create_error_guidance(self, error_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create comprehensive guidance for Claude when encountering specific errors
        
        Args:
            error_type: Type of error encountered
            context: Additional context information for enhanced guidance
            
        Returns:
            Dict containing structured guidance for Claude
        """
        context = context or {}
        
        error_guidance = {
            "insufficient_content": {
                "primary_guidance": (
                    "The PDF content appears to be insufficient for comprehensive analysis. "
                    "This may be due to poor OCR extraction, image-based PDFs, or very short documents."
                ),
                "analysis_approach": [
                    "Work with the available content, however limited",
                    "Clearly indicate which sections could not be completed due to insufficient information",
                    "Provide analysis for sections that do have adequate content",
                    "Use placeholders like '[Content insufficient for analysis]' where needed",
                    "Focus on extracting whatever meaningful information is available"
                ],
                "template_adaptations": [
                    "Fill sections with available content only",
                    "Mark incomplete sections clearly",
                    "Prioritize metadata extraction if content is minimal",
                    "Include a note about content limitations in the summary"
                ],
                "quality_expectations": "Provide the best possible analysis given the content limitations, with clear documentation of what could not be analyzed."
            },
            "corrupted_pdf": {
                "primary_guidance": (
                    "The PDF content appears corrupted, poorly extracted, or contains significant OCR errors. "
                    "Text may be garbled, incomplete, or contain extraction artifacts."
                ),
                "analysis_approach": [
                    "Work with the readable portions of the text",
                    "Note sections where content seems incomplete or garbled",
                    "Focus on clearly readable portions for analysis",
                    "Indicate areas of uncertainty due to poor text quality",
                    "Attempt to infer meaning from context where text is unclear"
                ],
                "template_adaptations": [
                    "Mark uncertain sections with qualifiers like '[text unclear]'",
                    "Prioritize sections with better text quality",
                    "Include notes about text extraction issues",
                    "Focus on extractable metadata and clear sections"
                ],
                "quality_expectations": "Provide analysis based on readable content while clearly marking areas affected by extraction issues."
            },
            "unsupported_format": {
                "primary_guidance": (
                    "This document format may not be suitable for standard academic analysis. "
                    "It may be a non-academic document, presentation, or differently structured content."
                ),
                "analysis_approach": [
                    "Adapt the analysis approach to the available content type",
                    "Identify the document type and adjust expectations accordingly",
                    "Extract relevant information based on document structure",
                    "Clearly indicate deviations from standard academic analysis",
                    "Focus on the most relevant analytical aspects available"
                ],
                "template_adaptations": [
                    "Modify template sections to match document type",
                    "Skip sections not applicable to the document format",
                    "Add notes about format adaptations made",
                    "Focus on extractable content rather than forcing template structure"
                ],
                "quality_expectations": "Provide appropriate analysis for the document type while noting format limitations and adaptations."
            },
            "template_error": {
                "primary_guidance": (
                    "There was an issue loading the specified template. "
                    "You'll need to create a structured analysis without template guidance."
                ),
                "analysis_approach": [
                    "Create a comprehensive analysis following standard academic format",
                    "Include all essential sections for literature note analysis",
                    "Maintain professional academic structure and tone",
                    "Ensure comprehensive coverage of the paper's content"
                ],
                "template_adaptations": [
                    "Use standard academic paper analysis structure",
                    "Include: Citation, Summary, Methodology, Findings, Implications, Limitations",
                    "Adapt section depth based on specified analysis depth level",
                    "Maintain focus area emphasis even without template guidance"
                ],
                "quality_expectations": "Provide a complete, well-structured analysis that meets academic literature note standards."
            },
            "focus_mismatch": {
                "primary_guidance": (
                    "The paper content may not align well with the specified focus area. "
                    "The document may be from a different domain or have different emphasis than expected."
                ),
                "analysis_approach": [
                    "Identify the most relevant aspects available in the paper",
                    "Adapt analysis to emphasize content that best matches the focus",
                    "Clearly explain how the analysis has been adapted",
                    "Include content from the specified focus area if any exists",
                    "Provide broader analysis if focus-specific content is limited"
                ],
                "template_adaptations": [
                    "Emphasize sections most relevant to available content",
                    "Note adaptations made due to content-focus mismatch",
                    "Include additional relevant sections if beneficial",
                    "Maintain template structure while adapting content emphasis"
                ],
                "quality_expectations": "Provide valuable analysis by adapting focus to match available content while noting the adaptations made."
            },
            "file_access_error": {
                "primary_guidance": (
                    "The file could not be accessed or read. This may be due to permissions, "
                    "file corruption, or the file being in use by another application."
                ),
                "analysis_approach": [
                    "This error prevents content analysis",
                    "No analysis can be performed without file access",
                    "Verify file path and permissions",
                    "Ensure file is not corrupted or locked"
                ],
                "template_adaptations": [
                    "Cannot generate analysis without content access",
                    "Provide error information instead of analysis",
                    "Include troubleshooting suggestions"
                ],
                "quality_expectations": "Cannot perform analysis due to file access issues. Provide clear error information and troubleshooting guidance."
            },
            "network_error": {
                "primary_guidance": (
                    "A network-related error occurred during processing. This may affect "
                    "content extraction or template loading."
                ),
                "analysis_approach": [
                    "Work with locally available content if any",
                    "Note which operations may have been affected",
                    "Provide analysis based on successfully retrieved content",
                    "Indicate network-related limitations"
                ],
                "template_adaptations": [
                    "Use fallback templates if primary template unavailable",
                    "Note any network-related limitations",
                    "Focus on offline-capable analysis"
                ],
                "quality_expectations": "Provide analysis with available resources while noting network-related limitations."
            }
        }
        
        # Get guidance for the specific error type
        guidance = error_guidance.get(error_type, {
            "primary_guidance": "An unexpected issue occurred during processing.",
            "analysis_approach": [
                "Analyze any available content to the best of your ability",
                "Clearly indicate limitations and uncertainties",
                "Provide whatever meaningful analysis is possible",
                "Note any issues encountered during analysis"
            ],
            "template_adaptations": [
                "Adapt template usage based on available content",
                "Mark uncertain or incomplete sections clearly",
                "Focus on providing value where possible"
            ],
            "quality_expectations": "Provide the best possible analysis given the circumstances while clearly documenting limitations."
        })
        
        # Add context-specific information if available
        if context:
            guidance["context_info"] = context
            
        return guidance
    
    def create_batch_analysis_instructions(self, focus: str, depth: str, file_count: int) -> Dict[str, Any]:
        """
        Create comprehensive analysis instructions for batch processing multiple papers
        
        Enhanced to support efficient and consistent analysis across multiple papers
        while maintaining quality and providing comprehensive guidance for Claude.
        
        Args:
            focus: Analysis focus type
            depth: Analysis depth level
            file_count: Number of files in the batch
            
        Returns:
            Dict containing comprehensive batch analysis instructions
        """
        base_instructions = self.create_analysis_instructions(focus, depth)
        
        # Determine batch size category for tailored guidance
        if file_count <= 3:
            batch_category = "small"
        elif file_count <= 10:
            batch_category = "medium"
        else:
            batch_category = "large"
        
        # Enhanced batch-specific guidance
        batch_guidance = {
            "batch_overview": {
                "total_papers": file_count,
                "batch_category": batch_category,
                "focus_area": focus,
                "depth_level": depth,
                "estimated_time": self._estimate_batch_processing_time(file_count, depth),
                "complexity_assessment": self._assess_batch_complexity(file_count, focus, depth)
            },
            "batch_processing_approach": [
                f"You are analyzing {file_count} papers in {batch_category} batch mode",
                "Each paper should receive individual attention using the same analytical framework",
                "Maintain consistent analysis depth and focus across all papers for comparability",
                "Generate complete, self-contained literature notes for each paper",
                "Use identical template structure and section organization for all papers",
                "Apply the same quality standards and evaluation criteria throughout"
            ],
            "consistency_requirements": {
                "analytical_consistency": [
                    "Apply identical analysis depth to each paper",
                    "Use consistent terminology and conceptual frameworks",
                    "Maintain uniform quality standards across all analyses",
                    "Apply the same critical evaluation criteria to each paper"
                ],
                "structural_consistency": [
                    "Use identical template structure for all papers",
                    "Maintain consistent section organization and formatting",
                    "Apply uniform citation and reference styles",
                    "Use consistent headings and organizational patterns"
                ],
                "quality_consistency": [
                    "Ensure comparable comprehensiveness across all analyses",
                    "Maintain consistent writing style and academic tone",
                    "Apply uniform evidence standards and source requirements",
                    "Provide consistent level of critical evaluation"
                ]
            },
            "batch_workflow": {
                "preparation_phase": [
                    "1. Review batch summary and understand scope of all papers",
                    "2. Identify any apparent thematic connections between papers",
                    "3. Note any papers that may require special handling",
                    "4. Confirm analysis framework and template structure"
                ],
                "processing_phase": [
                    "5. Process each paper individually using the established framework",
                    "6. Generate complete literature note for each paper",
                    "7. Ensure each note is self-contained and professionally complete",
                    "8. Apply consistent quality review to each completed analysis"
                ],
                "quality_assurance": [
                    "9. Review all analyses for consistency in depth and quality",
                    "10. Check that all papers received appropriate attention",
                    "11. Verify that analysis standards were maintained throughout",
                    "12. Confirm that batch processing goals were achieved"
                ]
            },
            "efficiency_strategies": {
                "focus_optimization": [
                    f"Concentrate on {focus}-specific elements to maintain efficiency",
                    "Use the structured template to ensure systematic coverage",
                    "Prioritize accuracy and completeness over processing speed",
                    "Leverage pattern recognition across similar papers"
                ],
                "time_management": [
                    f"Target {self._get_time_per_paper(depth)} per paper for {depth} analysis",
                    "Allocate extra time for complex or challenging papers",
                    "Use batch processing momentum to maintain analytical flow",
                    "Schedule quality review time for the entire batch"
                ],
                "quality_maintenance": [
                    "Maintain high standards regardless of batch size",
                    "Take breaks if needed to prevent analysis fatigue",
                    "Use cross-paper insights to enhance individual analyses",
                    "Document any processing challenges encountered"
                ]
            },
            "special_handling": {
                "problematic_papers": [
                    "Clearly indicate papers with insufficient content",
                    "Note any papers requiring format adaptations",
                    "Document extraction or processing issues encountered",
                    "Maintain analysis quality even for challenging papers"
                ],
                "comparative_opportunities": [
                    "Note methodological similarities and differences across papers",
                    "Identify theoretical connections and contradictions",
                    "Recognize complementary findings or conflicting results",
                    "Consider cumulative insights from the paper set"
                ],
                "batch_insights": [
                    "Document any emerging patterns across the paper set",
                    "Note thematic connections or research trends observed",
                    "Identify potential synthesis opportunities",
                    "Consider implications of the collective research"
                ]
            }
        }
        
        # Batch-specific quality standards
        batch_quality_standards = {
            "individual_paper_quality": "Each paper analysis must meet full quality standards",
            "batch_consistency": "All analyses must be comparable in depth and rigor",
            "comprehensive_coverage": "No paper should receive superficial treatment",
            "professional_presentation": "All notes must be publication-ready",
            "analytical_integrity": "Maintain objective analysis throughout the batch"
        }
        
        # Combine base instructions with enhanced batch guidance
        batch_instructions = {
            **base_instructions,
            "batch_guidance": batch_guidance,
            "batch_quality_standards": batch_quality_standards,
            "batch_size": file_count,
            "batch_category": batch_category,
            "processing_mode": "batch",
            "batch_completion_criteria": self._get_batch_completion_criteria(file_count, focus, depth)
        }
        
        return batch_instructions
    
    def _estimate_batch_processing_time(self, file_count: int, depth: str) -> str:
        """Estimate total processing time for batch analysis"""
        time_per_paper = {"quick": 8, "standard": 15, "deep": 25}  # minutes
        base_time = file_count * time_per_paper.get(depth, 15)
        overhead = max(5, file_count * 2)  # Setup and quality review overhead
        total_minutes = base_time + overhead
        
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
    
    def _assess_batch_complexity(self, file_count: int, focus: str, depth: str) -> str:
        """Assess the complexity of the batch processing task"""
        complexity_score = 0
        
        # File count factor
        if file_count <= 3:
            complexity_score += 1
        elif file_count <= 10:
            complexity_score += 2
        else:
            complexity_score += 3
        
        # Depth factor
        depth_scores = {"quick": 1, "standard": 2, "deep": 3}
        complexity_score += depth_scores.get(depth, 2)
        
        # Focus factor (some focuses are more demanding)
        focus_scores = {"balanced": 1, "research": 2, "theory": 3, "method": 2, "review": 2}
        complexity_score += focus_scores.get(focus, 1)
        
        if complexity_score <= 3:
            return "Low complexity - straightforward batch processing"
        elif complexity_score <= 6:
            return "Medium complexity - requires systematic approach"
        else:
            return "High complexity - demands careful attention and time management"
    
    def _get_time_per_paper(self, depth: str) -> str:
        """Get target time allocation per paper"""
        time_targets = {
            "quick": "5-8 minutes",
            "standard": "12-18 minutes", 
            "deep": "20-30 minutes"
        }
        return time_targets.get(depth, "12-18 minutes")
    
    def _get_batch_completion_criteria(self, file_count: int, focus: str, depth: str) -> Dict[str, Any]:
        """Define criteria for successful batch completion"""
        return {
            "all_papers_processed": f"All {file_count} papers have complete literature notes",
            "quality_maintained": f"All analyses meet {depth} depth requirements",
            "consistency_achieved": f"All papers analyzed with {focus} focus consistently",
            "standards_met": "All notes are self-contained and professionally complete",
            "documentation_complete": "Any processing issues or special cases are documented"
        }
    
    def create_fallback_instructions(self, focus: str, depth: str, fallback_reason: str) -> Dict[str, Any]:
        """
        Create fallback analysis instructions when normal processing fails
        
        Args:
            focus: Analysis focus type
            depth: Analysis depth level
            fallback_reason: Reason for fallback (template_error, content_error, etc.)
            
        Returns:
            Dict containing fallback analysis instructions
        """
        base_instructions = self.create_analysis_instructions(focus, depth)
        
        fallback_guidance = {
            "fallback_reason": fallback_reason,
            "emergency_instructions": [
                "Adapt analysis approach to available resources",
                "Provide valuable analysis despite technical limitations",
                "Clearly document what adaptations were made",
                "Focus on delivering useful insights with available content",
                "Maintain professional academic standards throughout"
            ],
            "content_strategy": {
                "template_error": [
                    "Create analysis using standard academic structure",
                    "Include: Citation, Summary, Key Findings, Methodology, Implications",
                    "Adapt sections based on focus and depth requirements",
                    "Maintain comprehensive coverage despite template issues"
                ],
                "content_error": [
                    "Work with whatever content is available",
                    "Note content limitations clearly",
                    "Extract maximum value from available text",
                    "Use inference and context where appropriate"
                ],
                "system_error": [
                    "Provide analysis based on successfully processed information",
                    "Note which systems or processes were affected",
                    "Focus on offline-capable analysis methods",
                    "Deliver value despite technical constraints"
                ]
            },
            "quality_assurance": [
                "Maintain accuracy standards despite limitations",
                "Clearly mark uncertain or inferred content",
                "Provide confidence indicators for different sections",
                "Document all adaptations and limitations",
                "Ensure analysis remains useful and actionable"
            ],
            "output_requirements": [
                "Include clear notes about fallback adaptations",
                "Maintain readable and professional format",
                "Provide executive summary highlighting key points",
                "Include troubleshooting information if relevant",
                "End with clear next steps or recommendations"
            ]
        }
        
        # Combine base instructions with fallback guidance
        fallback_instructions = {
            **base_instructions,
            "fallback_guidance": fallback_guidance,
            "processing_mode": "fallback",
            "adaptation_level": "high"
        }
        
        return fallback_instructions
    
    def create_edge_case_guidance(self, case_type: str, severity: str = "medium") -> Dict[str, Any]:
        """
        Create guidance for handling edge cases during analysis
        
        Args:
            case_type: Type of edge case (short_content, mixed_language, etc.)
            severity: Severity level (low, medium, high)
            
        Returns:
            Dict containing edge case handling guidance
        """
        edge_cases = {
            "short_content": {
                "description": "Document contains very limited content for analysis",
                "handling_strategy": [
                    "Focus on extracting maximum value from available content",
                    "Prioritize metadata and clear summary information",
                    "Use bullet points for concise information presentation",
                    "Note content limitations prominently",
                    "Avoid padding with speculative content"
                ],
                "template_modifications": [
                    "Combine similar sections to reduce redundancy",
                    "Focus on most important sections only",
                    "Use abbreviated format for minimal content sections",
                    "Include content length disclaimer"
                ]
            },
            "mixed_language": {
                "description": "Document contains multiple languages or non-English content",
                "handling_strategy": [
                    "Focus analysis on English-language portions",
                    "Note presence of other languages",
                    "Extract translatable key terms where beneficial",
                    "Use context to infer meaning where possible",
                    "Clearly mark language-related limitations"
                ],
                "template_modifications": [
                    "Include language composition note",
                    "Focus on universally understandable content",
                    "Note foreign language sections that couldn't be analyzed"
                ]
            },
            "technical_content": {
                "description": "Document contains highly technical or specialized content",
                "handling_strategy": [
                    "Extract general principles and approaches",
                    "Focus on methodology and results rather than technical details",
                    "Provide context for specialized terminology",
                    "Emphasize broader implications and applications",
                    "Note technical complexity level"
                ],
                "template_modifications": [
                    "Add technical complexity indicator",
                    "Include glossary section if needed",
                    "Focus on accessible summary sections",
                    "Emphasize practical applications"
                ]
            },
            "image_heavy": {
                "description": "Document is heavily dependent on images, figures, or charts",
                "handling_strategy": [
                    "Focus on text-based content and captions",
                    "Note the presence and importance of visual elements",
                    "Extract figure and table references where possible",
                    "Emphasize textual descriptions of visual content",
                    "Indicate visual content limitations"
                ],
                "template_modifications": [
                    "Include visual content disclaimer",
                    "Focus on text-extractable information",
                    "Note references to figures and tables",
                    "Emphasize need for original document review"
                ]
            },
            "old_format": {
                "description": "Document uses older formatting or non-standard structure",
                "handling_strategy": [
                    "Adapt to document's native structure",
                    "Extract content based on recognizable patterns",
                    "Use contextual clues for section identification",
                    "Focus on substantive content over format consistency",
                    "Note formatting challenges encountered"
                ],
                "template_modifications": [
                    "Adapt section mapping to document structure",
                    "Include format adaptation notes",
                    "Focus on content extraction over template conformity"
                ]
            }
        }
        
        guidance = edge_cases.get(case_type, {
            "description": "Unrecognized edge case encountered",
            "handling_strategy": [
                "Apply general robust analysis principles",
                "Adapt approach based on observed content characteristics",
                "Document unusual aspects encountered",
                "Provide best-effort analysis with noted limitations"
            ],
            "template_modifications": [
                "Adapt template usage as needed",
                "Note any unusual adaptations made"
            ]
        })
        
        # Add severity-based modifications
        if severity == "high":
            guidance["severity_note"] = "High-impact edge case requiring significant adaptation"
            guidance["quality_note"] = "Analysis quality may be significantly affected"
        elif severity == "low":
            guidance["severity_note"] = "Minor edge case with minimal impact"
            guidance["quality_note"] = "Analysis quality should be minimally affected"
        else:
            guidance["severity_note"] = "Moderate edge case requiring some adaptation"
            guidance["quality_note"] = "Analysis quality may be moderately affected"
            
        return guidance
    
    def create_discourse_analysis_instructions(self, focus: str, depth: str, field: str, section_filter: str) -> Dict[str, Any]:
        """Create instructions for discourse pattern analysis (sq:codelang)"""
        
        # Define focus-specific discourse analysis instructions
        discourse_focus_instructions = {
            "discourse": {
                "description": "Complete rhetorical and linguistic analysis of academic discourse",
                "analysis_areas": [
                    "Argument structure and logical flow",
                    "Topic introduction and highlighting patterns",
                    "Field-specific terminology and expressions",
                    "Rhetorical strategies and positioning",
                    "Section-specific language patterns",
                    "Discovered linguistic functions"
                ]
            },
            "architecture": {
                "description": "Focus on argument structure and logical flow patterns",
                "analysis_areas": [
                    "How the author builds their overall argument",
                    "Topic introduction and highlighting expressions",
                    "Logical transitions and connection patterns",
                    "Narrative structure and flow"
                ]
            },
            "terminology": {
                "description": "Focus on domain-specific vocabulary and technical expressions",
                "analysis_areas": [
                    "Field-specific vocabulary and technical terms",
                    "Mathematical and technical expressions",
                    "Methodological language patterns",
                    "Specialized notation and conventions"
                ]
            },
            "rhetoric": {
                "description": "Focus on persuasion strategies and authority positioning", 
                "analysis_areas": [
                    "Evidence presentation patterns",
                    "Authority and credibility building",
                    "Gap identification and contribution claims",
                    "Persuasion techniques and rhetoric"
                ]
            },
            "sections": {
                "description": "Focus on section-specific language patterns",
                "analysis_areas": [
                    "Introduction language patterns",
                    "Methods section expressions", 
                    "Results presentation language",
                    "Discussion and conclusion patterns"
                ]
            },
            "functions": {
                "description": "Focus on discovered linguistic functions",
                "analysis_areas": [
                    "Functional categories of expressions",
                    "Purpose-based language groupings",
                    "Communication strategies by function"
                ]
            },
            "summary": {
                "description": "Focus on key insights and writing conventions",
                "analysis_areas": [
                    "Primary discourse strategy",
                    "Field convention adherence",
                    "Unique language innovations",
                    "Expression frequency patterns"
                ]
            }
        }
        
        focus_instruction = discourse_focus_instructions.get(focus, discourse_focus_instructions["discourse"])
        
        # Create comprehensive discourse analysis instructions
        instructions = {
            "analysis_type": "discourse_pattern_analysis",
            "focus": focus,
            "depth": depth,
            "field": field,
            "section_filter": section_filter,
            "focus_description": focus_instruction["description"],
            "analysis_areas": focus_instruction["analysis_areas"],
            
            "primary_objectives": [
                f"Extract and analyze discourse patterns with focus on {focus}",
                "Identify the 'code language' used in this academic field",
                "Discover how the author structures arguments and presents ideas",
                "Find field-specific expressions and rhetorical strategies",
                "Map linguistic functions to communication purposes"
            ],
            
            "analysis_methodology": [
                "Read through the entire document to understand overall structure",
                "Identify patterns in how the author introduces topics and makes claims",
                "Extract actual expressions and phrases (not just describe them)",
                "Group expressions by their rhetorical and linguistic functions",
                "Analyze field-specific language and terminology usage",
                "Map argument structure and logical progression",
                "Discover unique or innovative language use"
            ],
            
            "extraction_guidelines": [
                "Extract ACTUAL expressions from the text, not examples",
                "Provide context for where each expression appears",
                "Note the frequency and function of each pattern",
                "Identify both explicit and implicit rhetorical moves",
                "Focus on how language serves argumentative purposes",
                "Document field-specific conventions and innovations"
            ],
            
            "output_requirements": [
                "Fill the template with discovered patterns and expressions",
                "Use specific quotes and examples from the paper",
                "Organize findings by rhetorical and linguistic functions",
                "Provide clear analysis of discourse strategies",
                "Note field conventions and unique innovations",
                "Create actionable insights for academic writing"
            ],
            
            "field_awareness": self._get_field_specific_guidance(field),
            "depth_specifications": self._get_discourse_depth_specs(depth),
            "section_focus": self._get_section_filter_guidance(section_filter)
        }
        
        return instructions
    
    def create_batch_discourse_instructions(self, focus: str, depth: str, field: str, section_filter: str, file_count: int) -> Dict[str, Any]:
        """Create instructions for batch discourse analysis"""
        
        base_instructions = self.create_discourse_analysis_instructions(focus, depth, field, section_filter)
        
        # Modify for batch analysis
        batch_instructions = base_instructions.copy()
        batch_instructions.update({
            "analysis_type": "batch_discourse_analysis",
            "file_count": file_count,
            "batch_objectives": [
                f"Analyze discourse patterns across {file_count} papers",
                "Identify common and unique patterns across papers",
                "Compare rhetorical strategies between authors",
                "Find field-wide conventions and individual innovations",
                "Create a unified analysis of discourse patterns"
            ],
            
            "batch_methodology": [
                "Analyze each paper's discourse patterns individually",
                "Identify patterns that appear across multiple papers",
                "Note variations and unique approaches by different authors",
                "Compare rhetorical strategies and linguistic choices",
                "Synthesize findings into unified discourse analysis",
                "Highlight both common conventions and individual innovations"
            ],
            
            "comparative_analysis": [
                "Compare argument structures across papers",
                "Identify common vs. unique expression patterns",
                "Note field conventions vs. individual style",
                "Analyze evolution of discourse patterns",
                "Find cross-paper linguistic functions",
                "Document stylistic variations and innovations"
            ],
            
            "output_format": [
                "Create ONE combined analysis file",
                "Organize by discourse patterns, not by individual papers",
                "Show comparative analysis between authors",
                "Highlight common field conventions",
                "Note unique innovations and variations",
                "Provide unified insights about the field's discourse"
            ]
        })
        
        return batch_instructions
    
    def _get_field_specific_guidance(self, field: str) -> Dict[str, Any]:
        """Get field-specific discourse analysis guidance"""
        
        field_guidance = {
            "physics": {
                "common_patterns": ["theoretical derivation", "experimental validation", "model prediction"],
                "typical_expressions": ["We derive", "The model predicts", "Experimental results show"],
                "field_conventions": "Physics papers often use mathematical derivations and experimental validation"
            },
            "computer_science": {
                "common_patterns": ["algorithmic description", "performance evaluation", "implementation details"],
                "typical_expressions": ["We implement", "The algorithm achieves", "Performance evaluation reveals"],
                "field_conventions": "CS papers focus on algorithmic innovation and performance metrics"
            },
            "biology": {
                "common_patterns": ["experimental observation", "mechanism description", "statistical analysis"],
                "typical_expressions": ["We observe", "The mechanism involves", "Statistical analysis indicates"],
                "field_conventions": "Biology papers emphasize empirical observation and mechanistic explanation"
            },
            "auto-detect": {
                "common_patterns": ["varied based on detected field"],
                "typical_expressions": ["context-dependent"],
                "field_conventions": "Analyze patterns without field-specific assumptions"
            }
        }
        
        return field_guidance.get(field, field_guidance["auto-detect"])
    
    def _get_discourse_depth_specs(self, depth: str) -> Dict[str, Any]:
        """Get depth-specific specifications for discourse analysis"""
        
        depth_specs = {
            "quick": {
                "analysis_scope": "Surface-level discourse patterns",
                "detail_level": "Basic pattern identification",
                "expected_patterns": "10-20 key expressions",
                "focus_areas": ["primary argument structure", "main rhetorical moves"]
            },
            "standard": {
                "analysis_scope": "Comprehensive discourse analysis",
                "detail_level": "Detailed pattern extraction and analysis",
                "expected_patterns": "30-50 expressions with context",
                "focus_areas": ["argument structure", "rhetorical strategies", "field conventions", "linguistic functions"]
            },
            "deep": {
                "analysis_scope": "Exhaustive discourse and rhetorical analysis",
                "detail_level": "Thorough extraction with functional analysis",
                "expected_patterns": "50+ expressions with detailed analysis",
                "focus_areas": ["complete discourse mapping", "rhetorical innovation", "stylistic analysis", "field evolution"]
            }
        }
        
        return depth_specs.get(depth, depth_specs["standard"])
    
    def _get_section_filter_guidance(self, section_filter: str) -> Dict[str, Any]:
        """Get section-specific analysis guidance"""
        
        section_guidance = {
            "all": {
                "scope": "Analyze discourse patterns across all sections",
                "approach": "Comprehensive analysis of entire paper"
            },
            "introduction": {
                "scope": "Focus on introduction section discourse",
                "key_patterns": ["topic highlighting", "gap identification", "contribution claims"],
                "approach": "Analyze how authors introduce topics and position their work"
            },
            "methods": {
                "scope": "Focus on methodology section discourse",
                "key_patterns": ["procedure description", "validation language", "technical precision"],
                "approach": "Analyze methodological language and technical communication"
            },
            "results": {
                "scope": "Focus on results section discourse",
                "key_patterns": ["finding presentation", "evidence language", "statistical reporting"],
                "approach": "Analyze how findings are presented and supported"
            },
            "discussion": {
                "scope": "Focus on discussion section discourse",
                "key_patterns": ["interpretation language", "implication discussion", "limitation acknowledgment"],
                "approach": "Analyze how authors interpret and contextualize their findings"
            }
        }
        
        return section_guidance.get(section_filter, section_guidance["all"])