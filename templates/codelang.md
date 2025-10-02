# Code Language Analysis: {{ title }}

> [!Metadata]
> **FirstAuthor**:: {{ first_author }}
{%- for author in authors %}
> **Author**:: {{ author }}
{%- endfor %}
> **Title**:: {{ title }}
> **Year**:: {{ year or "Unknown" }}
> **Citekey**:: {{ citekey }}
> **Field**:: {{ detected_field or "Auto-detected" }}
> **Analysis Focus**:: {{ analysis_focus }}
{%- if journal %}
> **Journal**:: *{{ journal }}*
{%- endif %}
{%- if doi %}
> **DOI**:: {{ doi }}
{%- endif %}

## Discourse Architecture

### Argument Structure
{{ argument_structure or "How the author constructs their overall argument and logical flow." }}

### Topic Introduction & Highlighting
{%- if topic_highlighting_expressions %}
{%- for expression in topic_highlighting_expressions %}
- **"{{ expression.text }}"** *({{ expression.function }})*
{%- endfor %}
{%- else %}
{{ topic_highlighting or "Expressions and patterns used to introduce and highlight the main topic." }}
{%- endif %}

### Logical Flow & Transitions
{%- if transition_patterns %}
{%- for pattern in transition_patterns %}
- **{{ pattern.type }}**: "{{ pattern.expression }}" → {{ pattern.function }}
{%- endfor %}
{%- else %}
{{ logical_transitions or "Patterns for connecting ideas, building arguments, and guiding reader through the logic." }}
{%- endif %}

## Field-Specific Language

### Domain Terminology
{%- if domain_terms %}
{%- for term in domain_terms %}
- **{{ term.expression }}**: {{ term.context }} *({{ term.frequency }} occurrences)*
{%- endfor %}
{%- else %}
{{ domain_terminology or "Field-specific vocabulary, technical terms, and specialized language conventions." }}
{%- endif %}

### Mathematical & Technical Expressions
{%- if mathematical_expressions %}
{%- for expr in mathematical_expressions %}
- **{{ expr.type }}**: `{{ expr.notation }}` - {{ expr.context }}
{%- endfor %}
{%- else %}
{{ mathematical_language or "Mathematical notation, equations, and technical expressions used." }}
{%- endif %}

### Methodological Language
{{ methodological_expressions or "Patterns for describing methods, procedures, and experimental approaches." }}

## Rhetorical Strategy

### Evidence Presentation
{%- if evidence_patterns %}
{%- for pattern in evidence_patterns %}
- **{{ pattern.signal }}**: "{{ pattern.expression }}" 
  - Context: {{ pattern.context }}
  - Function: {{ pattern.rhetorical_function }}
{%- endfor %}
{%- else %}
{{ evidence_presentation or "Patterns for presenting evidence, supporting claims, and building credibility." }}
{%- endif %}

### Authority & Positioning
{{ authority_expressions or "Expressions used to establish authority, position the work, and claim expertise." }}

### Gap Identification & Contribution Claims
{%- if contribution_patterns %}
{%- for pattern in contribution_patterns %}
- **Gap**: "{{ pattern.gap_expression }}"
- **Contribution**: "{{ pattern.contribution_claim }}"
{%- endfor %}
{%- else %}
{{ contribution_claims or "Patterns for identifying research gaps and claiming novel contributions." }}
{%- endif %}

## Section-Specific Language

### Introduction
{{ introduction_patterns or "Expressions and structures specific to the introduction section." }}

### Methods  
{{ methods_patterns or "Language patterns used in methodology sections." }}

### Results
{{ results_patterns or "Expressions for presenting findings and results." }}

### Discussion
{{ discussion_patterns or "Patterns for interpreting results and discussing implications." }}

## Linguistic Functions

{%- if discovered_functions %}
{%- for function_name, expressions in discovered_functions.items() %}
### {{ function_name }}
{%- for expr in expressions %}
- "{{ expr }}"
{%- endfor %}

{%- endfor %}
{%- else %}
{{ linguistic_functions or "Categories of how expressions function in this academic text." }}
{%- endif %}

## Summary

### Primary Discourse Strategy
{{ primary_strategy or "Overall approach this author uses to structure their academic argument." }}

### Field Convention Adherence
{{ field_conventions or "How well this paper follows established conventions of its academic field." }}

### Unique Language Innovations
{{ language_innovations or "Novel or distinctive ways this author uses language compared to field norms." }}

### Expression Frequency
{%- if expression_frequency %}
{%- for category, count in expression_frequency.items() %}
- **{{ category }}**: {{ count }} instances
{%- endfor %}
{%- else %}
{{ frequency_analysis or "Analysis of which types of expressions are most frequently used." }}
{%- endif %}

## Insights & Applications

### Writing Patterns
{{ writing_insights or "What can be learned from this author's approach to academic writing." }}

### Field Conventions
{{ field_insights or "Insights about how this academic field structures arguments and presents knowledge." }}

### Reusable Patterns
{%- if reusable_patterns %}
{%- for pattern in reusable_patterns %}
- **{{ pattern.context }}**: "{{ pattern.template }}"
{%- endfor %}
{%- else %}
{{ reusable_patterns or "Expression patterns that could be adapted for similar academic writing." }}
{%- endif %}

---
*Generated on {{ generated_at.strftime('%Y-%m-%d %H:%M:%S') }} using ScholarsQuill*