<!-- COMPREHENSIVE ANALYSIS INSTRUCTIONS FOR CLAUDE AI -->
<!--
TEMPLATE: Balanced Literature Note Analysis
FOCUS: Comprehensive coverage of all aspects of the paper
DEPTH: Adjustable based on depth parameter (quick/standard/deep)

CRITICAL INSTRUCTIONS:
This template provides balanced coverage of theoretical, methodological, and practical aspects.
Read the entire paper thoroughly and extract information for each section below.

KEY ANALYSIS PRINCIPLES:
1. Extract actual content from the paper - NEVER use placeholder text
2. Support all statements with specific evidence from the paper
3. Maintain academic objectivity while providing critical analysis
4. Include page references when possible (e.g., "As stated on page 15...")
5. Use direct quotes sparingly but effectively to illustrate key points
6. Ensure coherent flow between sections
7. Adapt detail level based on the specified depth parameter

SECTION-BY-SECTION GUIDANCE:
Each section below contains specific instructions for what to extract and how to analyze it.
Follow these instructions carefully to produce a comprehensive literature note.
-->

# {{ title }}

<!-- METADATA SECTION: Extract bibliographic information exactly as it appears -->
<!--
INSTRUCTIONS: Fill metadata fields with exact information from the paper.
- Use paper's exact title, author names, and publication details
- Convert publication year to integer format
- Generate appropriate citekey if not provided
- Extract DOI if available in the paper
-->
> [!Metadata]
> **FirstAuthor**:: {{ first_author }}
{%- for author in authors %}
> **Author**:: {{ author }}
{%- endfor %}
> **Title**:: {{ title }}
> **Year**:: {{ year or "Unknown" }}
> **Citekey**:: {{ citekey }}
> **itemType**:: {{ item_type }}
{%- if journal %}
> **Journal**:: *{{ journal }}*
{%- endif %}
{%- if volume %}
> **Volume**:: {{ volume }}
{%- endif %}
{%- if issue %}
> **Issue**:: {{ issue }}
{%- endif %}
{%- if pages %}
> **Pages**:: {{ pages }}
{%- endif %}
{%- if doi %}
> **DOI**:: {{ doi }}
{%- endif %}

## Executive Summary

<!-- RESEARCH OVERVIEW: Provide a concise but comprehensive overview -->
<!--
INSTRUCTIONS: Extract and synthesize the paper's main purpose, approach, and significance.
- Identify the central research problem or question
- Summarize the overall approach and methodology
- Highlight the paper's main contribution to the field
- Keep concise but informative (2-4 sentences)
EXAMPLE: "This study investigates the impact of X on Y using a randomized controlled trial with N participants. The authors developed a novel Z methodology to address limitations in previous research. Results demonstrate significant effects of X on Y, with implications for both theory and practice."
-->
### Research Overview
{{ research_overview or "Comprehensive overview of the study's purpose, approach, and significance" }}

<!-- KEY CONTRIBUTIONS: List the paper's primary contributions -->
<!--
INSTRUCTIONS: Identify and list the paper's main contributions to knowledge.
- Look for explicit statements of contributions in introduction/conclusion
- Include theoretical, methodological, and practical contributions
- Be specific about what is novel or innovative
- Typically 2-4 key contributions
EXAMPLES:
- "Novel machine learning algorithm that improves accuracy by 15% over existing methods"
- "First empirical evidence for the relationship between X and Y in population Z"
- "Theoretical framework that unifies previously disparate approaches"
-->
### Key Contributions
{%- if key_contributions %}
{%- for contribution in key_contributions %}
- {{ contribution }}
{%- endfor %}
{%- else %}
- Primary theoretical or methodological contribution
- Novel findings or insights
- Practical applications or implications
{%- endif %}

<!-- SIGNIFICANCE: Explain why this work matters -->
<!--
INSTRUCTIONS: Extract the paper's significance and impact to the field.
- Look for discussions of implications in introduction and conclusion
- Consider both immediate and long-term significance
- Include impact on theory, practice, and future research
- Be specific about who would benefit and how
EXAMPLE: "This work significantly advances our understanding of X by providing the first empirical validation of theory Y, with direct applications for practitioners in field Z."
-->
### Significance
{{ significance or "Impact and importance of this work to the field" }}

## Research Foundation

<!-- RESEARCH QUESTION & OBJECTIVES: Extract the study's core questions -->
<!--
INSTRUCTIONS: Identify the main research questions, hypotheses, and objectives.
- Look in introduction, abstract, and methods sections
- Include both explicit research questions and implicit objectives
- Distinguish between primary and secondary questions if applicable
- Include hypotheses if stated
EXAMPLE: "The study addresses three main questions: (1) How does X affect Y? (2) What mechanisms underlie this relationship? (3) Do these effects vary across different populations?"
-->
### Research Question & Objectives
{{ research_question or "Primary research questions and study objectives" }}

<!-- THEORETICAL FRAMEWORK: Describe the conceptual foundation -->
<!--
INSTRUCTIONS: Extract the theoretical foundation and conceptual framework.
- Identify key theories, models, or frameworks used
- Explain how these theories inform the research
- Include any theoretical innovations or extensions
- Look in introduction and literature review sections
EXAMPLE: "The study builds on Social Cognitive Theory and the Technology Acceptance Model to develop an integrated framework for understanding user adoption of AI systems."
-->
### Theoretical Framework
{{ theoretical_framework or "Underlying theoretical principles and conceptual foundation" }}

<!-- LITERATURE CONTEXT: Explain how this work builds on existing research -->
<!--
INSTRUCTIONS: Summarize how this work relates to and builds upon existing literature.
- Identify key prior studies that inform this work
- Highlight gaps in existing research that this study addresses
- Show progression of knowledge in the field
- Note controversies or debates this work addresses
EXAMPLE: "While previous studies (Smith, 2020; Jones, 2021) established the basic relationship between X and Y, they were limited by small sample sizes and cross-sectional designs. This study addresses these limitations by..."
-->
### Literature Context
{{ literature_context or "How this work builds on and relates to existing research" }}

## Methodology

<!-- RESEARCH DESIGN: Describe the overall methodological approach -->
<!--
INSTRUCTIONS: Extract and describe the overall research design and approach.
- Identify study type (experimental, observational, qualitative, etc.)
- Describe the overall methodological approach
- Include justification for chosen methods if provided
- Note any novel methodological contributions
EXAMPLE: "The authors employed a mixed-methods approach combining a randomized controlled trial (quantitative phase) with semi-structured interviews (qualitative phase) to provide comprehensive understanding of both effectiveness and user experience."
-->
### Research Design
{{ research_design or "Overall study design and methodological approach" }}

<!-- METHODS AND TECHNIQUES: List specific methods used -->
<!--
INSTRUCTIONS: Extract specific methods, techniques, and procedures used.
- Include data collection methods
- List analytical techniques and statistical methods
- Describe any specialized equipment or software
- Note validation procedures and quality controls
EXAMPLES:
- "Randomized controlled trial with 2x2 factorial design"
- "Semi-structured interviews analyzed using thematic analysis"
- "Machine learning models validated using 10-fold cross-validation"
-->
### Methods and Techniques
{%- if methods %}
{%- for method in methods %}
- {{ method }}
{%- endfor %}
{%- else %}
- Primary experimental or analytical methods
- Data collection procedures
- Analysis techniques employed
{%- endif %}

<!-- STUDY PARAMETERS: Describe key variables and conditions -->
<!--
INSTRUCTIONS: Extract information about study parameters, variables, and conditions.
- Include sample characteristics (size, demographics, selection criteria)
- Describe independent and dependent variables
- Note experimental conditions or treatment groups
- Include measurement instruments and their properties
EXAMPLE: "Sample: 245 university students (62% female, mean age 20.4 years). Independent variable: Training condition (traditional vs. AI-enhanced). Dependent variables: Performance measured using validated XYZ scale (Cronbach's α = 0.89)."
-->
### Study Parameters
{{ study_parameters or "Key variables, conditions, and measurement parameters" }}

## Results and Findings

<!-- PRIMARY RESULTS: Extract main findings and quantitative results -->
<!--
INSTRUCTIONS: Extract the most important findings and results.
- Include key quantitative results with statistical details
- Report effect sizes and confidence intervals when available
- Describe primary outcomes for each research question
- Be specific with numbers and statistical significance
EXAMPLE: "The intervention group showed significantly higher performance (M = 85.4, SD = 12.3) compared to control group (M = 76.2, SD = 14.1), t(243) = 4.32, p < .001, Cohen's d = 0.68."
-->
### Primary Results
{{ primary_results or "Main findings and quantitative results" }}

<!-- SUPPORTING EVIDENCE: Include secondary findings and validation -->
<!--
INSTRUCTIONS: Extract supporting evidence and secondary findings.
- Include additional analyses that support main conclusions
- Describe validation procedures and their results
- Report subgroup analyses or sensitivity analyses
- Include qualitative findings if applicable
EXAMPLES:
- "Sensitivity analysis excluding outliers confirmed the main results"
- "Subgroup analysis revealed stronger effects for experienced users"
- "Qualitative interviews supported quantitative findings, with themes of..."
-->
### Supporting Evidence
{%- if supporting_evidence %}
{%- for evidence in supporting_evidence %}
- {{ evidence }}
{%- endfor %}
{%- else %}
- Secondary findings that support main conclusions
- Statistical validation and significance
- Reproducibility and consistency measures
{%- endif %}

<!-- DATA ANALYSIS: Summarize key insights from analysis -->
<!--
INSTRUCTIONS: Extract key insights from data analysis and interpretation.
- Describe patterns or trends identified in the data
- Include unexpected findings or surprises
- Explain how findings relate to research questions
- Note any post-hoc analyses or exploratory findings
EXAMPLE: "Analysis revealed an unexpected interaction effect between user experience and system complexity, suggesting that benefits are greatest for intermediate-level users."
-->
### Data Analysis
{{ data_analysis or "Key insights from data analysis and interpretation" }}

## Discussion and Implications

<!-- THEORETICAL IMPLICATIONS: How findings advance theory -->
<!--
INSTRUCTIONS: Extract theoretical implications and contributions to knowledge.
- Explain how findings support or challenge existing theories
- Describe theoretical innovations or extensions
- Connect findings to broader theoretical frameworks
- Include implications for conceptual understanding
EXAMPLE: "These findings extend Social Cognitive Theory by demonstrating that self-efficacy mediates the relationship between training and performance in AI-assisted tasks, suggesting a need to incorporate technology-specific efficacy constructs."
-->
### Theoretical Implications
{{ theoretical_implications or "How findings advance theoretical understanding" }}

<!-- PRACTICAL APPLICATIONS: Real-world applications and implementations -->
<!--
INSTRUCTIONS: Extract practical applications and real-world implications.
- Identify direct applications for practitioners
- Include implementation recommendations
- Describe relevance for policy or decision-making
- Note any clinical, educational, or industrial applications
EXAMPLES:
- "Results suggest that organizations should provide intermediate-level training before implementing AI tools"
- "Findings inform the design of user interfaces for AI-assisted decision-making systems"
- "Clinical implications include modified treatment protocols for patients with condition X"
-->
### Practical Applications
{%- if practical_applications %}
{%- for application in practical_applications %}
- {{ application }}
{%- endfor %}
{%- else %}
- Direct practical implementations
- Industrial or clinical applications
- Policy or decision-making implications
{%- endif %}

<!-- METHODOLOGICAL CONTRIBUTIONS: Advances in research methods -->
<!--
INSTRUCTIONS: Extract methodological contributions and innovations.
- Describe novel methods or techniques introduced
- Include improvements to existing methodologies
- Note validation of new measurement instruments
- Explain methodological insights for future research
EXAMPLE: "The study introduces a novel mixed-methods approach for evaluating AI systems that combines objective performance metrics with subjective user experience measures, providing a template for future evaluation studies."
-->
### Methodological Contributions
{{ methodological_contributions or "Advances in research methods or analytical approaches" }}

## Critical Assessment

<!-- STRENGTHS: Identify study strengths and positive aspects -->
<!--
INSTRUCTIONS: Extract and evaluate the study's strengths.
- Include methodological rigor and innovations
- Note comprehensive analysis and validation
- Highlight clear practical relevance
- Consider sample quality, design features, and analytical approach
EXAMPLES:
- "Large, representative sample with high response rate (87%)"
- "Rigorous experimental design with appropriate controls"
- "Novel analytical approach that addresses limitations of previous methods"
- "Clear theoretical foundation and well-articulated hypotheses"
-->
### Strengths
{%- if strengths %}
{%- for strength in strengths %}
- {{ strength }}
{%- endfor %}
{%- else %}
- Methodological rigor and innovation
- Comprehensive analysis and validation
- Clear practical relevance
{%- endif %}

<!-- LIMITATIONS: Identify acknowledged limitations and potential weaknesses -->
<!--
INSTRUCTIONS: Extract limitations acknowledged by authors and identify potential weaknesses.
- Include scope restrictions and boundary conditions
- Note potential sources of bias or confounding
- Identify generalizability limitations
- Consider measurement limitations or methodological constraints
EXAMPLES:
- "Cross-sectional design limits causal inferences"
- "Sample limited to university students, reducing generalizability"
- "Self-report measures may be subject to social desirability bias"
- "Short follow-up period limits understanding of long-term effects"
-->
### Limitations
{%- if limitations %}
{%- for limitation in limitations %}
- {{ limitation }}
{%- endfor %}
{%- else %}
- Acknowledged study limitations
- Scope restrictions and boundary conditions
- Potential sources of bias or error
{%- endif %}

<!-- FUTURE RESEARCH NEEDS: Identify gaps and future directions -->
<!--
INSTRUCTIONS: Extract suggested future research directions and identify remaining gaps.
- Include authors' explicit suggestions for future work
- Identify logical next steps based on findings
- Note methodological improvements for future studies
- Consider broader research questions that emerge
EXAMPLE: "Future research should examine long-term effects using longitudinal designs, test generalizability across different populations, and investigate the underlying neural mechanisms using neuroimaging techniques."
-->
### Future Research Needs
{{ future_research or "Identified gaps and suggested future research directions" }}

## Research Impact and Connections

<!-- FIELD ADVANCEMENT: How this work advances the broader field -->
<!--
INSTRUCTIONS: Extract how this work advances the broader research field.
- Consider contributions to cumulative knowledge
- Identify how findings fill gaps in understanding
- Note influence on research directions
- Include potential paradigm shifts or new perspectives
EXAMPLE: "This work significantly advances the field by providing the first empirical evidence for theory X in context Y, opening new avenues for research on Z and challenging assumptions about W."
-->
### Field Advancement
{{ field_advancement or "How this work advances the broader research field" }}

<!-- CROSS-DISCIPLINARY RELEVANCE: Relevance to other fields -->
<!--
INSTRUCTIONS: Extract relevance to other research areas or disciplines.
- Identify applications in related fields
- Note interdisciplinary connections
- Include potential for cross-fertilization of ideas
- Consider broader scientific or societal implications
EXAMPLE: "While focused on psychology, findings have important implications for computer science (AI design), education (learning technologies), and organizational behavior (technology adoption)."
-->
### Cross-Disciplinary Relevance
{{ cross_disciplinary or "Relevance to other research areas or disciplines" }}

<!-- FOLLOW-UP QUESTIONS: Generate research questions for future investigation -->
<!--
INSTRUCTIONS: Generate thoughtful follow-up questions based on the paper's findings.
- Create questions that extend the current work
- Include methodological and theoretical questions
- Consider practical implementation questions
- Think about broader implications and connections
EXAMPLES:
- "How would these findings change with a different population?"
- "What mechanisms explain the observed effects?"
- "How can these methods be scaled for real-world implementation?"
-->
### Follow-up Questions
{%- if follow_up_questions %}
{%- for question in follow_up_questions %}
- {{ question }}
{%- endfor %}
{%- else %}
- What additional studies would strengthen these findings?
- How can these methods be extended or improved?
- What are the broader implications for the field?
{%- endif %}

## Personal Research Notes

<!-- RELEVANCE TO CURRENT WORK: Connect to your research interests -->
<!--
INSTRUCTIONS: Reflect on how this paper relates to your current research.
- Consider methodological applications
- Identify theoretical connections
- Note potential collaborations or extensions
- Think about how findings inform your work
EXAMPLE: "This paper's approach to measuring user experience with AI systems directly relates to my current project on human-AI collaboration, particularly the validated scales for trust and self-efficacy."
-->
### Relevance to Current Work
{{ personal_relevance or "How this paper relates to your current research interests" }}

<!-- METHODOLOGICAL INSIGHTS: Extract applicable techniques -->
<!--
INSTRUCTIONS: Identify methodological insights applicable to your work.
- Note innovative techniques worth adopting
- Consider analytical approaches for your context
- Identify measurement instruments to explore
- Think about design features to incorporate
EXAMPLE: "The mixed-methods approach combining behavioral measures with think-aloud protocols provides a model for evaluating complex AI interfaces in my domain."
-->
### Methodological Insights
{{ methodological_insights or "Techniques or approaches applicable to your work" }}

<!-- KEY TAKEAWAYS: Summarize most important insights -->
<!--
INSTRUCTIONS: Synthesize the most important insights and lessons.
- Prioritize insights with broad applicability
- Include both theoretical and practical takeaways
- Consider surprising or counterintuitive findings
- Think about paradigm-shifting implications
EXAMPLE: "Key insight: AI effectiveness depends not just on technical capabilities but on user self-efficacy and training quality. This shifts focus from purely technical optimization to human-centered design considerations."
-->
### Key Takeaways
{{ key_takeaways or "Most important insights and lessons learned" }}

<!-- ACTION ITEMS: Specific next steps based on this paper -->
<!--
INSTRUCTIONS: Generate specific, actionable next steps based on this paper.
- Include methods to investigate further
- List concepts to incorporate into current research
- Identify follow-up papers to read
- Consider practical applications to pursue
EXAMPLES:
- "Investigate the XYZ scale for measuring user trust in AI systems"
- "Read Smith et al. (2021) on related theoretical framework"
- "Consider adapting the ABC methodology for my current experiment"
- "Explore collaboration with researchers working on similar problems"
-->
### Action Items
{%- if action_items %}
{%- for item in action_items %}
- {{ item }}
{%- endfor %}
{%- else %}
- Specific methods to investigate further
- Concepts to incorporate into current research
- Follow-up papers to read
{%- endif %}

---
*Generated on {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }} using ScholarSquill Kiro*