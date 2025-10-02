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

## Core Idea or Theoretical Claim

**Main Theoretical Proposition:** {{ theoretical_proposition or "Primary theoretical claim or model presented" }}

**Problem Addressed:** {{ problem_addressed or "What phenomenon or problem does this theory aim to explain?" }}

**Key Idea Summary:** {{ key_idea or "Concise summary of the theory's central concept" }}

## Key Equations and Assumptions

### Primary Equations
{%- if equations %}
{%- for equation in equations %}

**{{ equation.name or "Equation" }}:**
```
{{ equation.formula or equation }}
```
{%- if equation.symbols %}
**Symbols:** {{ equation.symbols }}
{%- endif %}

{%- endfor %}
{%- else %}

```
[Key mathematical equations will be listed here]
```
**Symbols:** [Define all symbols clearly]

{%- endif %}

### Underlying Assumptions
{%- if assumptions %}
{%- for assumption in assumptions %}
- {{ assumption }}
{%- endfor %}
{%- else %}
- Fundamental assumptions (e.g., dilute limit, linear response, equilibrium)
- Boundary conditions and domain of validity
- Approximations employed
{%- endif %}

### Domain of Validity
{{ validity_domain or "Specify conditions where the theory applies and known limitations" }}

## Derivation or Logical Structure

### Theoretical Foundation
{{ theoretical_foundation or "Physical laws, mathematical principles, or conceptual framework used" }}

### Key Derivation Steps
{%- if derivation_steps %}
{%- for step in derivation_steps %}
{{ loop.index }}. {{ step }}
{%- endfor %}
{%- else %}
1. Starting principles and initial conditions
2. Mathematical transformations and approximations
3. Key intermediate results
4. Final theoretical expressions
{%- endif %}

### Mathematical Tools Employed
{{ mathematical_tools or "Specific mathematical methods, approximations, or computational approaches" }}

## Applications or Case Studies

### Physical/Chemical Systems
{%- if applications %}
{%- for application in applications %}
- **{{ application.system or "System" }}:** {{ application.description or application }}
{%- endfor %}
{%- else %}
- Specific systems where theory has been applied
- Relevant experimental validations
- Computational implementations
{%- endif %}

### Key Findings from Applications
{{ application_findings or "Important results from theoretical applications" }}

### Simulation and Modeling Results
{{ simulation_results or "Computational validation and modeling outcomes" }}

## Theoretical Context and Connections

### Relationship to Previous Work
{{ previous_work or "How this theory relates to, extends, or replaces earlier models" }}

### Generalizations and Extensions
{{ generalizations or "What does this theory generalize, simplify, or extend?" }}

### Alternative Approaches
{{ alternatives or "Known competing theories or alternative formulations" }}

### Historical Development
{{ historical_context or "Evolution of ideas leading to this theoretical framework" }}

## Limitations and Criticisms

### Stated Limitations
{%- if limitations %}
{%- for limitation in limitations %}
- {{ limitation }}
{%- endfor %}
{%- else %}
- Acknowledged theoretical limitations
- Conditions where theory breaks down
- Approximation validity ranges
{%- endif %}

### Known Failure Modes
{{ failure_modes or "Systems or conditions where the theory fails (e.g., non-ideal systems, extreme conditions)" }}

### Literature Criticisms
{{ criticisms or "Critiques or comparative evaluations found in literature" }}

## Personal Commentary and Research Relevance

### Theoretical Assessment
{{ personal_assessment or "Your interpretation and evaluation of the theory's strengths and weaknesses" }}

### Research Application Potential
{{ research_relevance or "How this theory relates to your research questions or modeling efforts" }}

### Implementation Plans
{%- if implementation_plans %}
{%- for plan in implementation_plans %}
- {{ plan }}
{%- endfor %}
{%- else %}
- Specific aspects to apply or cite
- Elements requiring further investigation
- Potential modifications for your work
{%- endif %}

### Unclear Elements
{{ unclear_elements or "Theoretical aspects requiring clarification or additional study" }}

## Supplementary Notes and Resources

### Important Figures and Diagrams
{{ figures or "Key visual representations, phase diagrams, or theoretical illustrations" }}

### Computational Resources
{{ computational_resources or "Available code, datasets, or simulation parameters" }}

### Related Materials
{{ related_materials or "Supporting derivations, supplementary information, or connected papers" }}

---
*Generated on {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }} using ScholarsQuill*