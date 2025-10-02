# Batch Citation Network Analysis

**Analysis Date**: {{ batch_info.analysis_timestamp }}  
**Input Directory**: {{ batch_info.input_directory }}  
**Papers Analyzed**: {{ batch_info.processed_papers }}/{{ batch_info.total_papers }}  

---

## Cross-Reference Analysis Summary

**Total Papers**: {{ batch_info.total_papers }}  
**Successfully Processed**: {{ batch_info.processed_papers }}  
**Failed Processing**: {{ batch_info.failed_papers }}  
**Total References Extracted**: {{ batch_info.total_references }}  
**Total Citation Contexts**: {{ batch_info.total_citation_contexts }}  

---

## Papers in Collection

{% for paper in papers %}
{{ loop.index }}. **{{ paper.title }}**  
   *Authors*: {{ paper.authors | join(', ') }}  
   *Year*: {{ paper.year }}  
   *Citekey*: `{{ paper.citekey }}`

{% endfor %}

---

## Cross-Reference Relationships

{% if cross_reference_analysis.direct_cross_references %}
### Papers Citing Each Other

{% for cross_ref in cross_reference_analysis.direct_cross_references %}
**{{ cross_ref.paper1.title | truncate(50) }}** ↔ **{{ cross_ref.paper2.title | truncate(50) }}**  
- {{ cross_ref.paper1.citekey }} cites {{ cross_ref.paper2.citekey }}: {{ "✓" if cross_ref.paper1_cites_paper2 else "✗" }}  
- {{ cross_ref.paper2.citekey }} cites {{ cross_ref.paper1.citekey }}: {{ "✓" if cross_ref.paper2_cites_paper1 else "✗" }}  
- Bidirectional citation: {{ "Yes" if cross_ref.bidirectional else "No" }}

{% endfor %}
{% else %}
*No direct cross-references found between papers in this collection.*
{% endif %}

---

## Top 5 Most Cited Papers

{% if top_cited_papers %}
### Papers Most Frequently Referenced in Collection

{% for paper in top_cited_papers[:5] %}
**{{ loop.index }}. {{ paper.title }}** ({{ paper.year }})  
*Authors*: {{ paper.authors | join(', ') }}  
*Cited {{ paper.citation_count }} times across selected papers*  
*Citing papers*: {% for citekey in paper.cited_by %}{{ citekey }}{% if not loop.last %}, {% endif %}{% endfor %}

{% endfor %}
{% else %}
*No papers in the collection are cited multiple times by other papers in the collection.*
{% endif %}

---

## Common Sources Analysis

{% if common_sources %}
### Most Frequently Cited Sources

{% for source in common_sources[:10] %}
**{{ loop.index }}. {{ source.author }}** ({{ source.year }})  
*Cited by*: {{ source.citation_count }} papers  
*Papers*: {% for citation in source.cited_by %}{{ citation.paper }}{% if not loop.last %}, {% endif %}{% endfor %}  
{% if source.title %}*Title*: {{ source.title }}{% endif %}

{% endfor %}

### Citation Frequency Distribution

| Citation Count | Number of Sources | Papers |
|---------------|------------------|---------|
{% for count in range(10, 0, -1) %}
{% set sources_with_count = common_sources | selectattr('citation_count', 'equalto', count) | list %}
{% if sources_with_count %}
| {{ count }} | {{ sources_with_count | length }} | {% for source in sources_with_count[:3] %}{{ source.author }} {{ source.year }}{% if not loop.last %}, {% endif %}{% endfor %}{% if sources_with_count | length > 3 %}...{% endif %} |
{% endif %}
{% endfor %}

{% else %}
*No common sources found across multiple papers.*
{% endif %}

---

## Intellectual Lineage Analysis

{% if intellectual_lineage.foundational_works %}
### Foundational Works in Collection

{% for work in intellectual_lineage.foundational_works %}
**{{ work.paper.title }}** ({{ work.paper.year }})  
*Authors*: {{ work.paper.authors | join(', ') }}  
*Cited by {{ work.cited_by_count }} newer papers in collection*  
*Citing papers*: {% for citekey in work.cited_by %}{{ citekey }}{% if not loop.last %}, {% endif %}{% endfor %}

{% endfor %}
{% else %}
*No clear foundational works identified in this collection based on chronological citation patterns.*
{% endif %}

---

## Interactive Network Visualization

### PublicationNet-Style Citation Network

**[Open Interactive Network Visualization →](./../{{ batch_info.input_directory | basename }}_network.html)**

*Click the link above to open an interactive network visualization showing:*
- **Node size** = citation frequency in collection
- **Node color** = publication year (color scale)
- **Edges** = direct citation relationships
- **Interactive features** = hover for details, zoom, pan, drag

### Network Statistics

- **Total Papers**: {{ papers | length }}
- **Citation Relationships**: {{ reference_network.edges | length }}
- **Network Density**: {% if reference_network.nodes | length > 1 %}{{ "%.3f" | format((reference_network.edges | length) / ((reference_network.nodes | length) * (reference_network.nodes | length - 1))) }}{% else %}0.000{% endif %}
- **Connected Components**: Analysis shows {{ "interconnected" if reference_network.edges | length > 0 else "isolated" }} citation patterns

---

## Research Landscape Insights

### Key Findings

1. **Collection Coherence**: {% if cross_reference_analysis.direct_cross_references %}This collection shows {{ cross_reference_analysis.direct_cross_references | length }} direct cross-reference relationships, indicating a coherent research domain.{% else %}Limited direct cross-referencing suggests this collection spans multiple sub-domains or research areas.{% endif %}

2. **Common Foundation**: {% if common_sources %}{{ common_sources | length }} sources are cited by multiple papers, with the most cited being "{{ common_sources[0].author }} ({{ common_sources[0].year }})" referenced by {{ common_sources[0].citation_count }} papers.{% else %}No common foundational sources identified across papers.{% endif %}

3. **Research Scope**: Analysis covers {{ batch_info.total_citation_contexts }} citation contexts across {{ batch_info.processed_papers }} papers, providing comprehensive insight into the research domain.

### Research Domain Characteristics

- **Temporal Spread**: Papers span from {{ papers | map(attribute='year') | min }} to {{ papers | map(attribute='year') | max }}
- **Citation Density**: {{ "%.1f" | format(batch_info.total_citation_contexts / batch_info.processed_papers) }} citations per paper average
- **Reference Diversity**: {{ "%.1f" | format(batch_info.total_references / batch_info.processed_papers) }} unique references per paper average

---

## Analysis Methodology

This batch citation analysis was performed using:
- **Citation Context Extraction**: Advanced pattern matching for multiple citation formats
- **Cross-Reference Detection**: Author-year matching between papers in collection  
- **Network Analysis**: Graph-based representation of citation relationships
- **Lineage Tracing**: Chronological analysis of foundational vs. recent works

---

## Analysis Metadata

**Generated**: {{ batch_info.analysis_timestamp }}  
**Analysis Type**: Batch Citation Network Analysis  
**Template**: citemap_batch.md  
**Processor**: CitemapProcessor v1.0  
**Input Directory**: {{ batch_info.input_directory }}  
**Processing Time**: {{ batch_info.analysis_timestamp }}  

---

*This comprehensive citation network analysis reveals the intellectual connections, common foundations, and research landscape patterns across {{ batch_info.processed_papers }} academic papers.*