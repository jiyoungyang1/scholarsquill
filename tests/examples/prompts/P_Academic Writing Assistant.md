---
type: prompt
category: academic-writing
tags: [writing, academic, research, revision]
created: 2025-07-06
last_updated: 2025-07-16
---

# P_Academic Writing Assistant

A comprehensive collection of prompts for using Claude as an academic writing assistant, covering expression improvement, technical terminology, paragraph revision, and structural organization. When I give you phrases to revise, read the resources in the \cite{} first. Literature notes with citekeys in the \cite{} can be found in the folder "00 Literature Notes" in the working directory.

## 1. Expression Enhancement

### Better Academic Expressions
```
I need to improve the academic tone and sophistication of this sentence/phrase:

"[YOUR TEXT]"

Please provide 3-5 alternative expressions that are:
- More academically appropriate
- Precise and clear
- Suitable for [journal/field] publications
- Maintain the original meaning

For each alternative, briefly explain why it's better.
```

### Transition Improvement
```
Help me improve the flow between these sentences/paragraphs:

"[CURRENT TEXT]"

Please suggest better transitions that:
- Create logical connections
- Improve readability
- Maintain academic tone
- Show the relationship between ideas (cause/effect, contrast, addition, etc.)
```

### Conciseness & Clarity
```
Make this text more concise while maintaining academic rigor:

"[YOUR TEXT]"

Please:
- Remove redundancy
- Strengthen weak phrases
- Improve sentence structure
- Keep all essential information
- Maintain technical accuracy
```

## 2. Technical Terminology

### Term Precision
```
I'm writing about [TOPIC/FIELD]. Help me find more precise technical terms for:

"[CURRENT DESCRIPTION/PHRASE]"

Please provide:
- Specific technical terminology
- Definitions of suggested terms
- Context for when to use each term
- Any relevant citations or sources for terminology
```

### Terminology Consistency
```
Review this text for terminology consistency in [FIELD]:

"[YOUR TEXT]"

Please:
- Identify inconsistent term usage
- Suggest standardized terminology
- Flag any imprecise technical language
- Recommend field-specific conventions
```

### Domain-Specific Language
```
I need to adapt this explanation for a [TARGET AUDIENCE: expert/general academic/interdisciplinary]:

"[YOUR TEXT]"

Please adjust:
- Technical depth and complexity
- Terminology sophistication
- Background knowledge assumptions
- Explanatory detail level
```

## 3. Paragraph Revision

### Paragraph Structure
```
Improve the structure and flow of this paragraph:

"[YOUR PARAGRAPH]"

Please:
- Enhance topic sentence clarity
- Improve logical progression
- Strengthen supporting evidence presentation
- Create better concluding/transition sentence
- Maintain academic voice
```

### Argument Strengthening
```
Help me strengthen the argument in this paragraph:

"[YOUR PARAGRAPH]"

Focus on:
- Clearer claim/thesis statement
- Better evidence integration
- Stronger reasoning connections
- More persuasive language
- Addressing potential counterarguments
```

### Evidence Integration
```
Improve how I integrate evidence in this paragraph:

"[YOUR PARAGRAPH WITH CITATIONS]"

Please help with:
- Smoother source integration
- Better citation context
- Clearer analysis of evidence
- Stronger connections between sources
- More sophisticated synthesis
```

## 4. Multi-Paragraph Organization

### Section Structure
```
Help me organize these related paragraphs into a coherent section:

"[YOUR PARAGRAPHS]"

Please:
- Suggest logical ordering
- Improve transitions between paragraphs
- Identify gaps in argument flow
- Recommend paragraph consolidation/division
- Enhance overall section coherence
```

### Subsection Development
```
I need to develop this topic into 3-4 well-structured paragraphs:

Topic: [YOUR TOPIC]
Key points to cover: [LIST MAIN POINTS]
Target length: [WORD COUNT]

Please provide:
- Paragraph outline with main ideas
- Suggested topic sentences
- Key evidence/examples for each paragraph
- Logical flow between paragraphs
```

### Introduction/Conclusion Pairing
```
Help me create stronger introduction and conclusion sections:

Current introduction: "[YOUR INTRO]"
Main body points: [SUMMARIZE MAIN ARGUMENTS]
Current conclusion: "[YOUR CONCLUSION]"

Please improve:
- Hook and context in introduction
- Clear thesis statement
- Conclusion that synthesizes rather than summarizes
- Stronger connection between intro and conclusion
```

## 5. Paper Structure & Organization

### Section Transitions
```
Improve the transitions between these major sections:

Section 1: [TITLE AND LAST PARAGRAPH]
Section 2: [TITLE AND FIRST PARAGRAPH]

Please create:
- Smoother section transitions
- Clear signposting language
- Logical connection between sections
- Reader guidance for section purposes
```

### Comprehensive Structure Review
```
Review the overall structure of my paper:

Title: [YOUR TITLE]
Abstract: [YOUR ABSTRACT]
Section outline: [LIST SECTIONS AND MAIN POINTS]

Please assess:
- Logical flow between sections
- Balanced section development
- Clear argument progression
- Missing elements or gaps
- Suggestions for reordering
```

## 6. Specialized Academic Tasks

### Literature Review Organization
```
Help me organize this literature review section:

Topic: [YOUR TOPIC]
Sources: [LIST KEY SOURCES]
Current draft: "[YOUR TEXT]"

Please improve:
- Thematic organization
- Source synthesis
- Gap identification
- Critical analysis depth
- Transition between themes
```

### Literature Review Synthesis: From Reference-Centric to Concept-Centric
```
my text reads like a list of what different authors have done. Help me transform it into a concept-centric synthesis.

My current draft is reference-centric, like this:
"Author A did X... Then, Author B did Y... Author C found Z..."

I want to restructure it to be concept-centric, like this:
"A key mechanistic insight is [Concept A]. This is revealed by integrating [Technique 1] and [Technique 2]. For instance, this approach has been used to explain [Specific Phenomenon], where one method clarifies the observations of the other [ref1, ref2]."

Please guide me using this blueprint:
1.  **State the Core Insight:** Start with a strong topic sentence that identifies the type of mechanistic understanding that has been achieved.
2.  **Explain the Synergy:** Describe how different methods or ideas work together. What are the limitations of one approach that another overcomes?
3.  **Provide Synthesized Evidence:** Group references to support the conceptual point. Instead of dedicating a sentence to each paper, use them as collective evidence for your claim.
4.  **Conclude with the Significance:** Briefly summarize why this integrated insight is a significant advance.

Here is the section I want to revise:
"[YOUR LITERATURE REVIEW SECTION]"

Please apply the blueprint to rewrite this section, focusing on synthesizing the ideas rather than just listing the findings.
```

### Methods Section Clarity
```
Improve the clarity of my methods section:

"[YOUR METHODS TEXT]"

Please enhance:
- Step-by-step clarity
- Technical precision
- Reproducibility details
- Justification for choices
- Appropriate technical language
```

### Results Presentation
```
Help me present these results more effectively:

Data/Findings: [DESCRIBE YOUR RESULTS]
Current text: "[YOUR RESULTS TEXT]"

Please improve:
- Clear result presentation
- Appropriate statistical language
- Objective tone
- Logical result ordering
- Connection to research questions
```

## 7. Academic Phrase Templates

### Phrase Generalization
```
Your task is to generalize a sentence copied from a research paper by:
1. Identifying domain-specific terms (such as objects, methods, properties, etc.).
2. Replacing them with bracketed placeholders (e.g., [RESEARCH_OBJECT], [METHOD], [PROPERTY]).
3. Providing a list of what kind of items should go into each placeholder.
4. Keeping the sentence structure intact for reuse in other writing.

Here's the original sentence:
"[PASTE YOUR SENTENCE HERE]"

Now transform it into a reusable academic phrase template.
```

### Creating Reusable Templates
```
Help me create reusable academic phrase templates from these well-written sentences:

"[YOUR SENTENCES]"

For each sentence, please:
- Identify the academic writing pattern
- Replace specific terms with placeholders
- Explain what types of content fit each placeholder
- Suggest variations for different contexts
- Provide examples of how to use the template
```

### Academic Writing Phrases Collector
Link: [[Academic Writing Phrases Collector]]

Use this prompt to build a collection of reusable academic phrases and sentence structures that can be adapted for different research contexts.

## 8. Usage Guidelines

### How to Use These Prompts
1. **Select appropriate prompt** based on your specific need
2. **Customize context** by filling in brackets with your specific information
3. **Provide clear text** for Claude to work with
4. **Specify your field** when relevant for terminology accuracy
5. **Ask for explanations** when you want to understand the changes
6. **Use phrase templates** to build reusable academic writing patterns

### Best Practices
- Always review suggestions for field-specific accuracy
- Maintain your authentic voice while improving expression
- Use multiple prompts for comprehensive revision
- Ask follow-up questions for clarification
- Adapt prompts to your specific research area
- **Focus on synthesis over summary**, especially in literature reviews, by using concept-centric writing prompts.
- **Build a phrase collection** using the template generalization prompts
- **Create domain-specific variations** of templates for your field

### Field-Specific Adaptations
When using these prompts, specify your field:
- Life Sciences/Biology
- Physical Sciences/Chemistry
- Engineering
- Social Sciences
- Humanities
- Interdisciplinary studies

This ensures terminology and conventions are appropriate for your discipline.

---

*Note: Always verify technical accuracy and field-specific conventions with domain experts and recent literature.*