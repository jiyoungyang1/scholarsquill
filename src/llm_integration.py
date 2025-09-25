"""
LLM integration for content analysis and note generation
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from .models import PaperMetadata, AnalysisResult
except ImportError:
    from models import PaperMetadata, AnalysisResult


class LLMNoteGenerator:
    """Note generator that uses LLM for actual content analysis"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.logger = logging.getLogger(__name__)
    
    def generate_literature_note(self, 
                                pdf_content: str, 
                                metadata: PaperMetadata,
                                focus: str = "balanced",
                                depth: str = "standard") -> str:
        """
        Generate literature note using LLM analysis
        
        This is what should actually happen:
        1. Load the appropriate template
        2. Create a prompt with template + PDF content
        3. Call LLM to analyze and fill the template
        4. Return the LLM's structured response
        """
        
        # Load template
        template_content = self._load_template(focus)
        
        # Create the prompt for the LLM
        prompt = self._create_analysis_prompt(
            template_content, pdf_content, metadata, focus, depth
        )
        
        # This is where we would call the LLM
        # For now, return a clear explanation of what should happen
        return self._create_explanation_note(metadata, focus, depth, len(pdf_content))
    
    def _load_template(self, focus: str) -> str:
        """Load the appropriate template"""
        template_file = self.templates_dir / f"{focus}.md"
        
        if template_file.exists():
            return template_file.read_text()
        else:
            # Return a basic template
            return """# {{title}}

> [!Metadata]
> **FirstAuthor**:: {{first_author}}
> **Title**:: {{title}}
> **Year**:: {{year}}
> **Citekey**:: {{citekey}}

## Executive Summary

{{summary}}

## Key Findings

{{key_findings}}

## Methodology

{{methodology}}

## Results

{{results}}

## Conclusion

{{conclusion}}
"""
    
    def _create_analysis_prompt(self, 
                               template: str, 
                               pdf_content: str, 
                               metadata: PaperMetadata,
                               focus: str, 
                               depth: str) -> str:
        """Create the prompt that should be sent to the LLM"""
        
        depth_instructions = {
            "quick": "Provide a concise summary focusing on key points only.",
            "standard": "Provide a comprehensive analysis with detailed explanations.",
            "deep": "Provide an in-depth analysis with extensive detail and context."
        }
        
        focus_instructions = {
            "research": "Focus on research methodology, experimental design, and practical findings.",
            "theory": "Focus on theoretical frameworks, mathematical models, and conceptual contributions.",
            "review": "Focus on literature synthesis, research gaps, and comprehensive overview.",
            "method": "Focus on experimental methods, procedures, and technical approaches.",
            "balanced": "Provide a balanced analysis covering all aspects of the paper."
        }
        
        prompt = f"""You are an expert academic researcher creating literature notes from scientific papers.

TASK: Analyze the following scientific paper and create a structured literature note.

FOCUS: {focus_instructions.get(focus, "Provide a balanced analysis.")}
DEPTH: {depth_instructions.get(depth, "Provide standard level detail.")}

TEMPLATE TO FOLLOW:
{template}

PAPER METADATA:
- Title: {metadata.title}
- Authors: {', '.join(metadata.authors)}
- Year: {metadata.year}
- Citekey: {metadata.citekey}

PAPER CONTENT TO ANALYZE:
{pdf_content[:10000]}...

INSTRUCTIONS:
1. Read and understand the paper content
2. Extract key information based on the {focus} focus
3. Fill in the template structure with actual content from the paper
4. Provide {depth} level analysis
5. Replace all template placeholders with real content from the paper
6. Ensure all sections contain meaningful analysis, not placeholder text

Generate the literature note now:"""
        
        return prompt
    
    def _create_explanation_note(self, 
                                metadata: PaperMetadata, 
                                focus: str, 
                                depth: str,
                                content_length: int) -> str:
        """Create a note explaining what should happen"""
        
        return f"""# {metadata.title}

> [!Metadata]
> **FirstAuthor**:: {metadata.first_author}
> **Title**:: {metadata.title}
> **Year**:: {metadata.year}
> **Citekey**:: {metadata.citekey}
> **itemType**:: journalArticle

## ⚠️ LLM Integration Required

This note was generated by the ScholarsQuill Kiro MCP server, but **actual content analysis requires LLM integration**.

### What Should Happen:
1. **PDF Content Extracted**: ✅ Successfully extracted {content_length:,} characters
2. **Metadata Extracted**: ✅ Title, authors, year, citekey identified  
3. **LLM Analysis**: ❌ **MISSING** - Need to call LLM with analysis prompt
4. **Template Filling**: ❌ **MISSING** - LLM should fill template with real content

### Current Status:
- **Focus**: {focus}
- **Depth**: {depth}
- **PDF Processing**: Working correctly
- **Content Analysis**: Basic extraction working
- **LLM Integration**: **NOT IMPLEMENTED**

### To Fix This:
The MCP server needs to:
1. Create a prompt with the template + PDF content
2. Call the LLM (Claude, GPT, etc.) with this prompt
3. Return the LLM's structured analysis
4. NOT return template placeholders

### Example of What the Prompt Should Be:
```
You are an expert researcher. Analyze this paper and create a literature note.

Template to follow:
[markdown template]

Paper content:
[extracted PDF text]

Fill the template with real analysis of this paper.
```

**The LLM should then return a properly filled template with real content analysis.**

---
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Requires LLM integration to complete*"""