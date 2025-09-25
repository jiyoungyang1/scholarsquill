"""
Template processing engine for ScholarSquill Kiro MCP Server
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
import logging

try:
    from .interfaces import TemplateProcessorInterface
    from .models import NoteTemplate, TemplateSection, FocusType, DepthType, AnalysisResult
    from .exceptions import TemplateError, ConfigurationError
except ImportError:
    from interfaces import TemplateProcessorInterface
    from models import NoteTemplate, TemplateSection, FocusType, DepthType, AnalysisResult
    from exceptions import TemplateError, ConfigurationError


class TemplateProcessor(TemplateProcessorInterface):
    """Template processor using Jinja2 for note generation with dynamic content and customization"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize template processor
        
        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = Path(templates_dir)
        self.logger = logging.getLogger(__name__)
        self._template_cache: Dict[str, Template] = {}
        self._note_template_cache: Dict[str, NoteTemplate] = {}
        
        # Template selection rules based on paper classification
        self.classification_template_map = {
            "research": "research",
            "theoretical": "theory",
            "review": "review",
            "methodology": "method",
            "experimental": "research",
            "computational": "method",
            "survey": "review"
        }
        
        # Initialize Jinja2 environment with custom functions
        try:
            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )
            
            # Add custom template functions and filters
            self.env.globals.update({
                'has_content': self._has_content,
                'conditional_section': self._conditional_section
            })
            
            # Add custom filters
            self.env.filters.update({
                'filter_by_depth': self._filter_by_depth,
                'format_list': self._format_list,
                'truncate_smart': self._truncate_smart,
                'basename': self._basename
            })
            
            self.logger.info(f"Template processor initialized with directory: {self.templates_dir}")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize template environment: {e}")
    
    def load_template(self, template_name: str) -> NoteTemplate:
        """
        Load template by name with caching
        
        Args:
            template_name: Name of template to load (without .md extension)
            
        Returns:
            NoteTemplate object
            
        Raises:
            TemplateError: If template cannot be loaded
        """
        # Check cache first
        if template_name in self._note_template_cache:
            return self._note_template_cache[template_name]
        
        template_path = self.templates_dir / f"{template_name}.md"
        
        if not template_path.exists():
            available = self.list_available_templates()
            from .exceptions import ErrorCode
            raise TemplateError(
                f"Template '{template_name}' not found. Available templates: {available}",
                ErrorCode.TEMPLATE_NOT_FOUND
            )
        
        try:
            # Load Jinja2 template
            jinja_template = self.env.get_template(f"{template_name}.md")
            self._template_cache[template_name] = jinja_template
            
            # Create NoteTemplate structure
            note_template = self._create_note_template(template_name, template_path)
            
            # Cache the note template
            self._note_template_cache[template_name] = note_template
            
            self.logger.debug(f"Loaded template: {template_name}")
            return note_template
            
        except TemplateNotFound:
            from .exceptions import ErrorCode
            raise TemplateError(f"Template file not found: {template_path}", ErrorCode.TEMPLATE_NOT_FOUND)
        except Exception as e:
            from .exceptions import ErrorCode
            raise TemplateError(f"Failed to load template '{template_name}': {e}", ErrorCode.TEMPLATE_INVALID)
    
    def render_template(self, template: NoteTemplate, data: Dict) -> str:
        """
        Render template with provided data
        
        Args:
            template: NoteTemplate to render
            data: Data dictionary for template rendering
            
        Returns:
            Rendered template as string
            
        Raises:
            TemplateError: If template rendering fails
        """
        try:
            # Get cached Jinja2 template
            jinja_template = self._template_cache.get(template.name)
            if not jinja_template:
                # Reload if not in cache
                self.load_template(template.name)
                jinja_template = self._template_cache[template.name]
            
            # Render template with data
            rendered = jinja_template.render(**data)
            
            self.logger.debug(f"Rendered template: {template.name}")
            return rendered
            
        except Exception as e:
            from .exceptions import ErrorCode
            raise TemplateError(f"Failed to render template '{template.name}': {e}", ErrorCode.TEMPLATE_RENDER_FAILED)
    
    def list_available_templates(self) -> List[str]:
        """
        List all available template names
        
        Returns:
            List of template names (without .md extension)
        """
        if not self.templates_dir.exists():
            self.logger.warning(f"Templates directory does not exist: {self.templates_dir}")
            return []
        
        templates = []
        for file_path in self.templates_dir.glob("*.md"):
            templates.append(file_path.stem)
        
        return sorted(templates)
    
    def _create_note_template(self, template_name: str, template_path: Path) -> NoteTemplate:
        """
        Create NoteTemplate structure from template file
        
        Args:
            template_name: Name of the template
            template_path: Path to template file
            
        Returns:
            NoteTemplate object
        """
        # Define template metadata based on name
        template_metadata = {
            "research": {
                "description": "Template for research papers focusing on practical applications",
                "focus_areas": [FocusType.RESEARCH],
                "sections": [
                    TemplateSection("Metadata", "Paper metadata and citation", True, "citation"),
                    TemplateSection("Summary", "Brief paper summary", True, "text"),
                    TemplateSection("Research Question", "Main research question", True, "text"),
                    TemplateSection("Methodology", "Research methodology", True, "text"),
                    TemplateSection("Key Findings", "Main research findings", True, "list"),
                    TemplateSection("Practical Applications", "Real-world applications", True, "list"),
                    TemplateSection("Limitations", "Study limitations", False, "text"),
                    TemplateSection("Future Work", "Suggested future research", False, "text")
                ]
            },
            "theory": {
                "description": "Template for theoretical papers emphasizing mathematical models",
                "focus_areas": [FocusType.THEORY],
                "sections": [
                    TemplateSection("Metadata", "Paper metadata and citation", True, "citation"),
                    TemplateSection("Summary", "Brief paper summary", True, "text"),
                    TemplateSection("Theoretical Framework", "Main theoretical framework", True, "text"),
                    TemplateSection("Key Equations", "Important equations and models", True, "equation"),
                    TemplateSection("Mathematical Models", "Mathematical formulations", True, "equation"),
                    TemplateSection("Theoretical Contributions", "Novel theoretical insights", True, "list"),
                    TemplateSection("Assumptions", "Key assumptions made", False, "list"),
                    TemplateSection("Implications", "Theoretical implications", False, "text")
                ]
            },
            "review": {
                "description": "Template for literature review papers",
                "focus_areas": [FocusType.REVIEW],
                "sections": [
                    TemplateSection("Metadata", "Paper metadata and citation", True, "citation"),
                    TemplateSection("Summary", "Brief paper summary", True, "text"),
                    TemplateSection("Scope", "Review scope and criteria", True, "text"),
                    TemplateSection("Key Themes", "Main themes identified", True, "list"),
                    TemplateSection("Literature Synthesis", "Synthesis of reviewed literature", True, "text"),
                    TemplateSection("Research Gaps", "Identified research gaps", True, "list"),
                    TemplateSection("Future Directions", "Suggested research directions", True, "list"),
                    TemplateSection("Conclusions", "Review conclusions", True, "text")
                ]
            },
            "method": {
                "description": "Template for methodology-focused papers",
                "focus_areas": [FocusType.METHOD],
                "sections": [
                    TemplateSection("Metadata", "Paper metadata and citation", True, "citation"),
                    TemplateSection("Summary", "Brief paper summary", True, "text"),
                    TemplateSection("Method Overview", "Overview of proposed method", True, "text"),
                    TemplateSection("Experimental Design", "Experimental setup", True, "text"),
                    TemplateSection("Procedures", "Detailed procedures", True, "list"),
                    TemplateSection("Validation", "Method validation approach", True, "text"),
                    TemplateSection("Results", "Experimental results", True, "text"),
                    TemplateSection("Advantages", "Method advantages", False, "list"),
                    TemplateSection("Limitations", "Method limitations", False, "list")
                ]
            },
            "balanced": {
                "description": "Balanced template covering all aspects",
                "focus_areas": [FocusType.BALANCED],
                "sections": [
                    TemplateSection("Metadata", "Paper metadata and citation", True, "citation"),
                    TemplateSection("Executive Summary", "Comprehensive overview", True, "text"),
                    TemplateSection("Research Foundation", "Research questions and framework", True, "text"),
                    TemplateSection("Methodology", "Research methods and design", True, "text"),
                    TemplateSection("Results and Findings", "Key results and analysis", True, "text"),
                    TemplateSection("Discussion and Implications", "Theoretical and practical implications", True, "text"),
                    TemplateSection("Critical Assessment", "Strengths, limitations, and future needs", True, "text"),
                    TemplateSection("Research Impact", "Field advancement and connections", False, "text"),
                    TemplateSection("Personal Research Notes", "Relevance and action items", False, "text")
                ]
            },
            "minireview": {
                "description": "Template for comprehensive literature synthesis and mini-reviews",
                "focus_areas": [FocusType.REVIEW],
                "sections": [
                    TemplateSection("Executive Summary", "Overview of literature synthesis", True, "text"),
                    TemplateSection("Research Landscape", "Thematic organization and evolution", True, "text"),
                    TemplateSection("Methodological Analysis", "Research approaches and techniques", True, "text"),
                    TemplateSection("Results Synthesis", "Convergent findings and contradictions", True, "text"),
                    TemplateSection("Literature Network", "Research connections and dependencies", True, "text"),
                    TemplateSection("Knowledge Gaps", "Critical limitations and understudied areas", True, "text"),
                    TemplateSection("Future Directions", "Priority research areas and opportunities", True, "text"),
                    TemplateSection("Implications", "Theoretical, practical, and policy implications", True, "text"),
                    TemplateSection("Conclusions", "Synthesis summary and community impact", True, "text"),
                    TemplateSection("References", "Analyzed literature and citations", True, "list")
                ]
            },
            "citemap": {
                "description": "Template for citation context mapping and reference network analysis",
                "focus_areas": [FocusType.BALANCED],
                "sections": [
                    TemplateSection("Citation Summary", "Overview of citation analysis results", True, "text"),
                    TemplateSection("Citation Contexts", "Detailed citation context analysis", True, "text"),
                    TemplateSection("Reference Network", "Network of references and relationships", True, "text"),
                    TemplateSection("Citation Patterns", "Analysis of citation usage patterns", True, "text"),
                    TemplateSection("Intellectual Connections", "How paper connects to broader literature", True, "text"),
                    TemplateSection("Network Visualization", "Visual representation of citation network", True, "diagram"),
                    TemplateSection("Analysis Insights", "Key insights from citation mapping", True, "text")
                ]
            },
            "citemap_batch": {
                "description": "Template for batch citation network analysis across multiple papers",
                "focus_areas": [FocusType.BALANCED],
                "sections": [
                    TemplateSection("Collection Summary", "Overview of paper collection analysis", True, "text"),
                    TemplateSection("Cross-References", "Papers citing each other within collection", True, "text"),
                    TemplateSection("Common Sources", "Frequently cited sources across papers", True, "text"),
                    TemplateSection("Citation Patterns", "Statistical analysis of citation practices", True, "text"),
                    TemplateSection("Intellectual Lineage", "Chronological citation relationships", True, "text"),
                    TemplateSection("Network Visualization", "Cross-paper citation network diagram", True, "diagram"),
                    TemplateSection("Research Landscape", "Insights about the research domain", True, "text"),
                    TemplateSection("Individual Files", "Links to individual citemap analyses", True, "list")
                ]
            }
        }
        
        # Get template metadata or use default
        metadata = template_metadata.get(template_name, template_metadata["balanced"])
        
        return NoteTemplate(
            name=template_name,
            description=metadata["description"],
            sections=metadata["sections"],
            focus_areas=metadata["focus_areas"]
        )
    
    def select_template(self, 
                       focus_type: FocusType, 
                       paper_classification: Optional[Tuple[str, float]] = None,
                       analysis_result: Optional[AnalysisResult] = None) -> str:
        """
        Select appropriate template based on focus type and paper classification
        
        Args:
            focus_type: Requested focus type
            paper_classification: Tuple of (paper_type, confidence) from classification
            analysis_result: Content analysis results for additional context
            
        Returns:
            Template name to use
        """
        # If focus is explicitly set and not balanced, use focus-based template
        if focus_type != FocusType.BALANCED:
            template_name = focus_type.value
            self.logger.debug(f"Using focus-based template: {template_name}")
            return template_name
        
        # For balanced focus, use paper classification if available and confident
        if paper_classification and paper_classification[1] > 0.7:  # High confidence threshold
            paper_type = paper_classification[0].lower()
            template_name = self.classification_template_map.get(paper_type, "balanced")
            self.logger.debug(f"Using classification-based template: {template_name} (confidence: {paper_classification[1]:.2f})")
            return template_name
        
        # Fallback to content-based heuristics
        if analysis_result:
            template_name = self._infer_template_from_content(analysis_result)
            self.logger.debug(f"Using content-inferred template: {template_name}")
            return template_name
        
        # Default fallback
        self.logger.debug("Using default balanced template")
        return "balanced"
    
    def render_template_with_dynamic_content(self, 
                                           template: NoteTemplate, 
                                           data: Dict[str, Any],
                                           depth_type: DepthType = DepthType.STANDARD,
                                           analysis_result: Optional[AnalysisResult] = None) -> str:
        """
        Render template with dynamic content inclusion and depth filtering
        
        Args:
            template: NoteTemplate to render
            data: Data dictionary for template rendering
            depth_type: Depth level for content filtering
            analysis_result: Analysis results for dynamic section inclusion
            
        Returns:
            Rendered template as string with dynamic content
            
        Raises:
            TemplateError: If template rendering fails
        """
        try:
            # Enhance data with dynamic content flags and depth filtering
            enhanced_data = self._enhance_template_data(data, depth_type, analysis_result)
            
            # Get cached Jinja2 template
            jinja_template = self._template_cache.get(template.name)
            if not jinja_template:
                # Reload if not in cache
                self.load_template(template.name)
                jinja_template = self._template_cache[template.name]
            
            # Render template with enhanced data
            rendered = jinja_template.render(**enhanced_data)
            
            self.logger.debug(f"Rendered template with dynamic content: {template.name}")
            return rendered
            
        except Exception as e:
            from .exceptions import ErrorCode
            raise TemplateError(f"Failed to render template '{template.name}' with dynamic content: {e}", ErrorCode.TEMPLATE_RENDER_FAILED)
    
    def create_template_inheritance_data(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create shared template data for inheritance (metadata, citations, etc.)
        
        Args:
            base_data: Base template data
            
        Returns:
            Enhanced data with inheritance support
        """
        # Extract shared metadata
        shared_data = {
            # Metadata section (shared across all templates)
            "metadata_section": {
                "title": base_data.get("title", ""),
                "first_author": base_data.get("first_author", ""),
                "authors": base_data.get("authors", []),
                "year": base_data.get("year"),
                "citekey": base_data.get("citekey", ""),
                "item_type": base_data.get("item_type", "journalArticle"),
                "journal": base_data.get("journal", ""),
                "volume": base_data.get("volume"),
                "issue": base_data.get("issue"),
                "pages": base_data.get("pages"),
                "doi": base_data.get("doi"),
            },
            
            # Citation formatting (shared)
            "formatted_citation": self._format_citation_from_data(base_data),
            
            # Generation metadata (shared)
            "generation_info": {
                "generated_at": base_data.get("generated_at"),
                "generator": "ScholarSquill Kiro"
            }
        }
        
        # Merge with original data
        enhanced_data = {**base_data, **shared_data}
        return enhanced_data
    
    def _enhance_template_data(self, 
                              data: Dict[str, Any], 
                              depth_type: DepthType,
                              analysis_result: Optional[AnalysisResult]) -> Dict[str, Any]:
        """
        Enhance template data with dynamic content flags and depth filtering
        
        Args:
            data: Original template data
            depth_type: Depth level for filtering
            analysis_result: Analysis results for dynamic inclusion
            
        Returns:
            Enhanced data dictionary
        """
        enhanced_data = data.copy()
        
        # Add depth-based filtering parameters
        enhanced_data["depth_type"] = depth_type.value
        enhanced_data["depth_limits"] = self._get_depth_limits(depth_type)
        
        # Add content availability flags for dynamic section inclusion
        if analysis_result:
            enhanced_data["content_flags"] = {
                "has_equations": bool(analysis_result.equations),
                "has_methodologies": bool(analysis_result.methodologies),
                "has_sections": bool(analysis_result.sections),
                "has_key_concepts": bool(analysis_result.key_concepts),
                "section_availability": {
                    section: bool(content.strip()) 
                    for section, content in analysis_result.sections.items()
                }
            }
        else:
            # Default flags when no analysis available
            enhanced_data["content_flags"] = {
                "has_equations": False,
                "has_methodologies": False,
                "has_sections": False,
                "has_key_concepts": False,
                "section_availability": {}
            }
        
        # Add template inheritance data
        enhanced_data = self.create_template_inheritance_data(enhanced_data)
        
        return enhanced_data
    
    def _infer_template_from_content(self, analysis_result: AnalysisResult) -> str:
        """
        Infer appropriate template from content analysis
        
        Args:
            analysis_result: Content analysis results
            
        Returns:
            Template name
        """
        # Score different template types based on content
        scores = {
            "theory": 0,
            "method": 0,
            "research": 0,
            "review": 0
        }
        
        # Theory indicators
        if analysis_result.equations:
            scores["theory"] += len(analysis_result.equations) * 2
        
        # Method indicators
        if analysis_result.methodologies:
            scores["method"] += len(analysis_result.methodologies) * 2
        
        if "methods" in analysis_result.sections or "methodology" in analysis_result.sections:
            scores["method"] += 3
        
        # Research indicators
        if "results" in analysis_result.sections:
            scores["research"] += 3
        
        if "discussion" in analysis_result.sections:
            scores["research"] += 2
        
        # Review indicators
        review_keywords = ["review", "survey", "literature", "systematic"]
        for keyword in review_keywords:
            if any(keyword in concept.lower() for concept in analysis_result.key_concepts):
                scores["review"] += 2
        
        # Return template with highest score, or balanced if tie
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return "balanced"
    
    def _get_depth_limits(self, depth_type: DepthType) -> Dict[str, int]:
        """
        Get content limits based on depth type
        
        Args:
            depth_type: Depth level
            
        Returns:
            Dictionary of limits for different content types
        """
        limits = {
            DepthType.QUICK: {
                "max_items": 3,
                "max_text_length": 500,
                "max_equations": 2,
                "max_sections": 4
            },
            DepthType.STANDARD: {
                "max_items": 5,
                "max_text_length": 1000,
                "max_equations": 5,
                "max_sections": 6
            },
            DepthType.DEEP: {
                "max_items": 10,
                "max_text_length": 2000,
                "max_equations": 10,
                "max_sections": 8
            }
        }
        
        return limits.get(depth_type, limits[DepthType.STANDARD])
    
    def _format_citation_from_data(self, data: Dict[str, Any]) -> str:
        """
        Format citation from template data
        
        Args:
            data: Template data containing metadata
            
        Returns:
            Formatted citation string
        """
        authors = data.get("authors", [])
        if not authors:
            authors_str = data.get("first_author", "Unknown Author")
        elif len(authors) == 1:
            authors_str = authors[0]
        elif len(authors) == 2:
            authors_str = f"{authors[0]} and {authors[1]}"
        else:
            authors_str = f"{authors[0]} et al."
        
        # Build citation
        citation_parts = [authors_str]
        
        if data.get("year"):
            citation_parts.append(f"({data['year']})")
        
        if data.get("title"):
            citation_parts.append(f'"{data["title"]}"')
        
        if data.get("journal"):
            citation_parts.append(f"*{data['journal']}*")
        
        if data.get("volume"):
            vol_str = f"Vol. {data['volume']}"
            if data.get("issue"):
                vol_str += f", No. {data['issue']}"
            citation_parts.append(vol_str)
        
        if data.get("pages"):
            citation_parts.append(f"pp. {data['pages']}")
        
        if data.get("doi"):
            citation_parts.append(f"DOI: {data['doi']}")
        
        return ", ".join(citation_parts) + "."
    
    # Jinja2 template helper functions
    def _has_content(self, value: Any) -> bool:
        """Check if value has meaningful content"""
        if not value:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True
    
    def _filter_by_depth(self, items: List[Any], depth_type: str, item_type: str = "items") -> List[Any]:
        """Filter items based on depth type"""
        if not items:
            return items
        
        depth_enum = DepthType(depth_type)
        limits = self._get_depth_limits(depth_enum)
        max_items = limits.get(f"max_{item_type}", limits["max_items"])
        
        return items[:max_items]
    
    def _format_list(self, items: List[Any], format_type: str = "bullet") -> str:
        """Format list items"""
        if not items:
            return ""
        
        if format_type == "bullet":
            return "\n".join(f"- {item}" for item in items)
        elif format_type == "numbered":
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
        else:
            return "\n".join(str(item) for item in items)
    
    def _truncate_smart(self, text: str, max_length: int, depth_type: str = "standard") -> str:
        """Smart truncation that respects sentence boundaries"""
        if not text or len(text) <= max_length:
            return text
        
        # Try to truncate at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.7:  # If we can keep at least 70% of content
            return text[:last_period + 1]
        else:
            return truncated + "..."
    
    def _conditional_section(self, condition: bool, content: str, fallback: str = "") -> str:
        """Conditionally include section content"""
        return content if condition else fallback
    
    def _basename(self, path: str) -> str:
        """Extract basename from file path"""
        from pathlib import Path
        return Path(path).name
    
    def clear_cache(self) -> None:
        """Clear template cache"""
        self._template_cache.clear()
        self._note_template_cache.clear()
        self.logger.debug("Template cache cleared")
    
    def validate_template_directory(self) -> bool:
        """
        Validate that template directory exists and contains templates
        
        Returns:
            True if valid, False otherwise
        """
        if not self.templates_dir.exists():
            self.logger.error(f"Templates directory does not exist: {self.templates_dir}")
            return False
        
        templates = self.list_available_templates()
        if not templates:
            self.logger.warning(f"No templates found in directory: {self.templates_dir}")
            return False
        
        return True