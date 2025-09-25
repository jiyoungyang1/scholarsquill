"""
Template loader with embedded analysis instructions for Claude AI
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

try:
    from .exceptions import TemplateError
except ImportError:
    from exceptions import TemplateError


class TemplateLoader:
    """Load templates with embedded analysis instructions for Claude"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize template loader
        
        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = Path(templates_dir)
        self.logger = logging.getLogger(__name__)
        
        # Ensure templates directory exists
        if not self.templates_dir.exists():
            self.logger.warning(f"Templates directory not found: {self.templates_dir}")
    
    async def load_template(self, focus: str) -> Dict[str, Any]:
        """
        Load template with embedded instructions for Claude
        
        Args:
            focus: Focus type (research, theory, method, review, balanced)
            
        Returns:
            Dict containing template content and metadata
        """
        try:
            # Determine template file path
            template_path = self.templates_dir / f"{focus}.md"
            
            # Fallback to balanced template if specific focus not found
            if not template_path.exists():
                self.logger.warning(f"Template not found: {template_path}, falling back to balanced.md")
                template_path = self.templates_dir / "balanced.md"
            
            # Final fallback to default template if balanced doesn't exist
            if not template_path.exists():
                self.logger.warning(f"Balanced template not found, using default template")
                return self._create_default_template(focus)
            
            # Read template content
            template_content = template_path.read_text(encoding='utf-8')
            
            # Add analysis instructions directly to template
            enhanced_template = self._add_analysis_instructions(template_content, focus)
            
            # Extract template metadata
            variables = self._extract_template_variables(template_content)
            sections = self._extract_template_sections(template_content)
            
            return {
                "template_content": enhanced_template,
                "template_name": focus,
                "template_path": str(template_path),
                "variables": variables,
                "sections": sections,
                "instructions_embedded": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load template for focus '{focus}': {str(e)}")
            raise TemplateError(f"Template loading failed: {str(e)}")
    
    def _add_analysis_instructions(self, template: str, focus: str) -> str:
        """
        Add analysis instructions directly to template
        
        Args:
            template: Original template content
            focus: Focus type
            
        Returns:
            Enhanced template with embedded instructions
        """
        # Focus-specific analysis guidance
        focus_guidance = {
            "research": {
                "description": "Research Paper Analysis",
                "emphasis": "Focus on methodology, empirical findings, and statistical analysis",
                "key_areas": [
                    "Research questions and hypotheses",
                    "Study design and methodology",
                    "Sample characteristics and data collection",
                    "Statistical analysis and results",
                    "Practical implications and applications"
                ]
            },
            "theory": {
                "description": "Theoretical Paper Analysis", 
                "emphasis": "Focus on theoretical frameworks, mathematical models, and conceptual contributions",
                "key_areas": [
                    "Theoretical propositions and assumptions",
                    "Mathematical formulations and proofs",
                    "Conceptual relationships and frameworks",
                    "Model validation and applications",
                    "Theoretical implications and extensions"
                ]
            },
            "method": {
                "description": "Methodological Paper Analysis",
                "emphasis": "Focus on experimental methods, procedures, and technical approaches",
                "key_areas": [
                    "Experimental design and procedures",
                    "Technical implementation details",
                    "Validation approaches and metrics",
                    "Performance evaluation results",
                    "Method advantages and limitations"
                ]
            },
            "review": {
                "description": "Review Paper Analysis",
                "emphasis": "Focus on literature synthesis, research gaps, and comprehensive overview",
                "key_areas": [
                    "Literature scope and search strategy",
                    "Thematic analysis and synthesis",
                    "Research gaps and limitations",
                    "Future research directions",
                    "Field advancement and implications"
                ]
            },
            "balanced": {
                "description": "Comprehensive Paper Analysis",
                "emphasis": "Provide balanced coverage of all aspects of the paper",
                "key_areas": [
                    "Research overview and objectives",
                    "Methodology and approach",
                    "Key findings and results",
                    "Theoretical contributions",
                    "Practical applications and limitations"
                ]
            }
        }
        
        guidance = focus_guidance.get(focus, focus_guidance["balanced"])
        
        instructions_header = f"""<!-- ANALYSIS INSTRUCTIONS FOR CLAUDE AI -->
<!--
TEMPLATE: {guidance['description']}
FOCUS: {focus.upper()}

CRITICAL INSTRUCTIONS:
{guidance['emphasis']}

KEY AREAS TO ANALYZE:
{chr(10).join(f'- {area}' for area in guidance['key_areas'])}

TEMPLATE FILLING RULES:
1. Read the entire PDF content provided before starting analysis
2. Extract information based on the {focus} focus area
3. Fill each section below with actual content from the paper
4. NEVER use placeholder text - all content must be real analysis
5. Use specific examples and evidence from the paper
6. Maintain academic tone and accuracy
7. Include direct quotes when they effectively illustrate points
8. Provide page references when possible
9. Ensure logical flow between sections
10. Make the analysis self-contained and comprehensive

QUALITY REQUIREMENTS:
- All information must be accurately extracted from the paper
- Analysis should be clear to someone unfamiliar with the paper
- Support all claims with specific evidence from the paper
- Maintain objective tone while providing critical analysis
- Follow the template structure while ensuring coherent narrative

SECTION GUIDANCE:
Each section below has specific requirements. Fill them based on what you find in the paper, 
adapting the depth and detail to match the content available and the {focus} focus area.
-->

"""
        
        # Add section-specific instructions
        enhanced_template = self._add_section_instructions(instructions_header + template, focus)
        
        return enhanced_template
    
    def _add_section_instructions(self, template: str, focus: str) -> str:
        """
        Add section-specific instructions to template
        
        Args:
            template: Template with header instructions
            focus: Focus type
            
        Returns:
            Template with section-specific instructions
        """
        # Common section instruction patterns
        section_instructions = {
            "citation": "<!-- Extract exact citation information from the paper metadata and content -->",
            "summary": "<!-- Provide a comprehensive summary focusing on the main contributions and findings -->",
            "executive summary": "<!-- Write a concise executive summary highlighting key points for the specified focus area -->",
            "research problem": "<!-- Identify and clearly state the research problem or question addressed -->",
            "methodology": "<!-- Describe the research methods, experimental design, and analytical approaches used -->",
            "key findings": "<!-- Extract and summarize the most important findings and results -->",
            "results": "<!-- Detail the specific results, including quantitative findings and statistical analysis -->",
            "implications": "<!-- Discuss the theoretical and practical implications of the findings -->",
            "limitations": "<!-- Identify study limitations and potential biases mentioned by the authors -->",
            "future research": "<!-- Extract suggestions for future research directions from the paper -->",
            "theoretical framework": "<!-- Describe the theoretical foundations and conceptual frameworks used -->",
            "mathematical models": "<!-- Extract and explain any mathematical models, equations, or formulations -->",
            "experimental design": "<!-- Detail the experimental setup, procedures, and validation approaches -->",
            "literature review": "<!-- Summarize how this work relates to and builds upon existing literature -->",
            "conclusions": "<!-- Extract the authors' main conclusions and their significance -->"
        }
        
        # Add instructions to sections based on common header patterns
        for section_name, instruction in section_instructions.items():
            # Look for section headers (various formats)
            patterns = [
                rf'(#+\s*{re.escape(section_name)}[^\n]*\n)',
                rf'(\*\*{re.escape(section_name)}\*\*[^\n]*\n)',
                rf'(_{re.escape(section_name)}_[^\n]*\n)'
            ]
            
            for pattern in patterns:
                template = re.sub(
                    pattern, 
                    rf'\1{instruction}\n', 
                    template, 
                    flags=re.IGNORECASE
                )
        
        return template
    
    def _extract_template_variables(self, template: str) -> List[str]:
        """
        Extract Jinja2 variables from template
        
        Args:
            template: Template content
            
        Returns:
            List of variable names found in template
        """
        # Find Jinja2 variable patterns: {{ variable_name }}
        variables = re.findall(r'\{\{\s*(\w+)\s*\}\}', template)
        
        # Find other common placeholder patterns
        placeholder_patterns = [
            r'\[([A-Z_]+)\]',  # [PLACEHOLDER]
            r'\{([A-Z_]+)\}',  # {PLACEHOLDER}
            r'<([A-Z_]+)>',    # <PLACEHOLDER>
        ]
        
        for pattern in placeholder_patterns:
            matches = re.findall(pattern, template)
            variables.extend(matches)
        
        # Remove duplicates and return
        return list(set(variables))
    
    def _extract_template_sections(self, template: str) -> List[str]:
        """
        Extract section headers from template
        
        Args:
            template: Template content
            
        Returns:
            List of section names found in template
        """
        sections = []
        
        # Find markdown headers
        header_patterns = [
            r'^#+\s+(.+)$',      # # Header, ## Header, etc.
            r'^\*\*(.+)\*\*$',   # **Bold Header**
            r'^_(.+)_$',         # _Italic Header_
        ]
        
        for pattern in header_patterns:
            matches = re.findall(pattern, template, re.MULTILINE)
            sections.extend(matches)
        
        # Clean up section names (remove extra whitespace, etc.)
        sections = [section.strip() for section in sections if section.strip()]
        
        return sections
    
    def _create_default_template(self, focus: str) -> Dict[str, Any]:
        """
        Create a default template when no template file is found
        
        Args:
            focus: Focus type
            
        Returns:
            Dict containing default template
        """
        self.logger.info(f"Creating default template for focus: {focus}")
        
        default_template = f"""<!-- DEFAULT TEMPLATE FOR {focus.upper()} ANALYSIS -->
<!-- This is a fallback template. Please analyze the paper according to the {focus} focus. -->

# Literature Note: {{{{ title }}}}

## Citation
<!-- Extract complete citation information -->

## Executive Summary
<!-- Provide comprehensive summary focusing on {focus} aspects -->

## Key Findings
<!-- Extract and analyze main findings relevant to {focus} -->

## Methodology
<!-- Describe research methods and approaches -->

## Implications
<!-- Discuss theoretical and practical implications -->

## Limitations
<!-- Identify study limitations and constraints -->

## Future Research
<!-- Extract suggestions for future work -->

## Personal Notes
<!-- Add any additional insights or connections -->
"""
        
        enhanced_template = self._add_analysis_instructions(default_template, focus)
        
        return {
            "template_content": enhanced_template,
            "template_name": focus,
            "template_path": "default",
            "variables": ["title"],
            "sections": ["Citation", "Executive Summary", "Key Findings", "Methodology", "Implications", "Limitations", "Future Research", "Personal Notes"],
            "instructions_embedded": True,
            "is_default": True
        }
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available template files
        
        Returns:
            List of available template names (without .md extension)
        """
        if not self.templates_dir.exists():
            return ["balanced"]  # Default fallback
        
        template_files = list(self.templates_dir.glob("*.md"))
        template_names = [f.stem for f in template_files]
        
        # Ensure we always have at least the basic focus types
        basic_templates = ["research", "theory", "method", "review", "balanced"]
        for template in basic_templates:
            if template not in template_names:
                template_names.append(template)
        
        return sorted(template_names)
    
    def validate_template(self, template_content: str) -> Dict[str, Any]:
        """
        Validate template content and structure
        
        Args:
            template_content: Template content to validate
            
        Returns:
            Dict with validation results
        """
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "sections_found": 0,
            "variables_found": 0
        }
        
        # Check for basic structure
        sections = self._extract_template_sections(template_content)
        variables = self._extract_template_variables(template_content)
        
        validation_result["sections_found"] = len(sections)
        validation_result["variables_found"] = len(variables)
        
        # Validate minimum requirements
        if len(sections) < 3:
            validation_result["warnings"].append("Template has fewer than 3 sections")
        
        if len(template_content.strip()) < 100:
            validation_result["warnings"].append("Template content is very short")
        
        # Check for common issues
        if "placeholder" in template_content.lower():
            validation_result["warnings"].append("Template contains placeholder text")
        
        if not re.search(r'#+\s+', template_content):
            validation_result["warnings"].append("No markdown headers found in template")
        
        return validation_result