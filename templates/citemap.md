# Citation Context Map: {{ paper.title }}

**Authors**: {{ paper.authors | join(', ') }}  
**Year**: {{ paper.year }}  
**DOI**: {% if paper.doi %}{{ paper.doi }}{% else %}N/A{% endif %}  
**Citekey**: `{{ paper.citekey }}`  

---

## Citation Analysis Summary

**Total Citations Found**: {{ citation_analysis.total_citations }}  
**Unique References**: {{ citation_analysis.unique_references }}  
**Network Complexity**: {{ citation_analysis.network.nodes | length }} nodes, {{ citation_analysis.network.edges | length }} edges  

---

## Citation Context Analysis

### Citation Purposes Distribution

{% for purpose, contexts in citation_analysis.citation_contexts | groupby('purpose') %}
#### {{ purpose | replace('_', ' ') | title }} ({{ contexts | list | length }} citations)

{% for context in contexts %}
- **Citation**: {{ context.citation }}
- **Context**: {{ context.surrounding_context }}
- **Section**: {{ context.section }}
- **Purpose**: {{ context.purpose | replace('_', ' ') | title }}

{% endfor %}
{% endfor %}

---

## Reference Network

### All References Found

{% for ref in citation_analysis.references %}
{{ loop.index }}. **{{ ref.parsed_authors }}** ({{ ref.parsed_year }}){% if ref.parsed_title %} - {{ ref.parsed_title }}{% endif %}
   
   *Full Reference*: {{ ref.text }}

{% endfor %}

---

## Reference Relationships Network

### Network Structure

```mermaid
graph LR
    Current["{{ paper.title | truncate(30) }}"] 
    
{% for node in citation_analysis.network.nodes %}
    {% if node.type == "reference" %}
    {{ node.id }}["{{ node.label }}"]
    {% endif %}
{% endfor %}

{% for edge in citation_analysis.network.edges %}
    {% if edge.source == "current_paper" %}
    Current --> {{ edge.target }}
    {% else %}
    {{ edge.source }} --> {{ edge.target }}
    {% endif %}
{% endfor %}
```

### Citation Network Analysis

{% if citation_analysis.network.clusters %}
#### Citation Purpose Clusters

{% for purpose, refs in citation_analysis.network.clusters.items() %}
**{{ purpose | replace('_', ' ') | title }}**:
{% for ref_id in refs %}
- {{ ref_id }}
{% endfor %}

{% endfor %}
{% endif %}

---

## Citation Pattern Analysis

### Section-wise Citation Distribution

| Section | Citation Count | Percentage |
|---------|---------------|------------|
{% for context in citation_analysis.citation_contexts %}
{% set section_counts = citation_analysis.citation_contexts | groupby('section') | map(attribute='1') | map('list') | map('length') %}
{% endfor %}

### Purpose-wise Citation Usage

| Purpose | Count | Description |
|---------|-------|-------------|
| Supporting Evidence | {{ citation_analysis.citation_contexts | selectattr('purpose', 'equalto', 'supporting_evidence') | list | length }} | Citations used to support claims |
| Contrasting View | {{ citation_analysis.citation_contexts | selectattr('purpose', 'equalto', 'contrasting_view') | list | length }} | Citations presenting opposing viewpoints |
| Methodology Source | {{ citation_analysis.citation_contexts | selectattr('purpose', 'equalto', 'methodology_source') | list | length }} | Citations for methods and techniques |
| Background Context | {{ citation_analysis.citation_contexts | selectattr('purpose', 'equalto', 'background_context') | list | length }} | Citations for background information |
| Comparison | {{ citation_analysis.citation_contexts | selectattr('purpose', 'equalto', 'comparison') | list | length }} | Citations for comparative analysis |
| General Reference | {{ citation_analysis.citation_contexts | selectattr('purpose', 'equalto', 'general_reference') | list | length }} | General citations and references |

---

## Intellectual Connections

### Key Citation Contexts

#### Most Significant References

{% for context in citation_analysis.citation_contexts[:5] %}
**{{ loop.index }}. {{ context.citation }}**  
*Section*: {{ context.section | title }}  
*Purpose*: {{ context.purpose | replace('_', ' ') | title }}  
*Context*: {{ context.surrounding_context }}

{% endfor %}

### Citation Network Insights

This paper creates intellectual connections through {{ citation_analysis.total_citations }} citations across {{ citation_analysis.unique_references }} unique sources. The citation network reveals:

- **Primary citation purpose**: {% if citation_analysis.citation_contexts %}{{ citation_analysis.citation_contexts | groupby('purpose') | map(attribute='0') | first | replace('_', ' ') | title }}{% endif %}
- **Most cited section**: {% if citation_analysis.citation_contexts %}{{ citation_analysis.citation_contexts | groupby('section') | map(attribute='0') | first | title }}{% endif %}
- **Citation density**: {{ "%.1f" | format((citation_analysis.total_citations / citation_analysis.unique_references) if citation_analysis.unique_references > 0 else 0) }} citations per unique source

---

## Analysis Metadata

**Generated**: {{ timestamp }}  
**Analysis Type**: Citation Context Mapping  
**Template**: citemap.md  
**Processor**: CitemapProcessor v1.0  

---

*This citation context map provides a comprehensive analysis of how this paper connects to and builds upon existing literature through its citation practices and reference relationships.*