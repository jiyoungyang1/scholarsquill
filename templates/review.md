# {{ title }}

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

{%- if zotero_key %}
> **Zotero**:: [Open in Zotero]({{ zotero_url }})
> **Zotero Key**:: {{ zotero_key }}
{%- endif %}
{%- if zotero_tags %}
> **Tags**:: {% for tag in zotero_tags %}#{{ tag|replace('-', '_') }} {% endfor %}
{%- endif %}
{%- if zotero_collections %}
> **Collections**:: {{ zotero_collections|join(', ') }}
{%- endif %}
{%- if date_added %}
> **Date Added**:: {{ date_added }}
{%- endif %}
{%- if date_modified %}
> **Date Modified**:: {{ date_modified }}
{%- endif %}
> **PDF**:: [[{{ source_path }}]]

## Review Overview

### Scope and Objectives
{{ scope or "Review scope, research questions, and objectives addressed" }}

### Search Strategy
{{ search_strategy or "Databases searched, keywords used, and search methodology" }}

### Inclusion/Exclusion Criteria
{%- if inclusion_criteria %}
{%- for criterion in inclusion_criteria %}
- {{ criterion }}
{%- endfor %}
{%- else %}
- Study types included
- Population characteristics
- Outcome measures
- Time period covered
{%- endif %}

### Literature Coverage
{{ coverage or "Number of studies reviewed, publication years, and geographic distribution" }}

## Thematic Analysis

### Major Research Themes
{%- if key_themes %}
{%- for theme in key_themes %}

#### {{ theme.title or "Theme" }}
**Description:** {{ theme.description or "Theme description" }}
**Key Studies:** {{ theme.studies or "Representative studies in this theme" }}
**Findings:** {{ theme.findings or "Main findings within this theme" }}

{%- endfor %}
{%- else %}

#### Foundational Theoretical Work
**Description:** Core theoretical frameworks and models
**Key Studies:** Seminal papers establishing theoretical foundations
**Findings:** Fundamental principles and mathematical formulations

#### Methodological Developments
**Description:** Advances in experimental and computational methods
**Key Studies:** Papers introducing novel methodological approaches
**Findings:** Technical innovations and validation studies

#### Applied Research and Applications
**Description:** Practical implementations and real-world applications
**Key Studies:** Case studies and application-focused research
**Findings:** Performance evaluations and practical outcomes

{%- endif %}

## Literature Synthesis and Network Analysis

### Theoretical Framework Evolution
{{ theoretical_evolution or "How theoretical understanding has developed over time" }}

### Methodological Progression
{{ methodological_progression or "Evolution of research methods and experimental approaches" }}

### Key Connections and Relationships
{%- if connections %}
{%- for connection in connections %}
- {{ connection }}
{%- endfor %}
{%- else %}
- Cross-citations and theoretical building blocks
- Methodological dependencies and improvements
- Conflicting findings and resolution attempts
{%- endif %}

### Hub References and Influential Work
{%- if hub_references %}
{%- for hub in hub_references %}
- **{{ hub.reference }}:** {{ hub.influence or "Description of influence and connections" }}
{%- endfor %}
{%- else %}
- Most cited foundational papers
- Methodological breakthrough studies
- Recent high-impact contributions
{%- endif %}

## Critical Analysis

### Research Gaps and Limitations
{%- if research_gaps %}
{%- for gap in research_gaps %}
- {{ gap }}
{%- endfor %}
{%- else %}
- Understudied populations or systems
- Methodological limitations across studies
- Theoretical gaps requiring attention
{%- endif %}

### Methodological Issues
{{ methodological_issues or "Common methodological problems or limitations identified" }}

### Conflicting Findings
{{ conflicts or "Areas where studies report contradictory results and potential explanations" }}

### Quality Assessment
{{ quality_assessment or "Overall quality of evidence and reliability of conclusions" }}

## Future Research Directions

### Priority Research Areas
{%- if future_directions %}
{%- for direction in future_directions %}
- {{ direction }}
{%- endfor %}
{%- else %}
- High-priority research questions
- Methodological improvements needed
- Emerging application areas
{%- endif %}

### Methodological Recommendations
{{ methodological_recommendations or "Suggested improvements to research methods and study designs" }}

### Theoretical Development Needs
{{ theoretical_needs or "Areas where theoretical frameworks require extension or refinement" }}

## Conclusions and Implications

### Key Findings Summary
{{ key_findings or "Primary conclusions from the literature synthesis" }}

### Theoretical Implications
{{ theoretical_implications or "Impact on theoretical understanding and conceptual frameworks" }}

### Practical Implications
{{ practical_implications or "Applications for practitioners, policymakers, or industry" }}

### Research Community Impact
{{ community_impact or "How this review advances the field and guides future research" }}

## Literature Network Visualization

{%- if network_diagram %}
```mermaid
%%{init: {'flowchart': {'htmlLabels': true, 'useMaxWidth': true, 'curve': 'basis'}}}%%
%%{wrap}%%
{{ network_diagram }}
```
{%- else %}
```mermaid
%%{init: {'flowchart': {'htmlLabels': true, 'useMaxWidth': true, 'curve': 'basis'}}}%%
%%{wrap}%%
graph LR
    A[Foundational Theory] --> B[Methodological Development]
    B --> C[Applied Research]
    A --> D[Theoretical Extensions]
    C --> E[Practical Applications]
    D --> F[Future Directions]
```
{%- endif %}

**Network Analysis:** {{ network_analysis or "Description of literature connections, clusters, and evolution patterns" }}

---
*Generated on {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }} using ScholarsQuill*