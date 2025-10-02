"""
Note generation engine for ScholarsQuill MCP Server
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from .interfaces import NoteGeneratorInterface, ContentAnalyzerInterface, TemplateProcessorInterface
    from .models import (
        PaperMetadata, ProcessingOptions, NoteContent, AnalysisResult, 
        FocusType, DepthType, NoteTemplate
    )
    from .template_engine import TemplateProcessor
    from .exceptions import NoteGenerationError, TemplateError, ErrorCode
except ImportError:
    from interfaces import NoteGeneratorInterface, ContentAnalyzerInterface, TemplateProcessorInterface
    from models import (
        PaperMetadata, ProcessingOptions, NoteContent, AnalysisResult, 
        FocusType, DepthType, NoteTemplate
    )
    from template_engine import TemplateProcessor
    from exceptions import NoteGenerationError, TemplateError, ErrorCode


class NoteGenerator(NoteGeneratorInterface):
    """
    Template-based note generator that creates structured literature notes using Jinja2 templates
    
    This class generates rich, structured literature notes by:
    1. Analyzing PDF content using ContentAnalyzer
    2. Extracting structured data for template variables
    3. Selecting appropriate Jinja2 templates based on focus type
    4. Rendering templates with extracted content data
    5. Falling back to manual generation only when template system fails
    
    The template system supports multiple focus types (research, theory, method, review, balanced)
    and depth levels (quick, standard, deep) with dynamic content inclusion.
    """
    
    def __init__(self, 
                 template_processor: Optional[TemplateProcessorInterface] = None,
                 content_analyzer: Optional[ContentAnalyzerInterface] = None,
                 templates_dir: str = "templates"):
        """
        Initialize template-based note generator
        
        Args:
            template_processor: Template processor instance for Jinja2 template handling
            content_analyzer: Content analyzer instance for PDF content analysis
            templates_dir: Directory containing Jinja2 templates (balanced.md, research.md, etc.)
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize template processor
        if template_processor:
            self.template_processor = template_processor
        else:
            self.template_processor = TemplateProcessor(templates_dir)
        
        self.content_analyzer = content_analyzer
        
        self.logger.info("Template-based NoteGenerator initialized")
    
    def generate_note(self, content: str, metadata: PaperMetadata, 
                     focus: str, depth: str) -> str:
        """
        Generate structured literature note using Jinja2 template system
        
        This method implements the template-based note generation workflow:
        1. Analyzes content using ContentAnalyzer
        2. Selects appropriate template based on focus type and content classification
        3. Extracts structured data to populate template variables
        4. Renders template with dynamic content inclusion based on depth level
        5. Falls back to manual generation only if template system fails
        
        Args:
            content: Extracted text content from PDF
            metadata: Paper metadata (title, authors, year, etc.)
            focus: Focus type (research, theory, review, method, balanced)
            depth: Analysis depth (quick, standard, deep)
            
        Returns:
            Rich, structured markdown note generated from Jinja2 templates
            
        Raises:
            NoteGenerationError: If both template and fallback generation fail
        """
        try:
            self.logger.info(f"Generating note with focus={focus}, depth={depth}")
            
            # Convert string parameters to enums
            focus_type = FocusType(focus)
            depth_type = DepthType(depth)
            
            # Analyze content
            analysis_result = None
            if self.content_analyzer:
                analysis_result = self.content_analyzer.analyze_content(content, focus)
                self.logger.debug(f"Content analysis completed: {analysis_result.paper_type}")
            
            # Try template-based generation first
            try:
                # 1. Select appropriate template with enhanced logging
                template_name = self._select_template_with_logging(
                    focus_type, analysis_result
                )
                
                # 2. Prepare template data
                template_data = self._prepare_template_data(
                    content, metadata, analysis_result, focus_type, depth_type
                )
                
                # 3. Load and render template with comprehensive error handling
                rendered_note = self._render_template_with_error_handling(
                    template_name, template_data, depth_type, analysis_result
                )
                
                self.logger.info(f"Note generated successfully using template: {template_name}")
                return rendered_note
                
            except TemplateError as template_error:
                # Log detailed template error information
                self.logger.error(f"Template processing failed: {template_error}")
                self.logger.error(f"Template error details - Focus: {focus}, Depth: {depth}, Metadata: {metadata.citekey}")
                
                # Fallback to manual generation if template fails
                self.logger.warning("Using fallback generation due to template error")
                return self._generate_note_content_fallback(content, metadata, analysis_result, focus, depth)
                
            except Exception as template_error:
                # Log unexpected template errors with full context
                self.logger.error(f"Unexpected template generation error: {template_error}")
                self.logger.error(f"Error context - Focus: {focus}, Depth: {depth}, Paper: {metadata.title[:100] if metadata.title else 'Unknown'}")
                
                # Fallback to manual generation for any template system failure
                self.logger.warning("Using fallback generation due to unexpected template error")
                return self._generate_note_content_fallback(content, metadata, analysis_result, focus, depth)
            
        except Exception as e:
            self.logger.error(f"Note generation failed: {e}")
            raise NoteGenerationError(f"Failed to generate note: {e}")
    
    def _select_template_with_logging(self, 
                                     focus_type: FocusType, 
                                     analysis_result: Optional[AnalysisResult]) -> str:
        """
        Select appropriate template with detailed logging of decision process
        
        Args:
            focus_type: Requested focus type
            analysis_result: Content analysis results
            
        Returns:
            Template name to use
        """
        self.logger.debug(f"Starting template selection for focus_type: {focus_type.value}")
        
        # Prepare paper classification tuple if analysis available
        paper_classification = None
        if analysis_result:
            paper_classification = (analysis_result.paper_type, analysis_result.confidence)
            self.logger.debug(f"Paper classification: {paper_classification[0]} (confidence: {paper_classification[1]:.2f})")
        else:
            self.logger.debug("No content analysis available for template selection")
        
        # Log focus type decision
        if focus_type != FocusType.BALANCED:
            self.logger.info(f"Using explicit focus type: {focus_type.value}")
        else:
            self.logger.debug("Focus type is BALANCED, will use classification or content-based selection")
        
        # Call template processor selection with logging
        try:
            template_name = self.template_processor.select_template(
                focus_type, 
                paper_classification,
                analysis_result
            )
            
            # Log selection reasoning
            if focus_type != FocusType.BALANCED:
                self.logger.info(f"Selected template '{template_name}' based on explicit focus type '{focus_type.value}'")
            elif paper_classification and paper_classification[1] > 0.7:
                self.logger.info(f"Selected template '{template_name}' based on paper classification '{paper_classification[0]}' with high confidence ({paper_classification[1]:.2f})")
            elif analysis_result:
                self.logger.info(f"Selected template '{template_name}' based on content analysis heuristics")
            else:
                self.logger.info(f"Selected default template '{template_name}' due to insufficient classification data")
            
            # Validate template exists
            available_templates = self.template_processor.list_available_templates()
            if template_name not in available_templates:
                self.logger.warning(f"Selected template '{template_name}' not found in available templates: {available_templates}")
                fallback_template = "balanced"
                self.logger.info(f"Falling back to template: {fallback_template}")
                return fallback_template
            
            return template_name
            
        except TemplateError as e:
            self.logger.error(f"Template selection failed with TemplateError: {e}")
            self.logger.error(f"Template selection context - Focus: {focus_type.value}, Analysis available: {analysis_result is not None}")
            fallback_template = "balanced"
            self.logger.warning(f"Using fallback template '{fallback_template}' due to template selection error")
            return fallback_template
            
        except Exception as e:
            self.logger.error(f"Unexpected error during template selection: {e}")
            self.logger.error(f"Template selection context - Focus: {focus_type.value}, Analysis available: {analysis_result is not None}")
            fallback_template = "balanced"
            self.logger.warning(f"Using fallback template '{fallback_template}' due to unexpected error")
            return fallback_template
    
    def _render_template_with_error_handling(self, 
                                           template_name: str,
                                           template_data: Dict[str, Any],
                                           depth_type: DepthType,
                                           analysis_result: Optional[AnalysisResult]) -> str:
        """
        Render template with comprehensive error handling and validation
        
        Args:
            template_name: Name of template to render
            template_data: Data dictionary for template rendering
            depth_type: Depth level for content filtering
            analysis_result: Analysis results for dynamic content inclusion
            
        Returns:
            Rendered template as string
            
        Raises:
            TemplateError: If template rendering fails completely
        """
        try:
            self.logger.debug(f"Loading template: {template_name}")
            
            # Load template with error handling
            try:
                template = self.template_processor.load_template(template_name)
                self.logger.debug(f"Template loaded successfully: {template_name}")
            except TemplateError as e:
                self.logger.error(f"Failed to load template '{template_name}': {e}")
                self.logger.error(f"Template loading context - Available templates: {self.template_processor.list_available_templates()}")
                raise TemplateError(f"Template '{template_name}' not found or corrupted: {e}", ErrorCode.TEMPLATE_NOT_FOUND)
            except Exception as e:
                self.logger.error(f"Unexpected error loading template '{template_name}': {e}")
                self.logger.error(f"Template loading context - Template path and permissions may be invalid")
                raise TemplateError(f"Failed to load template '{template_name}' due to system error: {e}", ErrorCode.TEMPLATE_INVALID)
            
            # Validate template data before rendering
            self._validate_template_data(template_data, template_name)
            
            # Render template with dynamic content
            try:
                self.logger.debug(f"Rendering template with dynamic content: {template_name}")
                rendered_note = self.template_processor.render_template_with_dynamic_content(
                    template, template_data, depth_type, analysis_result
                )
                
                # Validate rendered output
                if not rendered_note or not rendered_note.strip():
                    raise TemplateError(f"Template '{template_name}' rendered empty content", ErrorCode.TEMPLATE_RENDER_FAILED)
                
                # Log successful rendering with content statistics
                self._log_rendering_statistics(rendered_note, template_name)
                
                return rendered_note
                
            except TemplateError as e:
                self.logger.error(f"Template rendering failed for '{template_name}': {e}")
                self.logger.error(f"Rendering context - Template variables: {len(template_data)} provided")
                self.logger.debug(f"Template data keys: {list(template_data.keys())}")
                raise TemplateError(f"Template '{template_name}' rendering failed - missing variables or syntax error: {e}", ErrorCode.TEMPLATE_RENDER_FAILED)
            except Exception as e:
                self.logger.error(f"Unexpected error rendering template '{template_name}': {e}")
                self.logger.error(f"Rendering context - Data type issues or template corruption possible")
                raise TemplateError(f"Failed to render template '{template_name}' due to unexpected error: {e}", ErrorCode.TEMPLATE_RENDER_FAILED)
                
        except Exception as e:
            self.logger.error(f"Template processing failed completely for '{template_name}': {e}")
            raise
    
    def _validate_template_data(self, template_data: Dict[str, Any], template_name: str) -> None:
        """
        Validate template data before rendering
        
        Args:
            template_data: Data dictionary for template rendering
            template_name: Name of template being rendered
        """
        # Check for required metadata fields
        required_fields = ["title", "first_author", "citekey", "generated_at"]
        missing_fields = []
        
        for field in required_fields:
            if field not in template_data or not template_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            self.logger.warning(f"Template data missing required fields for '{template_name}': {missing_fields}")
            self.logger.warning(f"Missing field details - This may cause template rendering issues")
            # Don't raise error, just log warning as templates should handle missing data gracefully
            
            # Provide fallback values for critical missing fields
            for field in missing_fields:
                if field == "title":
                    template_data[field] = "Untitled Paper"
                elif field == "first_author":
                    template_data[field] = "Unknown Author"
                elif field == "citekey":
                    template_data[field] = f"unknown_{datetime.now().strftime('%Y%m%d')}"
                elif field == "generated_at":
                    template_data[field] = datetime.now()
            
            self.logger.info(f"Provided fallback values for missing required fields: {missing_fields}")
        
        # Log available template variables for debugging
        available_vars = list(template_data.keys())
        self.logger.debug(f"Template data contains {len(available_vars)} variables: {available_vars[:10]}{'...' if len(available_vars) > 10 else ''}")
        
        # Check for content-specific variables based on template type
        content_vars = [
            "research_overview", "key_contributions", "significance", 
            "research_question", "methodology", "key_findings"
        ]
        
        available_content_vars = [var for var in content_vars if var in template_data and template_data[var]]
        missing_content_vars = [var for var in content_vars if var not in template_data or not template_data[var]]
        
        self.logger.debug(f"Available content variables: {available_content_vars}")
        if missing_content_vars:
            self.logger.debug(f"Missing/empty content variables: {missing_content_vars}")
    
    def _log_rendering_statistics(self, rendered_note: str, template_name: str) -> None:
        """
        Log statistics about the rendered template
        
        Args:
            rendered_note: Rendered template content
            template_name: Name of template that was rendered
        """
        # Basic statistics
        line_count = len(rendered_note.split('\n'))
        word_count = len(rendered_note.split())
        char_count = len(rendered_note)
        
        self.logger.debug(f"Template '{template_name}' rendered successfully: {line_count} lines, {word_count} words, {char_count} characters")
        
        # Check for template structure markers
        section_markers = rendered_note.count('##')  # Count of section headers
        list_items = rendered_note.count('- ')  # Count of list items
        
        self.logger.debug(f"Template structure: {section_markers} sections, {list_items} list items")
        
        # Validate minimum content requirements
        if word_count < 50:
            self.logger.warning(f"Template '{template_name}' produced very short content ({word_count} words)")
        elif word_count > 5000:
            self.logger.info(f"Template '{template_name}' produced extensive content ({word_count} words)")
        
        # Check for placeholder content that wasn't replaced
        placeholder_patterns = [
            "require further analysis", "embedded within the paper", 
            "detailed analysis", "comprehensive understanding"
        ]
        
        placeholder_count = sum(rendered_note.lower().count(pattern) for pattern in placeholder_patterns)
        if placeholder_count > 3:
            self.logger.warning(f"Template '{template_name}' contains {placeholder_count} placeholder phrases - content extraction may need improvement")
    
    def _prepare_template_data(self, 
                              content: str, 
                              metadata: PaperMetadata,
                              analysis_result: Optional[AnalysisResult],
                              focus_type: FocusType,
                              depth_type: DepthType) -> Dict[str, Any]:
        """
        Prepare data dictionary for template rendering
        
        Args:
            content: Raw text content
            metadata: Paper metadata
            analysis_result: Content analysis results
            focus_type: Focus type for generation
            depth_type: Depth level for generation
            
        Returns:
            Template data dictionary
        """
        # Base metadata mapping
        template_data = {
            "title": metadata.title,
            "first_author": metadata.first_author,
            "authors": metadata.authors,
            "year": metadata.year,
            "citekey": metadata.citekey,
            "item_type": metadata.item_type,
            "journal": metadata.journal,
            "volume": metadata.volume,
            "issue": metadata.issue,
            "pages": metadata.pages,
            "doi": metadata.doi,
            "generated_at": datetime.now()
        }
        
        # Extract content-based data for template variables
        if analysis_result:
            template_data.update(self._extract_content_data(content, analysis_result, focus_type, depth_type))
        else:
            # Fallback to basic content extraction when no analysis available
            template_data.update(self._extract_basic_content_data(content, focus_type, depth_type))
        
        return template_data
    
    def _extract_content_data(self, 
                             content: str, 
                             analysis_result: AnalysisResult,
                             focus_type: FocusType, 
                             depth_type: DepthType) -> Dict[str, Any]:
        """
        Extract structured content data for templates from analysis results
        
        Args:
            content: Raw text content
            analysis_result: Content analysis results
            focus_type: Focus type for generation
            depth_type: Depth level for generation
            
        Returns:
            Template data dictionary with content-based variables
        """
        data = {}
        sections = analysis_result.sections
        
        # Common template variables with meaningful defaults
        data["research_overview"] = self._extract_research_overview(sections)
        data["key_contributions"] = self._extract_key_contributions(analysis_result)
        data["significance"] = self._extract_significance(sections)
        data["research_question"] = self._extract_research_question(sections)
        data["theoretical_framework"] = self._extract_theoretical_framework(sections)
        data["methodology"] = self._extract_methodology(sections)
        data["key_findings"] = self._extract_key_findings(analysis_result)
        data["limitations"] = self._extract_limitations(sections)
        data["practical_applications"] = self._extract_practical_applications(sections)
        
        # Additional template variables for comprehensive coverage
        data["conclusions"] = self._extract_conclusions(sections)
        data["new_knowledge"] = self._extract_new_knowledge(sections)
        data["theoretical_connections"] = self._extract_theoretical_connections(sections)
        data["methodological_insights"] = self._extract_methodological_insights(sections)
        data["research_gaps"] = self._extract_research_gaps(sections)
        data["research_impact"] = self._extract_research_impact(sections)
        data["follow_up_questions"] = self._extract_follow_up_questions(sections)
        data["implementation"] = self._extract_implementation(sections)
        data["scalability"] = self._extract_scalability(sections)
        data["related_work"] = self._extract_related_work(sections)
        data["competing_approaches"] = self._extract_competing_approaches(sections)
        data["future_work"] = self._extract_future_work(sections)
        
        # Balanced template specific variables
        data["literature_context"] = self._extract_literature_context(sections)
        data["research_design"] = self._extract_research_design(sections)
        data["methods"] = self._extract_methods_list(sections)
        data["study_parameters"] = self._extract_study_parameters(sections)
        data["primary_results"] = self._extract_primary_results(sections)
        data["supporting_evidence"] = self._extract_supporting_evidence(sections)
        data["data_analysis"] = self._extract_data_analysis(sections)
        data["theoretical_implications"] = self._extract_theoretical_implications(sections)
        data["methodological_contributions"] = self._extract_methodological_contributions(sections)
        data["strengths"] = self._extract_strengths(sections)
        data["future_research"] = self._extract_future_research(sections)
        data["field_advancement"] = self._extract_field_advancement(sections)
        data["cross_disciplinary"] = self._extract_cross_disciplinary(sections)
        data["personal_relevance"] = self._extract_personal_relevance(sections)
        data["key_takeaways"] = self._extract_key_takeaways(sections)
        data["action_items"] = self._extract_action_items(sections)
        
        # Focus-specific data extraction
        if focus_type == FocusType.THEORY:
            data.update(self._extract_theory_specific_data(analysis_result))
        elif focus_type == FocusType.RESEARCH:
            data.update(self._extract_research_specific_data(analysis_result))
        elif focus_type == FocusType.METHOD:
            data.update(self._extract_method_specific_data(analysis_result))
        elif focus_type == FocusType.REVIEW:
            data.update(self._extract_review_specific_data(analysis_result))
        # BALANCED uses common variables only
        
        return data
    
    def _generate_note_content_fallback(self, 
                                       content: str, 
                                       metadata: PaperMetadata,
                                       analysis_result: Optional[AnalysisResult],
                                       focus: str, 
                                       depth: str) -> str:
        """
        Fallback note generation using manual markdown generation when template system fails
        
        DEPRECATED: This method should only be used as a fallback when the template system
        fails completely. The primary note generation should use the Jinja2 template system
        with proper content extraction and template data mapping.
        
        Args:
            content: Raw text content
            metadata: Paper metadata
            analysis_result: Content analysis results (may be None)
            focus: Focus type as string
            depth: Depth level as string
            
        Returns:
            Manually generated markdown note
        """
        self.logger.warning(f"Using DEPRECATED fallback note generation - Focus: {focus}, Depth: {depth}")
        self.logger.warning(f"Fallback reason: Template system unavailable or failed - this should be investigated")
        self.logger.info("Primary note generation should use template system with proper content extraction")
        
        try:
            # Generate basic markdown structure manually
            note_lines = []
            
            # Header section
            note_lines.append(f"# Literature Note: {metadata.title or 'Untitled Paper'}")
            note_lines.append("")
            
            # Metadata section
            note_lines.append("## Metadata")
            note_lines.append("")
            note_lines.append(f"- **Authors**: {', '.join(metadata.authors) if metadata.authors else metadata.first_author or 'Unknown'}")
            note_lines.append(f"- **Year**: {metadata.year or 'Unknown'}")
            note_lines.append(f"- **Citekey**: {metadata.citekey}")
            if metadata.journal:
                note_lines.append(f"- **Journal**: {metadata.journal}")
            if metadata.doi:
                note_lines.append(f"- **DOI**: {metadata.doi}")
            note_lines.append(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            note_lines.append("")
            
            # Content sections based on focus type
            if focus.lower() == "research":
                note_lines.extend(self._generate_research_fallback_sections(analysis_result, content))
            elif focus.lower() == "theory":
                note_lines.extend(self._generate_theory_fallback_sections(analysis_result, content))
            elif focus.lower() == "method":
                note_lines.extend(self._generate_method_fallback_sections(analysis_result, content))
            elif focus.lower() == "review":
                note_lines.extend(self._generate_review_fallback_sections(analysis_result, content))
            else:  # balanced or unknown
                note_lines.extend(self._generate_balanced_fallback_sections(analysis_result, content))
            
            # Footer
            note_lines.append("")
            note_lines.append("---")
            note_lines.append("*Note generated using fallback system due to template processing issues*")
            
            fallback_note = "\n".join(note_lines)
            
            # Log fallback generation statistics
            word_count = len(fallback_note.split())
            line_count = len(note_lines)
            self.logger.info(f"Fallback note generated successfully: {line_count} lines, {word_count} words")
            
            return fallback_note
            
        except Exception as e:
            self.logger.error(f"Fallback generation failed: {e}")
            # Ultimate fallback - minimal note
            return self._generate_minimal_fallback_note(metadata)
    
    def _generate_research_fallback_sections(self, 
                                           analysis_result: Optional[AnalysisResult], 
                                           content: str) -> List[str]:
        """
        Generate research-focused fallback sections (DEPRECATED - kept for fallback only)
        
        This method is deprecated and should only be used as a fallback when template 
        processing fails. The primary note generation should use the template system.
        """
        self.logger.warning("Using deprecated manual research section generation - template system should be used instead")
        
        sections = []
        
        sections.append("## Research Overview")
        sections.append("")
        if analysis_result and analysis_result.sections.get("abstract"):
            abstract_summary = self._summarize_text(analysis_result.sections["abstract"], max_length=300)
            sections.append(abstract_summary)
        else:
            sections.append("Research overview requires analysis of the paper's abstract and introduction.")
        sections.append("")
        
        sections.append("## Research Question")
        sections.append("")
        if analysis_result:
            research_question = self._extract_research_question(analysis_result.sections)
            sections.append(research_question)
        else:
            sections.append("Research questions and objectives require detailed analysis of the paper content.")
        sections.append("")
        
        sections.append("## Methodology")
        sections.append("")
        if analysis_result:
            methodology = self._extract_methodology(analysis_result.sections)
            sections.append(methodology)
        else:
            sections.append("Research methodology and approach require analysis of the methods section.")
        sections.append("")
        
        sections.append("## Key Findings")
        sections.append("")
        if analysis_result:
            findings = self._extract_key_findings(analysis_result)
            for finding in findings[:5]:
                sections.append(f"- {finding}")
        else:
            sections.append("- Key findings require analysis of results and conclusions")
            sections.append("- Primary outcomes and significance need detailed review")
        sections.append("")
        
        sections.append("## Significance")
        sections.append("")
        if analysis_result:
            significance = self._extract_significance(analysis_result.sections)
            sections.append(significance)
        else:
            sections.append("Research significance and implications require analysis of discussion and conclusion sections.")
        sections.append("")
        
        return sections
    
    def _generate_theory_fallback_sections(self, 
                                         analysis_result: Optional[AnalysisResult], 
                                         content: str) -> List[str]:
        """
        Generate theory-focused fallback sections (DEPRECATED - kept for fallback only)
        
        This method is deprecated and should only be used as a fallback when template 
        processing fails. The primary note generation should use the template system.
        """
        self.logger.warning("Using deprecated manual theory section generation - template system should be used instead")
        
        sections = []
        
        sections.append("## Theoretical Framework")
        sections.append("")
        if analysis_result:
            framework = self._extract_theoretical_framework(analysis_result.sections)
            sections.append(framework)
        else:
            sections.append("Theoretical framework and conceptual foundations require detailed analysis.")
        sections.append("")
        
        sections.append("## Key Concepts")
        sections.append("")
        if analysis_result and analysis_result.key_concepts:
            for concept in analysis_result.key_concepts[:5]:
                sections.append(f"- {concept}")
        else:
            sections.append("- Core theoretical concepts require extraction from paper content")
            sections.append("- Conceptual relationships and definitions need analysis")
        sections.append("")
        
        sections.append("## Theoretical Contributions")
        sections.append("")
        if analysis_result:
            contributions = self._extract_key_contributions(analysis_result)
            for contrib in contributions[:3]:
                sections.append(f"- {contrib}")
        else:
            sections.append("- Theoretical contributions and novel insights require analysis")
            sections.append("- Conceptual advances and framework extensions need review")
        sections.append("")
        
        return sections
    
    def _generate_method_fallback_sections(self, 
                                         analysis_result: Optional[AnalysisResult], 
                                         content: str) -> List[str]:
        """
        Generate method-focused fallback sections (DEPRECATED - kept for fallback only)
        
        This method is deprecated and should only be used as a fallback when template 
        processing fails. The primary note generation should use the template system.
        """
        self.logger.warning("Using deprecated manual method section generation - template system should be used instead")
        
        sections = []
        
        sections.append("## Methodology Overview")
        sections.append("")
        if analysis_result:
            methodology = self._extract_methodology(analysis_result.sections)
            sections.append(methodology)
        else:
            sections.append("Methodological approach and research design require detailed analysis.")
        sections.append("")
        
        sections.append("## Methods and Procedures")
        sections.append("")
        if analysis_result and "methods" in analysis_result.sections:
            methods_summary = self._summarize_text(analysis_result.sections["methods"], max_length=400)
            sections.append(methods_summary)
        else:
            sections.append("Detailed methods and procedures require analysis of the methodology section.")
        sections.append("")
        
        sections.append("## Methodological Insights")
        sections.append("")
        sections.append("- Methodological approaches and innovations require detailed review")
        sections.append("- Technical procedures and validation methods need analysis")
        sections.append("- Reproducibility and implementation considerations require evaluation")
        sections.append("")
        
        return sections
    
    def _generate_review_fallback_sections(self, 
                                         analysis_result: Optional[AnalysisResult], 
                                         content: str) -> List[str]:
        """
        Generate review-focused fallback sections (DEPRECATED - kept for fallback only)
        
        This method is deprecated and should only be used as a fallback when template 
        processing fails. The primary note generation should use the template system.
        """
        self.logger.warning("Using deprecated manual review section generation - template system should be used instead")
        
        sections = []
        
        sections.append("## Literature Context")
        sections.append("")
        sections.append("Literature context and related work require analysis of introduction and background sections.")
        sections.append("")
        
        sections.append("## Synthesis and Analysis")
        sections.append("")
        if analysis_result:
            key_findings = self._extract_key_findings(analysis_result)
            sections.append("Key synthesis points:")
            for finding in key_findings[:4]:
                sections.append(f"- {finding}")
        else:
            sections.append("Literature synthesis and comparative analysis require detailed review.")
        sections.append("")
        
        sections.append("## Research Gaps")
        sections.append("")
        sections.append("Identified research gaps and future directions require analysis of discussion and conclusion sections.")
        sections.append("")
        
        return sections
    
    def _generate_balanced_fallback_sections(self, 
                                           analysis_result: Optional[AnalysisResult], 
                                           content: str) -> List[str]:
        """
        Generate balanced fallback sections covering all aspects (DEPRECATED - kept for fallback only)
        
        This method is deprecated and should only be used as a fallback when template 
        processing fails. The primary note generation should use the template system.
        """
        self.logger.warning("Using deprecated manual balanced section generation - template system should be used instead")
        
        sections = []
        
        sections.append("## Overview")
        sections.append("")
        if analysis_result and analysis_result.sections.get("abstract"):
            abstract_summary = self._summarize_text(analysis_result.sections["abstract"], max_length=250)
            sections.append(abstract_summary)
        else:
            sections.append("Paper overview and main contributions require analysis of abstract and introduction.")
        sections.append("")
        
        sections.append("## Key Points")
        sections.append("")
        if analysis_result:
            findings = self._extract_key_findings(analysis_result)
            for finding in findings[:4]:
                sections.append(f"- {finding}")
        else:
            sections.append("- Main findings and contributions require detailed analysis")
            sections.append("- Methodological approaches and innovations need review")
            sections.append("- Theoretical implications and practical applications require evaluation")
        sections.append("")
        
        sections.append("## Methodology")
        sections.append("")
        if analysis_result:
            methodology = self._extract_methodology(analysis_result.sections)
            sections.append(methodology)
        else:
            sections.append("Research methodology and approach require analysis of methods section.")
        sections.append("")
        
        sections.append("## Significance")
        sections.append("")
        sections.append("Research significance and broader implications require analysis of discussion and conclusion sections.")
        sections.append("")
        
        return sections
    
    def _generate_minimal_fallback_note(self, metadata: PaperMetadata) -> str:
        """
        Generate minimal fallback note when all other generation methods fail
        
        Args:
            metadata: Paper metadata
            
        Returns:
            Minimal markdown note with basic metadata only
        """
        self.logger.warning("Generating minimal fallback note - all other generation methods failed")
        
        minimal_note = f"""# Literature Note: {metadata.title or 'Untitled Paper'}

## Metadata

- **Authors**: {', '.join(metadata.authors) if metadata.authors else metadata.first_author or 'Unknown'}
- **Year**: {metadata.year or 'Unknown'}
- **Citekey**: {metadata.citekey}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Note

This paper requires manual analysis and note generation due to processing limitations.

Key areas for manual review:
- Research objectives and questions
- Methodology and approach
- Main findings and results
- Theoretical contributions
- Practical implications

---
*Minimal note generated due to system processing issues*
"""
        
        self.logger.info("Minimal fallback note generated successfully")
        return minimal_note
    
    def _extract_basic_content_data(self, 
                                   content: str, 
                                   focus_type: FocusType, 
                                   depth_type: DepthType) -> Dict[str, Any]:
        """
        Extract basic content data when no analysis result is available
        
        Args:
            content: Raw text content
            focus_type: Focus type for generation
            depth_type: Depth level for generation
            
        Returns:
            Template data dictionary with basic fallback content
        """
        # Provide meaningful fallback content for all template variables
        return {
            "research_overview": "This paper presents research findings that require detailed analysis for comprehensive understanding.",
            "key_contributions": [
                "Novel insights and findings presented in the study",
                "Methodological or theoretical contributions to the field",
                "Practical applications and implications identified"
            ],
            "significance": "This work contributes to the advancement of knowledge in its respective field.",
            "research_question": "Research objectives and questions require further analysis of the paper content.",
            "theoretical_framework": "Theoretical foundation and conceptual framework are embedded within the paper.",
            "methodology": "Research methodology and approach require detailed analysis of the methods section.",
            "key_findings": [
                "Primary results and findings from the study",
                "Supporting evidence and validation",
                "Significant observations and insights"
            ],
            "limitations": "Study limitations and scope restrictions are discussed within the paper.",
            "practical_applications": [
                "Real-world applications and implementations",
                "Clinical or industrial relevance",
                "Policy and decision-making implications"
            ],
            # Additional template variables with fallback content
            "conclusions": "Primary conclusions and their implications for the field",
            "new_knowledge": "What novel insights does this paper contribute?",
            "theoretical_connections": "How does this relate to existing theoretical frameworks?",
            "methodological_insights": "What methodological approaches can be applied?",
            "research_gaps": "What gaps in knowledge does this study reveal?",
            "research_impact": "How might this change future research approaches or hypotheses?",
            "follow_up_questions": [
                "What additional studies are needed?",
                "How can these findings be extended?",
                "What methodological improvements could be made?"
            ],
            "implementation": "Factors to consider for practical implementation",
            "scalability": "How broadly applicable are these findings?",
            "related_work": "How this work builds on or relates to previous research",
            "competing_approaches": "Alternative methods or theories in this area",
            "future_work": [
                "Suggested extensions and improvements",
                "Unexplored applications",
                "Methodological developments needed"
            ],
            # Balanced template specific variables
            "literature_context": "How this work builds on and relates to existing research",
            "research_design": "Overall study design and methodological approach",
            "methods": [
                "Primary experimental or analytical methods",
                "Data collection procedures",
                "Analysis techniques employed"
            ],
            "study_parameters": "Key variables, conditions, and measurement parameters",
            "primary_results": "Main findings and quantitative results",
            "supporting_evidence": [
                "Secondary findings that support main conclusions",
                "Statistical validation and significance",
                "Reproducibility and consistency measures"
            ],
            "data_analysis": "Key insights from data analysis and interpretation",
            "theoretical_implications": "How findings advance theoretical understanding",
            "methodological_contributions": "Advances in research methods or analytical approaches",
            "strengths": [
                "Methodological rigor and innovation",
                "Comprehensive analysis and validation",
                "Clear practical relevance"
            ],
            "future_research": "Identified gaps and suggested future research directions",
            "field_advancement": "How this work advances the broader research field",
            "cross_disciplinary": "Relevance to other research areas or disciplines",
            "personal_relevance": "How this paper relates to your current research interests",
            "key_takeaways": "Most important insights and lessons learned",
            "action_items": [
                "Specific methods to investigate further",
                "Concepts to incorporate into current research",
                "Follow-up papers to read"
            ]
        }
    
    # Content extraction methods for template variables
    def _extract_research_overview(self, sections: Dict[str, str]) -> str:
        """
        Extract research overview for executive summaries from abstract or introduction
        
        Args:
            sections: Dictionary of paper sections
            
        Returns:
            Comprehensive research overview
        """
        # Prioritize abstract for overview
        if "abstract" in sections:
            abstract_text = self._clean_extracted_text(sections["abstract"])
            if abstract_text and len(abstract_text) > 50:
                # Create structured overview from abstract
                overview = self._create_structured_overview(abstract_text)
                return overview if overview else self._summarize_text(abstract_text, max_length=400)
        
        # Fallback to introduction
        if "introduction" in sections:
            intro_text = self._clean_extracted_text(sections["introduction"])
            if intro_text and len(intro_text) > 50:
                # Extract key overview elements from introduction
                overview = self._extract_overview_from_introduction(intro_text)
                return overview if overview else self._summarize_text(intro_text, max_length=400)
        
        return "Comprehensive overview of the study's purpose, approach, and significance"
    
    def _create_structured_overview(self, abstract_text: str) -> str:
        """Create structured overview from abstract"""
        # Try to identify key components in abstract
        components = []
        
        # Background/context
        background = self._extract_background_from_abstract(abstract_text)
        if background:
            components.append(f"Background: {background}")
        
        # Objective/purpose
        objective = self._extract_research_question_from_text(abstract_text)
        if objective:
            components.append(f"Objective: {objective}")
        
        # Methods (brief)
        methods = self._extract_brief_methods_from_abstract(abstract_text)
        if methods:
            components.append(f"Methods: {methods}")
        
        # Results (brief)
        results = self._extract_brief_results_from_abstract(abstract_text)
        if results:
            components.append(f"Results: {results}")
        
        if len(components) >= 2:
            return ". ".join(components) + "."
        
        return ""
    
    def _extract_background_from_abstract(self, text: str) -> str:
        """Extract background context from abstract"""
        background_patterns = [
            r"^([^.!?]*(?:background|context|problem|issue)[^.!?]*)",
            r"^([^.!?]{20,100})",  # First sentence if reasonable length
        ]
        
        for pattern in background_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                background = self._clean_extracted_text(match.group(1))
                if len(background) > 20 and len(background) < 150:
                    return background
        
        return ""
    
    def _extract_brief_methods_from_abstract(self, text: str) -> str:
        """Extract brief methods from abstract"""
        method_patterns = [
            r"(?:we\s+)?(?:used|employed|applied|conducted|performed)\s+([^.!?]+)",
            r"(?:methods?|methodology|approach)\s*:?\s*([^.!?]+)",
            r"(?:using|through|via)\s+([^.!?]+)"
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                method = self._clean_extracted_text(match.group(1))
                if len(method) > 15 and len(method) < 100:
                    return method
        
        return ""
    
    def _extract_brief_results_from_abstract(self, text: str) -> str:
        """Extract brief results from abstract"""
        result_patterns = [
            r"(?:results?\s+)?(?:showed?|demonstrated?|revealed?|found)\s+(?:that\s+)?([^.!?]+)",
            r"(?:we\s+)?(?:found|observed|identified)\s+([^.!?]+)",
            r"(?:significant|notable)\s+([^.!?]*(?:increase|decrease|improvement|reduction|difference|correlation))"
        ]
        
        for pattern in result_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result = self._clean_extracted_text(match.group(1))
                if len(result) > 15 and len(result) < 100:
                    return result
        
        return ""
    
    def _extract_key_contributions(self, analysis_result: AnalysisResult) -> List[str]:
        """Extract key contributions from analysis results"""
        contributions = []
        
        # Use key concepts if available
        if analysis_result.key_concepts:
            contributions.extend(analysis_result.key_concepts[:3])
        
        # Extract from conclusion section
        if "conclusion" in analysis_result.sections:
            conclusion_text = analysis_result.sections["conclusion"]
            conclusion_contributions = self._extract_findings_from_text(conclusion_text)
            contributions.extend(conclusion_contributions[:2])
        
        # Remove duplicates and limit
        unique_contributions = list(dict.fromkeys(contributions))[:5]
        
        return unique_contributions if unique_contributions else [
            "Novel insights and findings presented in the study",
            "Methodological or theoretical contributions to the field",
            "Practical applications and implications identified"
        ]
    
    def _extract_significance(self, sections: Dict[str, str]) -> str:
        """
        Extract significance to identify paper importance from conclusion or discussion
        
        Args:
            sections: Dictionary of paper sections
            
        Returns:
            Paper significance and importance
        """
        # Look for explicit significance statements
        significance_sections = ["conclusion", "discussion", "implications"]
        
        for section_name in significance_sections:
            if section_name in sections:
                section_text = sections[section_name]
                significance = self._extract_significance_from_text(section_text)
                if significance:
                    return significance
        
        # Look for significance in abstract
        if "abstract" in sections:
            abstract_text = sections["abstract"]
            significance = self._extract_significance_from_text(abstract_text)
            if significance:
                return significance
        
        return "This work contributes to the advancement of knowledge in its respective field."
    
    def _extract_significance_from_text(self, text: str) -> str:
        """Extract significance using pattern matching"""
        if not text:
            return ""
        
        clean_text = self._clean_extracted_text(text)
        
        # Significance patterns
        significance_patterns = [
            r"(?:the\s+)?(?:significance|importance|impact|contribution)\s+(?:of\s+this\s+(?:study|work|research)\s+)?(?:is|lies\s+in|includes?)\s+([^.!?]+)",
            r"(?:this\s+(?:study|work|research)\s+)?(?:contributes?|adds?)\s+(?:to\s+)?([^.!?]*(?:understanding|knowledge|field|literature))",
            r"(?:these\s+)?(?:findings|results)\s+(?:have\s+)?(?:important\s+)?(?:implications?|significance)\s+(?:for\s+)?([^.!?]+)",
            r"(?:the\s+)?(?:practical|clinical|theoretical)\s+(?:implications?|applications?|significance)\s+(?:of\s+this\s+work\s+)?(?:include[s]?|are)\s+([^.!?]+)",
            r"(?:this\s+work\s+)?(?:advances?|improves?|enhances?)\s+(?:our\s+)?(?:understanding|knowledge)\s+(?:of\s+)?([^.!?]+)",
            r"(?:importantly|significantly|notably),?\s+(?:this\s+(?:study|work|research)\s+)?([^.!?]*(?:demonstrates?|shows?|reveals?))"
        ]
        
        for pattern in significance_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                significance = self._clean_extracted_text(match.group(1))
                if len(significance) > 20 and len(significance) < 300:
                    return significance
        
        # Look for sentences containing significance keywords
        sentences = clean_text.split('.')
        significance_keywords = [
            'significant', 'important', 'crucial', 'critical', 'valuable',
            'contribution', 'advance', 'improve', 'enhance', 'impact',
            'implications', 'applications', 'benefits', 'advantages'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 30 and len(sentence) < 200 and
                any(keyword in sentence.lower() for keyword in significance_keywords)):
                clean_sentence = self._clean_extracted_text(sentence)
                if clean_sentence:
                    return clean_sentence
        
        return ""
    
    def _extract_research_question(self, sections: Dict[str, str]) -> str:
        """
        Extract research question from introduction or abstract using regex patterns and NLP
        
        Args:
            sections: Dictionary of paper sections
            
        Returns:
            Extracted research question or meaningful fallback
        """
        # Look in introduction first
        if "introduction" in sections:
            intro_text = sections["introduction"]
            question = self._extract_research_question_from_text(intro_text)
            if question:
                return question
        
        # Fallback to abstract
        if "abstract" in sections:
            abstract_text = sections["abstract"]
            question = self._extract_research_question_from_text(abstract_text)
            if question:
                return question
        
        # Check other sections that might contain research objectives
        for section_name, section_text in sections.items():
            if any(keyword in section_name.lower() for keyword in ["objective", "aim", "purpose", "goal"]):
                question = self._extract_research_question_from_text(section_text)
                if question:
                    return question
        
        # Meaningful fallback when research questions cannot be identified
        return "Research objectives and questions require further analysis of the paper content."
    
    def _extract_theoretical_framework(self, sections: Dict[str, str]) -> str:
        """
        Extract theoretical framework for theoretical context from introduction
        
        Args:
            sections: Dictionary of paper sections
            
        Returns:
            Theoretical framework and conceptual foundation
        """
        # Look for theoretical framework in introduction
        if "introduction" in sections:
            intro_text = sections["introduction"]
            framework = self._extract_theoretical_framework_from_text(intro_text)
            if framework:
                return framework
        
        # Look for theory-related sections
        theory_sections = ["theoretical framework", "conceptual framework", "literature review", "background"]
        for section_name in theory_sections:
            if section_name in sections:
                section_text = sections[section_name]
                framework = self._extract_theoretical_framework_from_text(section_text)
                if framework:
                    return framework
        
        return "Theoretical foundation and conceptual framework are embedded within the paper."
    
    def _extract_theoretical_framework_from_text(self, text: str) -> str:
        """Extract theoretical framework using pattern matching"""
        if not text:
            return ""
        
        clean_text = self._clean_extracted_text(text)
        
        # Theoretical framework patterns
        framework_patterns = [
            r"(?:theoretical\s+framework|conceptual\s+framework|theoretical\s+foundation)\s*:?\s*([^.!?]+)",
            r"(?:based\s+on|grounded\s+in|drawing\s+(?:on|from))\s+([^.!?]*(?:theory|model|framework|approach))",
            r"(?:this\s+study\s+)?(?:builds\s+on|extends|applies)\s+([^.!?]*(?:theory|model|framework))",
            r"(?:according\s+to|following)\s+([^.!?]*(?:theory|model|framework))",
            r"(?:the\s+)?(?:theory|model|framework)\s+(?:of\s+)?([^.!?]+)\s+(?:suggests?|proposes?|states?)"
        ]
        
        for pattern in framework_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                framework = self._clean_extracted_text(match.group(1))
                if len(framework) > 20 and len(framework) < 300:
                    return framework
        
        # Look for sentences mentioning theories or models
        sentences = clean_text.split('.')
        theory_keywords = ['theory', 'model', 'framework', 'approach', 'paradigm', 'concept', 'principle']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 40 and len(sentence) < 250 and
                any(keyword in sentence.lower() for keyword in theory_keywords)):
                clean_sentence = self._clean_extracted_text(sentence)
                if clean_sentence:
                    return self._summarize_text(clean_sentence, max_length=300)
        
        return ""
    
    def _extract_methodology(self, sections: Dict[str, str]) -> str:
        """
        Extract methodology from methods/methodology sections with structured summarization
        
        Args:
            sections: Dictionary of paper sections
            
        Returns:
            Structured methodology summary with appropriate length limits
        """
        # Primary methodology sections
        method_sections = ["methods", "methodology", "materials and methods", "experimental methods"]
        
        for section_key in method_sections:
            if section_key in sections:
                method_text = sections[section_key]
                clean_method = self._clean_extracted_text(method_text)
                if clean_method and len(clean_method) > 50:
                    return self._create_structured_methodology_summary(clean_method)
        
        # Look for methodology in other sections with method-related keywords
        method_keywords = ["method", "approach", "procedure", "protocol", "technique", "design", "experimental"]
        
        for section_name, section_text in sections.items():
            if any(keyword in section_name.lower() for keyword in method_keywords):
                clean_text = self._clean_extracted_text(section_text)
                if clean_text and len(clean_text) > 50:
                    return self._create_structured_methodology_summary(clean_text)
        
        # Handle cases where methodology is described in introduction or other sections
        methodology_from_intro = self._extract_methodology_from_introduction(sections)
        if methodology_from_intro:
            return methodology_from_intro
        
        # Meaningful fallback when methodology cannot be identified
        return "Methodology details are embedded within the paper and require detailed analysis."
    
    def _extract_key_findings(self, analysis_result: AnalysisResult) -> List[str]:
        """
        Extract key findings from results, discussion, and conclusion sections
        Uses existing key_concepts from ContentAnalyzer when available
        
        Args:
            analysis_result: Content analysis results containing sections and key concepts
            
        Returns:
            List of key findings with meaningful content
        """
        findings = []
        
        # Use existing key_concepts if available (prioritize these as they're already analyzed)
        if analysis_result.key_concepts:
            # Clean and validate key concepts
            for concept in analysis_result.key_concepts[:5]:
                clean_concept = self._clean_extracted_text(concept)
                if clean_concept and len(clean_concept) > 10:
                    findings.append(clean_concept)
        
        # Extract from results section using enhanced pattern matching
        if "results" in analysis_result.sections:
            results_text = analysis_result.sections["results"]
            results_findings = self._extract_findings_with_patterns(results_text, "results")
            findings.extend(results_findings[:4])
        
        # Extract from discussion section
        if "discussion" in analysis_result.sections:
            discussion_text = analysis_result.sections["discussion"]
            discussion_findings = self._extract_findings_with_patterns(discussion_text, "discussion")
            findings.extend(discussion_findings[:3])
        
        # Extract from conclusion section
        if "conclusion" in analysis_result.sections:
            conclusion_text = analysis_result.sections["conclusion"]
            conclusion_findings = self._extract_findings_with_patterns(conclusion_text, "conclusion")
            findings.extend(conclusion_findings[:3])
        
        # Remove duplicates while preserving order
        unique_findings = []
        seen = set()
        for finding in findings:
            # Create a normalized version for duplicate detection
            normalized = re.sub(r'\s+', ' ', finding.lower().strip())
            if normalized not in seen and len(finding) > 15:
                unique_findings.append(finding)
                seen.add(normalized)
                if len(unique_findings) >= 8:  # Limit to 8 findings
                    break
        
        # Provide meaningful fallback when findings cannot be identified
        return unique_findings if unique_findings else [
            "Key findings require detailed analysis of results and conclusions",
            "Significant contributions identified in the study",
            "Novel insights presented in the research"
        ]
    
    def _extract_limitations(self, sections: Dict[str, str]) -> str:
        """
        Extract limitations to identify study limitations from discussion or conclusion
        
        Args:
            sections: Dictionary of paper sections
            
        Returns:
            Study limitations and scope restrictions
        """
        # Look for explicit limitations section first
        limitation_sections = ["limitations", "study limitations", "limitations and future work"]
        
        for section_name in limitation_sections:
            if section_name in sections:
                limitations_text = self._clean_extracted_text(sections[section_name])
                if limitations_text and len(limitations_text) > 30:
                    return self._create_structured_limitations(limitations_text)
        
        # Look in discussion section
        if "discussion" in sections:
            discussion_text = sections["discussion"]
            limitations = self._extract_limitations_from_text(discussion_text)
            if limitations:
                return limitations
        
        # Look in conclusion section
        if "conclusion" in sections:
            conclusion_text = sections["conclusion"]
            limitations = self._extract_limitations_from_text(conclusion_text)
            if limitations:
                return limitations
        
        # Look in methods section for methodological limitations
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            method_limitations = self._extract_methodological_limitations(method_text)
            if method_limitations:
                return method_limitations
        
        return "Study limitations and scope restrictions are discussed within the paper."
    
    def _create_structured_limitations(self, limitations_text: str) -> str:
        """Create structured summary of limitations"""
        # Try to identify different types of limitations
        limitations = []
        
        # Sample size limitations
        sample_limitation = self._extract_sample_limitations(limitations_text)
        if sample_limitation:
            limitations.append(f"Sample: {sample_limitation}")
        
        # Methodological limitations
        method_limitation = self._extract_method_limitations_from_text(limitations_text)
        if method_limitation:
            limitations.append(f"Methodology: {method_limitation}")
        
        # Scope limitations
        scope_limitation = self._extract_scope_limitations(limitations_text)
        if scope_limitation:
            limitations.append(f"Scope: {scope_limitation}")
        
        if limitations:
            return ". ".join(limitations) + "."
        else:
            return self._summarize_text(limitations_text, max_length=300)
    
    def _extract_sample_limitations(self, text: str) -> str:
        """Extract sample-related limitations"""
        sample_patterns = [
            r"(?:small|limited|insufficient)\s+(?:sample|population|cohort)\s+(?:size\s+)?([^.!?]*)",
            r"(?:sample\s+)?(?:size|population)\s+(?:was|is)\s+(?:small|limited|insufficient)\s*([^.!?]*)",
            r"(?:limited\s+)?(?:generalizability|external\s+validity)\s+(?:due\s+to\s+)?([^.!?]*(?:sample|population))"
        ]
        
        for pattern in sample_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                limitation = self._clean_extracted_text(match.group(1) if match.group(1) else match.group(0))
                if len(limitation) > 10 and len(limitation) < 150:
                    return limitation
        
        return ""
    
    def _extract_method_limitations_from_text(self, text: str) -> str:
        """Extract methodological limitations"""
        method_patterns = [
            r"(?:methodological\s+)?(?:limitation[s]?|weakness|constraint)\s+(?:include[s]?|is|are)\s+([^.!?]+)",
            r"(?:cross-sectional|observational|retrospective)\s+(?:design|nature|study)\s+([^.!?]*)",
            r"(?:lack\s+of|absence\s+of|no)\s+(?:control\s+group|randomization|blinding)\s*([^.!?]*)"
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                limitation = self._clean_extracted_text(match.group(1))
                if len(limitation) > 10 and len(limitation) < 150:
                    return limitation
        
        return ""
    
    def _extract_scope_limitations(self, text: str) -> str:
        """Extract scope-related limitations"""
        scope_patterns = [
            r"(?:limited\s+to|restricted\s+to|focused\s+on)\s+([^.!?]+)",
            r"(?:scope|focus)\s+(?:was|is)\s+(?:limited\s+to|restricted\s+to)\s+([^.!?]+)",
            r"(?:only|solely)\s+(?:examined|investigated|studied|analyzed)\s+([^.!?]+)"
        ]
        
        for pattern in scope_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                limitation = self._clean_extracted_text(match.group(1))
                if len(limitation) > 10 and len(limitation) < 150:
                    return limitation
        
        return ""
    
    def _extract_methodological_limitations(self, method_text: str) -> str:
        """Extract limitations from methodology section"""
        if not method_text:
            return ""
        
        # Look for limitation indicators in methods
        limitation_indicators = [
            'limitation', 'constraint', 'restriction', 'assumption',
            'unable to', 'could not', 'did not include', 'excluded'
        ]
        
        sentences = method_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 30 and
                any(indicator in sentence.lower() for indicator in limitation_indicators)):
                clean_sentence = self._clean_extracted_text(sentence)
                if clean_sentence:
                    return clean_sentence
        
        return ""
    
    def _extract_practical_applications(self, sections: Dict[str, str]) -> List[str]:
        """
        Extract practical applications for real-world applications from discussion or conclusion
        
        Args:
            sections: Dictionary of paper sections
            
        Returns:
            List of practical applications and real-world implementations
        """
        applications = []
        
        # Look in discussion section
        if "discussion" in sections:
            discussion_text = sections["discussion"]
            applications.extend(self._extract_applications_with_patterns(discussion_text))
        
        # Look in conclusion section
        if "conclusion" in sections:
            conclusion_text = sections["conclusion"]
            applications.extend(self._extract_applications_with_patterns(conclusion_text))
        
        # Look in implications section
        if "implications" in sections:
            implications_text = sections["implications"]
            applications.extend(self._extract_applications_with_patterns(implications_text))
        
        # Look in abstract for applications
        if "abstract" in sections and len(applications) < 3:
            abstract_text = sections["abstract"]
            applications.extend(self._extract_applications_with_patterns(abstract_text))
        
        # Remove duplicates while preserving order
        unique_applications = []
        seen = set()
        for app in applications:
            normalized = re.sub(r'\s+', ' ', app.lower().strip())
            if normalized not in seen and len(app) > 15:
                unique_applications.append(app)
                seen.add(normalized)
                if len(unique_applications) >= 5:
                    break
        
        return unique_applications if unique_applications else [
            "Real-world applications and implementations",
            "Clinical or industrial relevance",
            "Policy and decision-making implications"
        ]
    
    def _extract_applications_with_patterns(self, text: str) -> List[str]:
        """Extract applications using enhanced pattern matching"""
        if not text:
            return []
        
        applications = []
        clean_text = self._clean_extracted_text(text)
        
        # Enhanced application patterns
        application_patterns = [
            r"(?:practical\s+)?(?:applications?|uses?|implementations?)\s+(?:of\s+this\s+(?:work|study|research)\s+)?(?:include[s]?|are|could\s+be)\s+([^.!?]+)",
            r"(?:this\s+(?:work|study|research|approach|method)\s+)?(?:can\s+be|could\s+be|may\s+be)\s+(?:used|applied|implemented|employed)\s+(?:in|for|to)\s+([^.!?]+)",
            r"(?:clinical|industrial|commercial|practical)\s+(?:applications?|uses?|implementations?|relevance)\s+(?:include[s]?|are|of\s+this\s+work)\s*:?\s*([^.!?]*)",
            r"(?:these\s+)?(?:findings|results)\s+(?:have\s+)?(?:implications?|applications?)\s+(?:for|in)\s+([^.!?]+)",
            r"(?:potential\s+)?(?:applications?|uses?)\s+(?:in|for)\s+([^.!?]*(?:healthcare|medicine|industry|education|policy))",
            r"(?:could\s+be\s+)?(?:useful|beneficial|valuable)\s+(?:for|in|to)\s+([^.!?]+)",
            r"(?:this\s+approach\s+)?(?:enables?|allows?|facilitates?)\s+([^.!?]+)",
            r"(?:practitioners?|clinicians?|professionals?)\s+(?:can|could|may)\s+(?:use|apply|implement)\s+(?:this|these\s+findings?)\s+(?:to|for)\s+([^.!?]+)"
        ]
        
        for pattern in application_patterns:
            matches = re.finditer(pattern, clean_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                app = self._clean_extracted_text(match.group(1))
                if self._is_valid_application(app):
                    applications.append(app)
                    if len(applications) >= 5:
                        break
            if len(applications) >= 5:
                break
        
        # If no pattern matches, look for sentences with application keywords
        if not applications:
            applications.extend(self._extract_applications_by_keywords(clean_text))
        
        return applications[:5]
    
    def _is_valid_application(self, application: str) -> bool:
        """Validate if extracted text is a meaningful application"""
        if not application or len(application) < 15 or len(application) > 200:
            return False
        
        # Check for application-related content
        application_indicators = [
            'clinical', 'medical', 'healthcare', 'treatment', 'diagnosis',
            'industrial', 'manufacturing', 'production', 'commercial',
            'educational', 'training', 'teaching', 'learning',
            'policy', 'decision', 'management', 'planning',
            'practice', 'implementation', 'deployment', 'use'
        ]
        
        app_lower = application.lower()
        has_application_content = any(indicator in app_lower for indicator in application_indicators)
        
        # Avoid generic or incomplete applications
        avoid_patterns = [
            r'^(?:the|this|that|these|those|it|they)\s+(?:is|are|was|were)\s*$',
            r'^(?:and|but|however|therefore|thus|hence)\s+',
            r'^\s*[,;:]\s*'
        ]
        
        for avoid_pattern in avoid_patterns:
            if re.match(avoid_pattern, application, re.IGNORECASE):
                return False
        
        return has_application_content or len(application) > 40
    
    def _extract_applications_by_keywords(self, text: str) -> List[str]:
        """Extract applications using keyword-based sentence analysis"""
        applications = []
        sentences = text.split('.')
        
        application_keywords = [
            'application', 'use', 'implementation', 'practice', 'clinical',
            'industrial', 'commercial', 'practical', 'real-world', 'deployment'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 30 and len(sentence) < 200 and
                any(keyword in sentence.lower() for keyword in application_keywords)):
                
                clean_sentence = self._clean_extracted_text(sentence)
                if self._is_valid_application(clean_sentence):
                    applications.append(clean_sentence)
                    if len(applications) >= 3:
                        break
        
        return applications
    
    # Focus-specific data extraction methods for theory template variables
    def _extract_theory_specific_data(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Extract theory-focused data for theory template variables
        Maps theory-specific content to template variables like theoretical_proposition, equations, assumptions
        
        Args:
            analysis_result: Content analysis results
            
        Returns:
            Dictionary with theory-specific template variables
        """
        theory_data = {}
        sections = analysis_result.sections
        
        # Extract equations and mathematical models
        theory_data["equations"] = analysis_result.equations[:5] if analysis_result.equations else []
        
        # Extract theoretical propositions from introduction or theory sections
        theory_data["theoretical_proposition"] = self._extract_theoretical_propositions(sections)
        
        # Extract assumptions from methods or introduction
        theory_data["assumptions"] = self._extract_theoretical_assumptions(sections)
        
        # Extract mathematical models information
        theory_data["mathematical_models"] = self._extract_mathematical_models_info(sections, analysis_result.equations)
        
        # Extract theoretical framework details
        theory_data["theoretical_framework_details"] = self._extract_theoretical_framework_details(sections)
        
        # Extract theoretical contributions and novelty
        theory_data["theoretical_contributions"] = self._extract_theoretical_contributions(sections)
        
        # Extract proofs and derivations if available
        theory_data["proofs"] = self._extract_proofs_and_derivations(sections)
        
        # Extract theoretical validation approaches
        theory_data["theoretical_validation"] = self._extract_theoretical_validation(sections)
        
        return theory_data
    
    def _extract_research_specific_data(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Extract research-focused data for research template variables
        Maps research-specific content to template variables like study_design, participants, measures
        
        Args:
            analysis_result: Content analysis results
            
        Returns:
            Dictionary with research-specific template variables
        """
        research_data = {}
        sections = analysis_result.sections
        
        # Extract study design and experimental setup
        research_data["study_design"] = self._extract_study_design_detailed(sections)
        
        # Extract participants or sample information
        research_data["participants"] = self._extract_participants_detailed(sections)
        
        # Extract measures and instruments
        research_data["measures"] = self._extract_measures_and_instruments(sections)
        
        # Extract experimental procedures
        research_data["experimental_procedures"] = self._extract_experimental_procedures(sections)
        
        # Extract data collection methods
        research_data["data_collection"] = self._extract_data_collection_methods(sections)
        
        # Extract statistical analysis approaches
        research_data["statistical_analysis"] = self._extract_statistical_analysis(sections)
        
        # Extract research hypotheses
        research_data["hypotheses"] = self._extract_research_hypotheses(sections)
        
        # Extract validation and reliability measures
        research_data["validation_measures"] = self._extract_validation_measures(sections)
        
        return research_data
    
    def _extract_method_specific_data(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Extract method-focused data for methodology template variables
        Maps method-specific content to template variables like experimental_design, procedures, validation
        
        Args:
            analysis_result: Content analysis results
            
        Returns:
            Dictionary with method-specific template variables
        """
        method_data = {}
        sections = analysis_result.sections
        
        # Extract experimental design and setup
        method_data["experimental_design"] = self._extract_experimental_design_detailed(sections)
        
        # Extract detailed procedures
        method_data["procedures"] = self._extract_detailed_procedures(sections)
        
        # Extract validation and verification approaches
        method_data["validation"] = self._extract_method_validation(sections)
        
        # Extract equipment and materials
        method_data["equipment"] = self._extract_equipment_and_materials(sections)
        
        # Extract protocol details
        method_data["protocol"] = self._extract_protocol_details(sections)
        
        # Extract quality control measures
        method_data["quality_control"] = self._extract_quality_control_measures(sections)
        
        # Extract method advantages and innovations
        method_data["advantages"] = self._extract_method_advantages(sections, analysis_result)
        
        # Extract method limitations and considerations
        method_data["limitations"] = self._extract_method_limitations(sections)
        
        # Extract performance metrics
        method_data["performance_metrics"] = self._extract_performance_metrics(sections)
        
        return method_data
    
    def _extract_review_specific_data(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Extract review-focused data for literature review template variables
        Maps review-specific content to template variables like scope, key_themes, research_gaps
        
        Args:
            analysis_result: Content analysis results
            
        Returns:
            Dictionary with review-specific template variables
        """
        review_data = {}
        sections = analysis_result.sections
        
        # Extract review scope and inclusion criteria
        review_data["scope"] = self._extract_review_scope(sections)
        
        # Extract key themes and patterns from content
        review_data["key_themes"] = self._extract_review_themes(sections, analysis_result.key_concepts)
        
        # Extract research gaps and future directions
        review_data["research_gaps"] = self._extract_identified_research_gaps(sections)
        
        # Extract literature synthesis approach
        review_data["synthesis_approach"] = self._extract_synthesis_approach(sections)
        
        # Extract inclusion and exclusion criteria
        review_data["inclusion_criteria"] = self._extract_inclusion_criteria(sections)
        
        # Extract search strategy
        review_data["search_strategy"] = self._extract_search_strategy(sections)
        
        # Extract study characteristics
        review_data["study_characteristics"] = self._extract_study_characteristics(sections)
        
        # Extract quality assessment approach
        review_data["quality_assessment"] = self._extract_quality_assessment(sections)
        
        # Extract main conclusions from synthesis
        review_data["synthesis_conclusions"] = self._extract_synthesis_conclusions(sections)
        
        return review_data
    
    # Additional template variable extraction methods
    def _extract_conclusions(self, sections: Dict[str, str]) -> str:
        """Extract conclusions from conclusion section"""
        if "conclusion" in sections:
            conclusion_text = self._clean_extracted_text(sections["conclusion"])
            if conclusion_text and len(conclusion_text) > 50:
                return self._summarize_text(conclusion_text, max_length=400)
        
        return "Primary conclusions and their implications for the field"
    
    def _extract_new_knowledge(self, sections: Dict[str, str]) -> str:
        """Extract new knowledge contribution"""
        if "conclusion" in sections:
            conclusion_text = self._clean_extracted_text(sections["conclusion"])
            if conclusion_text and len(conclusion_text) > 50:
                return self._summarize_text(conclusion_text, max_length=300)
        
        return "What novel insights does this paper contribute?"
    
    def _extract_theoretical_connections(self, sections: Dict[str, str]) -> str:
        """Extract theoretical framework connections"""
        if "introduction" in sections:
            intro_text = self._clean_extracted_text(sections["introduction"])
            if intro_text and len(intro_text) > 50:
                return self._summarize_text(intro_text, max_length=300)
        
        return "How does this relate to existing theoretical frameworks?"
    
    def _extract_methodological_insights(self, sections: Dict[str, str]) -> str:
        """Extract methodological insights"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            clean_method = self._clean_extracted_text(method_text)
            if clean_method and len(clean_method) > 50:
                return self._summarize_text(clean_method, max_length=300)
        
        return "What methodological approaches can be applied?"
    
    def _extract_research_gaps(self, sections: Dict[str, str]) -> str:
        """Extract research gaps"""
        if "discussion" in sections:
            discussion_text = self._clean_extracted_text(sections["discussion"])
            if discussion_text and len(discussion_text) > 50:
                return self._summarize_text(discussion_text, max_length=300)
        
        return "What gaps in knowledge does this study reveal?"
    
    def _extract_research_impact(self, sections: Dict[str, str]) -> str:
        """Extract research impact"""
        if "conclusion" in sections:
            conclusion_text = self._clean_extracted_text(sections["conclusion"])
            if conclusion_text and len(conclusion_text) > 50:
                return self._summarize_text(conclusion_text, max_length=300)
        
        return "How might this change future research approaches or hypotheses?"
    
    def _extract_follow_up_questions(self, sections: Dict[str, str]) -> List[str]:
        """Extract follow-up questions"""
        return [
            "What additional studies are needed?",
            "How can these findings be extended?",
            "What methodological improvements could be made?"
        ]
    
    def _extract_implementation(self, sections: Dict[str, str]) -> str:
        """Extract implementation considerations"""
        if "discussion" in sections:
            discussion_text = self._clean_extracted_text(sections["discussion"])
            if discussion_text and len(discussion_text) > 50:
                return self._summarize_text(discussion_text, max_length=300)
        
        return "Factors to consider for practical implementation"
    
    def _extract_scalability(self, sections: Dict[str, str]) -> str:
        """Extract scalability information"""
        if "discussion" in sections:
            discussion_text = self._clean_extracted_text(sections["discussion"])
            if discussion_text and len(discussion_text) > 50:
                return self._summarize_text(discussion_text, max_length=300)
        
        return "How broadly applicable are these findings?"
    
    def _extract_related_work(self, sections: Dict[str, str]) -> str:
        """Extract related work information"""
        if "introduction" in sections:
            intro_text = self._clean_extracted_text(sections["introduction"])
            if intro_text and len(intro_text) > 50:
                return self._summarize_text(intro_text, max_length=400)
        
        return "How this work builds on or relates to previous research"
    
    def _extract_competing_approaches(self, sections: Dict[str, str]) -> str:
        """Extract competing approaches"""
        if "introduction" in sections:
            intro_text = self._clean_extracted_text(sections["introduction"])
            if intro_text and len(intro_text) > 50:
                return self._summarize_text(intro_text, max_length=300)
        
        return "Alternative methods or theories in this area"
    
    def _extract_future_work(self, sections: Dict[str, str]) -> List[str]:
        """Extract future work directions"""
        return [
            "Suggested extensions and improvements",
            "Unexplored applications",
            "Methodological developments needed"
        ]
    
    # Balanced template specific extraction methods
    def _extract_literature_context(self, sections: Dict[str, str]) -> str:
        """Extract literature context"""
        if "introduction" in sections:
            intro_text = self._clean_extracted_text(sections["introduction"])
            if intro_text and len(intro_text) > 50:
                return self._summarize_text(intro_text, max_length=400)
        
        return "How this work builds on and relates to existing research"
    
    def _extract_research_design(self, sections: Dict[str, str]) -> str:
        """Extract research design"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            clean_method = self._clean_extracted_text(method_text)
            if clean_method and len(clean_method) > 50:
                return self._summarize_text(clean_method, max_length=300)
        
        return "Overall study design and methodological approach"
    
    def _extract_methods_list(self, sections: Dict[str, str]) -> List[str]:
        """Extract methods as a list"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            if method_text:
                # Try to extract method items
                methods = self._extract_method_items_from_text(method_text)
                if methods:
                    return methods
        
        return [
            "Primary experimental or analytical methods",
            "Data collection procedures",
            "Analysis techniques employed"
        ]
    
    def _extract_study_parameters(self, sections: Dict[str, str]) -> str:
        """Extract study parameters"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            clean_method = self._clean_extracted_text(method_text)
            if clean_method and len(clean_method) > 50:
                return self._summarize_text(clean_method, max_length=300)
        
        return "Key variables, conditions, and measurement parameters"
    
    def _extract_primary_results(self, sections: Dict[str, str]) -> str:
        """Extract primary results"""
        if "results" in sections:
            results_text = self._clean_extracted_text(sections["results"])
            if results_text and len(results_text) > 50:
                return self._summarize_text(results_text, max_length=400)
        
        return "Main findings and quantitative results"
    
    def _extract_supporting_evidence(self, sections: Dict[str, str]) -> List[str]:
        """Extract supporting evidence"""
        if "results" in sections:
            results_text = sections["results"]
            evidence = self._extract_findings_from_text(results_text)
            if evidence:
                return evidence[:3]
        
        return [
            "Secondary findings that support main conclusions",
            "Statistical validation and significance",
            "Reproducibility and consistency measures"
        ]
    
    def _extract_data_analysis(self, sections: Dict[str, str]) -> str:
        """Extract data analysis insights"""
        if "results" in sections:
            results_text = self._clean_extracted_text(sections["results"])
            if results_text and len(results_text) > 50:
                return self._summarize_text(results_text, max_length=400)
        
        return "Key insights from data analysis and interpretation"
    
    def _extract_theoretical_implications(self, sections: Dict[str, str]) -> str:
        """Extract theoretical implications"""
        if "discussion" in sections:
            discussion_text = self._clean_extracted_text(sections["discussion"])
            if discussion_text and len(discussion_text) > 50:
                return self._summarize_text(discussion_text, max_length=400)
        
        return "How findings advance theoretical understanding"
    
    def _extract_methodological_contributions(self, sections: Dict[str, str]) -> str:
        """Extract methodological contributions"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            clean_method = self._clean_extracted_text(method_text)
            if clean_method and len(clean_method) > 50:
                return self._summarize_text(clean_method, max_length=300)
        
        return "Advances in research methods or analytical approaches"
    
    def _extract_strengths(self, sections: Dict[str, str]) -> List[str]:
        """Extract study strengths"""
        return [
            "Methodological rigor and innovation",
            "Comprehensive analysis and validation",
            "Clear practical relevance"
        ]
    
    def _extract_future_research(self, sections: Dict[str, str]) -> str:
        """Extract future research needs"""
        if "conclusion" in sections:
            conclusion_text = self._clean_extracted_text(sections["conclusion"])
            if conclusion_text and len(conclusion_text) > 50:
                return self._summarize_text(conclusion_text, max_length=300)
        
        return "Identified gaps and suggested future research directions"
    
    def _extract_field_advancement(self, sections: Dict[str, str]) -> str:
        """Extract field advancement information"""
        if "conclusion" in sections:
            conclusion_text = self._clean_extracted_text(sections["conclusion"])
            if conclusion_text and len(conclusion_text) > 50:
                return self._summarize_text(conclusion_text, max_length=300)
        
        return "How this work advances the broader research field"
    
    def _extract_cross_disciplinary(self, sections: Dict[str, str]) -> str:
        """Extract cross-disciplinary relevance"""
        if "discussion" in sections:
            discussion_text = self._clean_extracted_text(sections["discussion"])
            if discussion_text and len(discussion_text) > 50:
                return self._summarize_text(discussion_text, max_length=300)
        
        return "Relevance to other research areas or disciplines"
    
    def _extract_personal_relevance(self, sections: Dict[str, str]) -> str:
        """Extract personal research relevance"""
        return "How this paper relates to your current research interests"
    
    def _extract_key_takeaways(self, sections: Dict[str, str]) -> str:
        """Extract key takeaways"""
        if "conclusion" in sections:
            conclusion_text = self._clean_extracted_text(sections["conclusion"])
            if conclusion_text and len(conclusion_text) > 50:
                return self._summarize_text(conclusion_text, max_length=300)
        
        return "Most important insights and lessons learned"
    
    def _extract_action_items(self, sections: Dict[str, str]) -> List[str]:
        """Extract action items"""
        return [
            "Specific methods to investigate further",
            "Concepts to incorporate into current research",
            "Follow-up papers to read"
        ]
    
    def _extract_method_items_from_text(self, text: str) -> List[str]:
        """Extract method items from methodology text"""
        if not text:
            return []
        
        methods = []
        
        # Look for numbered or bulleted lists
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Check for list indicators
            if (line.startswith(('1.', '2.', '3.', '-', '•', '*')) or 
                re.match(r'^\d+\)', line) or
                re.match(r'^\([a-z]\)', line)):
                clean_line = re.sub(r'^[\d\.\)\-\*\•\s\(\)a-z]+', '', line).strip()
                if len(clean_line) > 15:
                    methods.append(clean_line)
                    if len(methods) >= 5:
                        break
        
        return methods
    
    # Text processing utility methods
    def _clean_extracted_text(self, text: str) -> str:
        """
        Enhanced text cleaning and normalization for PDF extraction artifacts
        Handles common PDF extraction issues and improves text quality
        """
        if not text:
            return ""
        
        # Remove common PDF extraction artifacts
        text = re.sub(r'\x0c|\f', ' ', text)  # Form feed characters
        text = re.sub(r'[\u2018\u2019]', "'", text)  # Smart quotes
        text = re.sub(r'[\u201c\u201d]', '"', text)  # Smart double quotes
        text = re.sub(r'\u2013|\u2014', '-', text)  # En/em dashes
        text = re.sub(r'\u2026', '...', text)  # Ellipsis
        
        # Fix missing spaces (common PDF extraction issue)
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'([a-z])(\d)', r'\1 \2', text)
        text = re.sub(r'(\d)([a-z])', r'\1 \2', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'(\w)([,.;:])', r'\1\2', text)  # Remove space before punctuation
        text = re.sub(r'([,.;:])(\w)', r'\1 \2', text)  # Add space after punctuation
        
        # Handle hyphenated line breaks
        text = re.sub(r'-\s*\n\s*', '', text)  # Remove hyphenated line breaks
        text = re.sub(r'\n\s*', ' ', text)  # Replace line breaks with spaces
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove PDF page artifacts
        text = re.sub(r'\b(?:page|p\.)\s*\d+\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b\d{4,}\b', '', text)  # Remove long numbers (likely page refs)
        text = re.sub(r'^\d+\s*$', '', text)  # Remove standalone numbers
        
        # Remove empty parentheses and brackets
        text = re.sub(r'\(\s*\)', '', text)
        text = re.sub(r'\[\s*\]', '', text)
        
        # Clean up multiple periods and spaces
        text = re.sub(r'\.{2,}', '...', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _summarize_text(self, text: str, max_length: int = 400) -> str:
        """
        Enhanced text summarization with intelligent truncation
        Preserves sentence boundaries and important content
        """
        if not text or len(text) <= max_length:
            return text
        
        # Clean the text first
        text = self._clean_extracted_text(text)
        
        # Try to identify key sentences based on content indicators
        sentences = re.split(r'[.!?]+', text)
        summary_sentences = []
        current_length = 0
        
        # Prioritize sentences with key indicators
        key_indicators = [
            'found', 'showed', 'demonstrated', 'revealed', 'indicates', 'suggests',
            'concluded', 'results show', 'significantly', 'important', 'novel',
            'first time', 'propose', 'develop', 'improve', 'enhance'
        ]
        
        # First pass: collect sentences with key indicators
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_with_period = sentence + '.'
            sentence_length = len(sentence_with_period)
            
            # Check if adding this sentence would exceed limit
            if current_length + sentence_length > max_length:
                break
                
            # Prioritize sentences with key indicators
            if any(indicator in sentence.lower() for indicator in key_indicators):
                summary_sentences.append(sentence_with_period)
                current_length += sentence_length + 1  # +1 for space
        
        # Second pass: fill remaining space with other sentences if needed
        if current_length < max_length * 0.6:  # If less than 60% filled
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                sentence_with_period = sentence + '.'
                sentence_length = len(sentence_with_period)
                
                # Skip if already included
                if sentence_with_period in summary_sentences:
                    continue
                    
                # Check if adding this sentence would exceed limit
                if current_length + sentence_length > max_length:
                    break
                    
                summary_sentences.append(sentence_with_period)
                current_length += sentence_length + 1
        
        # Join summary sentences
        if summary_sentences:
            summary = ' '.join(summary_sentences)
            if len(summary) <= max_length:
                return summary
        
        # Fallback to smart truncation at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.7:  # Keep at least 70% of content
            return text[:last_period + 1]
        else:
            # Try other sentence endings
            for ending in ['!', '?', ';']:
                last_ending = truncated.rfind(ending)
                if last_ending > max_length * 0.7:
                    return text[:last_ending + 1]
            
            return truncated.rstrip() + "..."
    
    def _create_structured_methodology_summary(self, method_text: str) -> str:
        """
        Create a structured summary of methodology with appropriate length limits
        
        Args:
            method_text: Raw methodology text
            
        Returns:
            Structured methodology summary
        """
        # Extract key methodological components
        components = []
        
        # Study design
        design = self._extract_study_design(method_text)
        if design:
            components.append(f"**Study Design**: {design}")
        
        # Data collection methods
        data_collection = self._extract_data_collection_methods(method_text)
        if data_collection:
            components.append(f"**Data Collection**: {data_collection}")
        
        # Analysis methods
        analysis = self._extract_analysis_methods(method_text)
        if analysis:
            components.append(f"**Analysis**: {analysis}")
        
        # Participants/samples
        participants = self._extract_participants_info(method_text)
        if participants:
            components.append(f"**Participants/Samples**: {participants}")
        
        # If we have structured components, use them
        if components:
            structured_summary = ". ".join(components)
            if len(structured_summary) <= 500:
                return structured_summary
            else:
                # Truncate while keeping structure
                return structured_summary[:500] + "..."
        
        # Fallback to general summarization
        return self._summarize_text(method_text, max_length=500)
    
    def _extract_study_design(self, text: str) -> str:
        """Extract study design information"""
        design_patterns = [
            r"(?:study\s+)?design[:\s]*([^.!?]+)",
            r"(?:experimental|observational|cross-sectional|longitudinal|randomized|controlled)\s+(?:study|trial|design|approach)",
            r"(?:we\s+)?(?:used|employed|adopted)\s+(?:a|an)\s+([^.!?]*(?:design|approach|method))",
            r"(?:this\s+)?(?:study|research)\s+(?:used|employed|adopted|followed)\s+(?:a|an)\s+([^.!?]+)"
        ]
        
        for pattern in design_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                design = self._clean_extracted_text(match.group(1) if match.lastindex else match.group(0))
                if len(design) > 10 and len(design) < 150:
                    return design
        
        return ""
    
    def _extract_data_collection_methods(self, text: str) -> str:
        """Extract data collection methods"""
        collection_patterns = [
            r"data\s+(?:were|was)\s+collected\s+(?:using|through|via|by)\s+([^.!?]+)",
            r"(?:we\s+)?collected\s+data\s+(?:using|through|via|by)\s+([^.!?]+)",
            r"(?:measurements|observations|surveys|interviews)\s+(?:were|was)\s+(?:conducted|performed|carried out)\s+([^.!?]*)",
            r"(?:using|through|via)\s+([^.!?]*(?:questionnaire|survey|interview|measurement|observation|instrument))"
        ]
        
        for pattern in collection_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                method = self._clean_extracted_text(match.group(1))
                if len(method) > 10 and len(method) < 150:
                    return method
        
        return ""
    
    def _extract_analysis_methods(self, text: str) -> str:
        """Extract analysis methods"""
        analysis_patterns = [
            r"(?:data\s+)?(?:were|was)\s+analyzed\s+(?:using|with|by)\s+([^.!?]+)",
            r"(?:statistical\s+)?analysis\s+(?:was|were)\s+(?:performed|conducted|carried out)\s+(?:using|with)\s+([^.!?]+)",
            r"(?:we\s+)?(?:used|employed|applied)\s+([^.!?]*(?:analysis|test|method|software|package))",
            r"(?:SPSS|R|Python|MATLAB|SAS|Stata)\s+(?:was|were)\s+used\s+(?:for|to)\s+([^.!?]+)"
        ]
        
        for pattern in analysis_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                analysis = self._clean_extracted_text(match.group(1))
                if len(analysis) > 10 and len(analysis) < 150:
                    return analysis
        
        return ""
    
    def _extract_participants_info(self, text: str) -> str:
        """Extract participants or sample information"""
        participant_patterns = [
            r"(?:participants|subjects|patients|samples)\s+(?:included|consisted of|were|was)\s+([^.!?]+)",
            r"(?:a\s+total\s+of\s+)?(\d+)\s+(?:participants|subjects|patients|samples)",
            r"(?:the\s+)?(?:study\s+)?(?:population|sample|cohort)\s+(?:included|consisted of|comprised)\s+([^.!?]+)",
            r"(?:inclusion\s+criteria|participants\s+were\s+selected)\s+([^.!?]+)"
        ]
        
        for pattern in participant_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                participants = self._clean_extracted_text(match.group(1))
                if len(participants) > 5 and len(participants) < 150:
                    return participants
        
        return ""
    
    def _extract_methodology_from_introduction(self, sections: Dict[str, str]) -> str:
        """Extract methodology information from introduction when methods section is not available"""
        if "introduction" not in sections:
            return ""
        
        intro_text = sections["introduction"]
        
        # Look for methodology-related sentences in introduction
        method_indicators = [
            "method", "approach", "technique", "procedure", "protocol",
            "analysis", "measured", "calculated", "performed", "conducted",
            "used", "applied", "implemented", "developed", "employed"
        ]
        
        sentences = intro_text.split('.')
        method_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 30 and 
                any(indicator in sentence.lower() for indicator in method_indicators)):
                clean_sentence = self._clean_extracted_text(sentence)
                if clean_sentence:
                    method_sentences.append(clean_sentence)
                    if len(method_sentences) >= 3:
                        break
        
        if method_sentences:
            methodology = '. '.join(method_sentences) + '.'
            return self._summarize_text(methodology, max_length=400)
        
        return ""

    def _extract_research_question_from_text(self, text: str) -> str:
        """
        Extract research question using comprehensive regex patterns and NLP
        
        Args:
            text: Text to extract research question from
            
        Returns:
            Extracted research question or empty string if not found
        """
        if not text:
            return ""
        
        # Clean text first
        clean_text = self._clean_extracted_text(text)
        
        # Comprehensive research question patterns
        question_patterns = [
            # Direct research question statements
            r"research question[s]?\s*(?:is|are|include[s]?)?\s*:?\s*([^.!?]+)",
            r"(?:the\s+)?(?:main|primary|central|key)\s+research\s+question[s]?\s*(?:is|are)?\s*:?\s*([^.!?]+)",
            r"research\s+(?:problem|issue|inquiry)\s*(?:is|was)?\s*:?\s*([^.!?]+)",
            
            # Objective and aim patterns
            r"(?:the\s+)?(?:main\s+)?(?:purpose|objective|goal|aim)[s]?\s+(?:of\s+this\s+study\s+)?(?:is|was|are|were)\s+(?:to\s+)?([^.!?]+)",
            r"this\s+(?:study|research|work|paper)\s+(?:aims|seeks|attempts|tries)\s+(?:to\s+)?([^.!?]+)",
            r"we\s+(?:aim|seek|attempt|try|investigate|examine|explore|study|analyze)\s+(?:to\s+)?([^.!?]+)",
            r"our\s+(?:aim|goal|objective|purpose)\s+(?:is|was)\s+(?:to\s+)?([^.!?]+)",
            
            # Investigation patterns
            r"(?:to\s+)?(?:investigate|examine|explore|study|analyze|determine|assess|evaluate)\s+(?:whether|how|what|why|when|where)\s+([^.!?]+)",
            r"(?:the\s+)?(?:question|issue|problem)\s+(?:addressed|investigated|examined)\s+(?:in\s+this\s+study\s+)?(?:is|was)\s*:?\s*([^.!?]+)",
            
            # Hypothesis patterns
            r"(?:we\s+)?(?:hypothesize|propose|suggest)\s+that\s+([^.!?]+)",
            r"(?:the\s+)?(?:hypothesis|proposition)\s+(?:is|was)\s+that\s+([^.!?]+)",
            
            # Question word patterns
            r"(?:specifically|particularly),?\s*(?:we\s+)?(?:ask|question|wonder)\s*:?\s*([^.!?]+)",
            r"(?:the\s+)?(?:key|main|central)\s+question\s+(?:is|was)\s*:?\s*([^.!?]+)"
        ]
        
        for pattern in question_patterns:
            matches = re.finditer(pattern, clean_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                question = self._clean_extracted_text(match.group(1))
                if len(question) > 15 and len(question) < 300:  # Meaningful length range
                    # Additional validation - should contain meaningful content
                    if any(word in question.lower() for word in ['how', 'what', 'why', 'whether', 'when', 'where', 'which', 'effect', 'impact', 'relationship', 'influence', 'role', 'factor']):
                        return question.strip()
                    elif len(question) > 30:  # Longer questions might be valid even without question words
                        return question.strip()
        
        # Handle cases where research questions are implicit or embedded
        # Look for sentences that describe what the study does
        implicit_patterns = [
            r"this\s+(?:study|research|work|paper)\s+(?:focuses\s+on|deals\s+with|addresses|tackles)\s+([^.!?]+)",
            r"(?:the\s+)?(?:focus|emphasis)\s+(?:of\s+this\s+study\s+)?(?:is|was)\s+(?:on\s+)?([^.!?]+)",
            r"(?:we\s+)?(?:focus\s+on|concentrate\s+on|examine|investigate)\s+([^.!?]+)",
            r"(?:the\s+)?(?:present|current)\s+study\s+(?:examines|investigates|explores|analyzes)\s+([^.!?]+)"
        ]
        
        for pattern in implicit_patterns:
            matches = re.finditer(pattern, clean_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                question = self._clean_extracted_text(match.group(1))
                if len(question) > 20 and len(question) < 250:
                    return f"This study focuses on {question.strip()}"
        
        return ""
    
    def _extract_limitations_from_text(self, text: str) -> str:
        """Extract limitations from text using pattern matching"""
        if not text:
            return ""
        
        # Look for limitation indicators
        limitation_patterns = [
            r"limitation[s]?\s*(?:of this study\s*)?(?:include[s]?|are|is)\s*([^.]+)",
            r"(?:however|nevertheless|despite),?\s*([^.]*limitation[^.]*)",
            r"(?:one|a|the)\s+limitation\s+(?:of this study\s+)?(?:is|was)\s+([^.]+)"
        ]
        
        for pattern in limitation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                limitation = self._clean_extracted_text(match.group(1))
                if len(limitation) > 20:  # Meaningful length
                    return limitation
        
        return ""
    
    def _extract_applications_from_text(self, text: str) -> List[str]:
        """Extract practical applications from text"""
        if not text:
            return []
        
        applications = []
        
        # Application indicators
        app_patterns = [
            r"(?:practical\s+)?application[s]?\s*(?:include[s]?|are|is)\s*([^.]+)",
            r"(?:can be|could be|may be)\s+(?:used|applied|implemented)\s+(?:in|for|to)\s+([^.]+)",
            r"(?:clinical|industrial|commercial)\s+(?:use[s]?|application[s]?|implementation[s]?)\s*([^.]*)"
        ]
        
        for pattern in app_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                app = self._clean_extracted_text(match.group(1))
                if len(app) > 15:  # Meaningful length
                    applications.append(app)
                    if len(applications) >= 3:
                        break
        
        return applications
    
    def apply_template(self, template_name: str, content: Dict) -> str:
        """
        Apply Jinja2 template to content - implementation of NoteGeneratorInterface
        
        This method provides direct template application functionality for the interface.
        For full note generation with content extraction and template selection, use generate_note().
        
        Args:
            template_name: Name of Jinja2 template to apply (e.g., 'research', 'theory', 'balanced')
            content: Content dictionary with template variables for rendering
            
        Returns:
            Rendered template as markdown string
            
        Raises:
            NoteGenerationError: If template loading or rendering fails
        """
        try:
            template = self.template_processor.load_template(template_name)
            return self.template_processor.render_template(template, content)
        except TemplateError as e:
            raise NoteGenerationError(f"Template application failed: {e}")
    
    def format_citations(self, metadata: PaperMetadata) -> str:
        """
        Format citation information - implementation of NoteGeneratorInterface
        
        Creates properly formatted academic citations from paper metadata.
        Used both in template rendering and standalone citation formatting.
        
        Args:
            metadata: Paper metadata containing authors, title, journal, etc.
            
        Returns:
            Formatted citation string in academic format
        """
        # Create basic citation format
        authors_str = ", ".join(metadata.authors) if metadata.authors else metadata.first_author or "Unknown Author"
        year_str = str(metadata.year) if metadata.year else "n.d."
        title_str = metadata.title or "Untitled"
        
        citation = f"{authors_str} ({year_str}). {title_str}"
        
        if metadata.journal:
            citation += f". *{metadata.journal}*"
            if metadata.volume:
                citation += f", {metadata.volume}"
                if metadata.issue:
                    citation += f"({metadata.issue})"
            if metadata.pages:
                citation += f", {metadata.pages}"
        
        if metadata.doi:
            citation += f". https://doi.org/{metadata.doi}"
        
        return citation
    
    # Missing methods that are called by template system but not implemented
    
    def _extract_key_findings(self, analysis_result: AnalysisResult) -> List[str]:
        """
        Extract key findings from results and conclusion sections
        
        Args:
            analysis_result: Content analysis results
            
        Returns:
            List of key findings and main results
        """
        findings = []
        
        # Use existing key_concepts if available
        if analysis_result.key_concepts:
            findings.extend(analysis_result.key_concepts[:5])
        
        # Extract from results section
        if "results" in analysis_result.sections:
            results_text = analysis_result.sections["results"]
            findings.extend(self._extract_findings_from_text(results_text))
        
        # Extract from conclusion section
        if "conclusion" in analysis_result.sections:
            conclusion_text = analysis_result.sections["conclusion"]
            findings.extend(self._extract_findings_from_text(conclusion_text))
        
        # Remove duplicates and limit
        unique_findings = list(dict.fromkeys(findings))[:8]
        
        return unique_findings if unique_findings else [
            "Key findings require detailed analysis of results and conclusions",
            "Significant contributions identified in the study",
            "Novel insights presented in the research"
        ]
    
    def _extract_findings_from_text(self, text: str) -> List[str]:
        """
        Extract findings from text using pattern matching
        
        Args:
            text: Text to extract findings from
            
        Returns:
            List of extracted findings
        """
        if not text:
            return []
        
        findings = []
        clean_text = self._clean_extracted_text(text)
        
        # Finding patterns
        finding_patterns = [
            r"(?:we\s+)?(?:found|discovered|observed|identified|demonstrated|showed)\s+(?:that\s+)?([^.!?]+)",
            r"(?:results?\s+)?(?:indicate[s]?|suggest[s]?|reveal[s]?|show[s]?)\s+(?:that\s+)?([^.!?]+)",
            r"(?:significant|notable|important)\s+([^.!?]*(?:increase|decrease|improvement|reduction|difference|correlation|association|effect))",
            r"(?:the\s+)?(?:main|primary|key|principal)\s+(?:finding[s]?|result[s]?|outcome[s]?)\s+(?:was|were|is|are)\s+([^.!?]+)",
            r"(?:in\s+conclusion|to\s+conclude|overall),?\s+([^.!?]+)",
            r"(?:these\s+)?(?:findings|results)\s+(?:demonstrate|indicate|suggest|show)\s+([^.!?]+)"
        ]
        
        for pattern in finding_patterns:
            matches = re.finditer(pattern, clean_text, re.IGNORECASE)
            for match in matches:
                finding = self._clean_extracted_text(match.group(1))
                if len(finding) > 15 and len(finding) < 200:
                    findings.append(finding)
        
        # Look for sentences with finding keywords
        sentences = clean_text.split('.')
        finding_keywords = [
            'significant', 'increased', 'decreased', 'improved', 'reduced',
            'correlation', 'association', 'effect', 'impact', 'difference',
            'higher', 'lower', 'better', 'worse', 'effective', 'successful'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 20 and len(sentence) < 150 and
                any(keyword in sentence.lower() for keyword in finding_keywords)):
                clean_sentence = self._clean_extracted_text(sentence)
                if clean_sentence and clean_sentence not in findings:
                    findings.append(clean_sentence)
        
        return findings[:5]  # Limit to 5 findings
    
    def _extract_findings_with_patterns(self, text: str) -> List[str]:
        """
        Extract findings using comprehensive pattern matching (alias for _extract_findings_from_text)
        
        Args:
            text: Text to extract findings from
            
        Returns:
            List of extracted findings
        """
        return self._extract_findings_from_text(text)
    
    def _extract_applications_with_patterns(self, text: str) -> List[str]:
        """
        Extract practical applications using pattern matching
        
        Args:
            text: Text to extract applications from
            
        Returns:
            List of practical applications
        """
        if not text:
            return []
        
        applications = []
        clean_text = self._clean_extracted_text(text)
        
        # Application patterns
        application_patterns = [
            r"(?:practical\s+)?(?:applications?|implications?|uses?)\s+(?:include[s]?|are|of\s+this\s+work)\s+([^.!?]+)",
            r"(?:this\s+(?:work|study|research)\s+)?(?:can\s+be\s+)?(?:applied|used|implemented)\s+(?:in|for|to)\s+([^.!?]+)",
            r"(?:clinical|industrial|commercial|real-world)\s+(?:applications?|implications?|uses?)\s+([^.!?]*)",
            r"(?:these\s+)?(?:findings|results)\s+(?:have\s+)?(?:implications?|applications?)\s+(?:for|in)\s+([^.!?]+)",
            r"(?:potential\s+)?(?:applications?|uses?)\s+(?:in|for)\s+([^.!?]+)",
            r"(?:could\s+be\s+)?(?:useful|beneficial|valuable)\s+(?:for|in)\s+([^.!?]+)"
        ]
        
        for pattern in application_patterns:
            matches = re.finditer(pattern, clean_text, re.IGNORECASE)
            for match in matches:
                application = self._clean_extracted_text(match.group(1))
                if len(application) > 10 and len(application) < 150:
                    applications.append(application)
        
        # Look for sentences with application keywords
        sentences = clean_text.split('.')
        application_keywords = [
            'application', 'implementation', 'practice', 'clinical',
            'industrial', 'commercial', 'real-world', 'practical',
            'useful', 'beneficial', 'valuable', 'applicable'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 25 and len(sentence) < 150 and
                any(keyword in sentence.lower() for keyword in application_keywords)):
                clean_sentence = self._clean_extracted_text(sentence)
                if clean_sentence and clean_sentence not in applications:
                    applications.append(clean_sentence)
        
        return applications[:4]  # Limit to 4 applications
    
    # Additional missing methods that may be called by template system
    
    def _extract_conclusions(self, sections: Dict[str, str]) -> str:
        """Extract conclusions from conclusion section"""
        if "conclusion" in sections:
            conclusion_text = sections["conclusion"]
            return self._summarize_text(conclusion_text, max_length=300)
        elif "conclusions" in sections:
            conclusions_text = sections["conclusions"]
            return self._summarize_text(conclusions_text, max_length=300)
        else:
            return "Conclusions require analysis of the paper's final sections."
    
    def _extract_new_knowledge(self, sections: Dict[str, str]) -> str:
        """Extract new knowledge contributions"""
        # Look in discussion or conclusion for new knowledge
        for section_name in ["discussion", "conclusion", "implications"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for new knowledge patterns
                patterns = [
                    r"(?:new|novel|original)\s+(?:knowledge|understanding|insights?)\s+([^.!?]+)",
                    r"(?:this\s+work\s+)?(?:contributes?|adds?)\s+(?:new\s+)?([^.!?]*(?:knowledge|understanding))",
                    r"(?:previously\s+)?(?:unknown|unexplored|undiscovered)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        knowledge = self._clean_extracted_text(match.group(1))
                        if len(knowledge) > 20:
                            return knowledge
        
        return "New knowledge and insights require detailed analysis of the research contributions."
    
    def _extract_theoretical_connections(self, sections: Dict[str, str]) -> str:
        """Extract theoretical connections and relationships"""
        if "discussion" in sections:
            discussion_text = sections["discussion"]
            # Look for theoretical connection patterns
            patterns = [
                r"(?:connects?|relates?|links?)\s+(?:to|with)\s+([^.!?]*(?:theory|framework|model))",
                r"(?:theoretical\s+)?(?:connections?|relationships?|links?)\s+([^.!?]+)",
                r"(?:builds?\s+on|extends?|expands?)\s+([^.!?]*(?:theory|framework|work))"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, discussion_text, re.IGNORECASE)
                if match:
                    connection = self._clean_extracted_text(match.group(1))
                    if len(connection) > 15:
                        return connection
        
        return "Theoretical connections require analysis of the discussion and related work sections."
    
    def _extract_methodological_insights(self, sections: Dict[str, str]) -> str:
        """Extract methodological insights and contributions"""
        if "discussion" in sections:
            discussion_text = sections["discussion"]
            # Look for methodological insights
            patterns = [
                r"(?:methodological\s+)?(?:insights?|contributions?|advances?)\s+([^.!?]+)",
                r"(?:this\s+method|approach)\s+(?:provides?|offers?|enables?)\s+([^.!?]+)",
                r"(?:novel|new|innovative)\s+(?:method|approach|technique)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, discussion_text, re.IGNORECASE)
                if match:
                    insight = self._clean_extracted_text(match.group(1))
                    if len(insight) > 15:
                        return insight
        
        return "Methodological insights require analysis of the methods and discussion sections."
    
    def _extract_research_gaps(self, sections: Dict[str, str]) -> str:
        """Extract research gaps identified in the paper"""
        for section_name in ["introduction", "literature review", "discussion"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for gap patterns
                patterns = [
                    r"(?:research\s+)?(?:gap[s]?|limitation[s]?)\s+(?:in|of)\s+([^.!?]+)",
                    r"(?:lack\s+of|absence\s+of|limited)\s+(?:research|studies|work)\s+(?:on|in)\s+([^.!?]+)",
                    r"(?:few|little|limited)\s+(?:studies|research|work)\s+(?:have|has)\s+([^.!?]+)",
                    r"(?:remains?\s+)?(?:unclear|unknown|unexplored)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        gap = self._clean_extracted_text(match.group(1))
                        if len(gap) > 15:
                            return gap
        
        return "Research gaps require analysis of the literature review and discussion sections."
    
    def _extract_research_impact(self, sections: Dict[str, str]) -> str:
        """Extract research impact and broader implications"""
        for section_name in ["discussion", "conclusion", "implications"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for impact patterns
                patterns = [
                    r"(?:impact|implications?|consequences?)\s+(?:of|for)\s+([^.!?]+)",
                    r"(?:broader|wider|significant)\s+(?:impact|implications?)\s+([^.!?]+)",
                    r"(?:this\s+work\s+)?(?:will|could|may)\s+(?:impact|influence|affect)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        impact = self._clean_extracted_text(match.group(1))
                        if len(impact) > 15:
                            return impact
        
        return "Research impact requires analysis of the discussion and implications sections."
    
    def _extract_follow_up_questions(self, sections: Dict[str, str]) -> List[str]:
        """Extract follow-up questions and future research directions"""
        questions = []
        
        for section_name in ["discussion", "conclusion", "future work"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for question patterns
                patterns = [
                    r"(?:future\s+)?(?:questions?|research)\s+(?:include[s]?|are)\s+([^.!?]+)",
                    r"(?:it\s+remains?\s+)?(?:unclear|unknown)\s+([^.!?]+)",
                    r"(?:further\s+)?(?:investigation|research|study)\s+(?:is\s+needed|required)\s+(?:to|into)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        question = self._clean_extracted_text(match.group(1))
                        if len(question) > 15 and len(question) < 150:
                            questions.append(question)
        
        return questions[:3] if questions else ["Future research directions require analysis of the discussion section."]
    
    def _extract_implementation(self, sections: Dict[str, str]) -> str:
        """Extract implementation details and considerations"""
        for section_name in ["discussion", "conclusion", "implementation"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for implementation patterns
                patterns = [
                    r"(?:implementation|deployment|application)\s+(?:of|requires?|involves?)\s+([^.!?]+)",
                    r"(?:to\s+implement|for\s+implementation)\s+([^.!?]+)",
                    r"(?:practical\s+)?(?:considerations?|requirements?)\s+(?:for|include)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        implementation = self._clean_extracted_text(match.group(1))
                        if len(implementation) > 15:
                            return implementation
        
        return "Implementation details require analysis of the discussion and practical considerations."
    
    def _extract_scalability(self, sections: Dict[str, str]) -> str:
        """Extract scalability considerations"""
        for section_name in ["discussion", "conclusion"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for scalability patterns
                patterns = [
                    r"(?:scalability|scaling)\s+([^.!?]+)",
                    r"(?:can\s+be\s+)?(?:scaled|extended)\s+(?:to|for)\s+([^.!?]+)",
                    r"(?:large[r]?\s+scale|broader\s+application)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        scalability = self._clean_extracted_text(match.group(1))
                        if len(scalability) > 15:
                            return scalability
        
        return "Scalability considerations require analysis of the discussion section."
    
    def _extract_related_work(self, sections: Dict[str, str]) -> str:
        """Extract related work and literature context"""
        if "related work" in sections:
            return self._summarize_text(sections["related work"], max_length=200)
        elif "literature review" in sections:
            return self._summarize_text(sections["literature review"], max_length=200)
        elif "background" in sections:
            return self._summarize_text(sections["background"], max_length=200)
        else:
            return "Related work requires analysis of the literature review and background sections."
    
    def _extract_competing_approaches(self, sections: Dict[str, str]) -> str:
        """Extract competing approaches and alternatives"""
        for section_name in ["related work", "literature review", "discussion"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for competing approach patterns
                patterns = [
                    r"(?:alternative|competing|other)\s+(?:approaches?|methods?|techniques?)\s+([^.!?]+)",
                    r"(?:compared\s+to|versus|vs\.?)\s+([^.!?]+)",
                    r"(?:existing|current|traditional)\s+(?:approaches?|methods?)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        approach = self._clean_extracted_text(match.group(1))
                        if len(approach) > 15:
                            return approach
        
        return "Competing approaches require analysis of the related work and comparison sections."
    
    def _extract_future_work(self, sections: Dict[str, str]) -> str:
        """Extract future work and research directions"""
        if "future work" in sections:
            return self._summarize_text(sections["future work"], max_length=200)
        elif "future research" in sections:
            return self._summarize_text(sections["future research"], max_length=200)
        else:
            for section_name in ["conclusion", "discussion"]:
                if section_name in sections:
                    text = sections[section_name]
                    # Look for future work patterns
                    patterns = [
                        r"(?:future\s+)?(?:work|research|studies?)\s+(?:will|should|could|may)\s+([^.!?]+)",
                        r"(?:next\s+steps?|future\s+directions?)\s+(?:include[s]?|are)\s+([^.!?]+)",
                        r"(?:further\s+)?(?:investigation|research|exploration)\s+(?:is\s+needed|required)\s+([^.!?]+)"
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            future_work = self._clean_extracted_text(match.group(1))
                            if len(future_work) > 20:
                                return future_work
        
        return "Future work directions require analysis of the conclusion and discussion sections."
    
    # Balanced template specific methods
    
    def _extract_literature_context(self, sections: Dict[str, str]) -> str:
        """Extract literature context for balanced template"""
        return self._extract_related_work(sections)
    
    def _extract_research_design(self, sections: Dict[str, str]) -> str:
        """Extract research design information"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            # Look for design patterns
            patterns = [
                r"(?:research\s+)?(?:design|approach|methodology)\s+([^.!?]+)",
                r"(?:this\s+)?(?:study|research)\s+(?:used|employed|adopted)\s+(?:a\s+)?([^.!?]*(?:design|approach|method))",
                r"(?:experimental|observational|cross-sectional|longitudinal|qualitative|quantitative)\s+(?:design|study|approach)\s*([^.!?]*)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    design = self._clean_extracted_text(match.group(1) if match.group(1) else match.group(0))
                    if len(design) > 10:
                        return design
        
        return "Research design requires analysis of the methodology section."
    
    def _extract_methods_list(self, sections: Dict[str, str]) -> List[str]:
        """Extract list of methods used"""
        methods = []
        
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for method lists
            method_patterns = [
                r"(?:methods?\s+)?(?:included?|used|employed|applied)\s+([^.!?]+)",
                r"(?:we\s+)?(?:used|employed|applied|conducted|performed)\s+([^.!?]+)",
                r"(?:techniques?\s+)?(?:such\s+as|including)\s+([^.!?]+)"
            ]
            
            for pattern in method_patterns:
                matches = re.finditer(pattern, method_text, re.IGNORECASE)
                for match in matches:
                    method = self._clean_extracted_text(match.group(1))
                    if len(method) > 10 and len(method) < 100:
                        methods.append(method)
        
        return methods[:4] if methods else ["Methods require analysis of the methodology section."]
    
    def _extract_study_parameters(self, sections: Dict[str, str]) -> str:
        """Extract study parameters and settings"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for parameter patterns
            patterns = [
                r"(?:parameters?|settings?|conditions?)\s+(?:were|included?)\s+([^.!?]+)",
                r"(?:sample\s+size|participants?|subjects?)\s+(?:was|were|included?)\s+([^.!?]+)",
                r"(?:duration|period|timeframe)\s+(?:was|of)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    parameters = self._clean_extracted_text(match.group(1))
                    if len(parameters) > 10:
                        return parameters
        
        return "Study parameters require analysis of the methodology section."
    
    def _extract_primary_results(self, sections: Dict[str, str]) -> List[str]:
        """Extract primary results"""
        results = []
        
        if "results" in sections:
            results_text = sections["results"]
            results.extend(self._extract_findings_from_text(results_text)[:3])
        
        if "abstract" in sections:
            abstract_text = sections["abstract"]
            # Look for results in abstract
            result_patterns = [
                r"(?:results?\s+)?(?:showed?|demonstrated?|revealed?|found)\s+([^.!?]+)",
                r"(?:we\s+)?(?:found|observed|identified)\s+([^.!?]+)"
            ]
            
            for pattern in result_patterns:
                match = re.search(pattern, abstract_text, re.IGNORECASE)
                if match:
                    result = self._clean_extracted_text(match.group(1))
                    if len(result) > 15 and result not in results:
                        results.append(result)
        
        return results[:3] if results else ["Primary results require analysis of the results section."]
    
    def _extract_supporting_evidence(self, sections: Dict[str, str]) -> str:
        """Extract supporting evidence"""
        if "results" in sections:
            results_text = sections["results"]
            # Look for evidence patterns
            patterns = [
                r"(?:evidence|support|confirmation)\s+(?:for|of)\s+([^.!?]+)",
                r"(?:supported\s+by|confirmed\s+by|evidenced\s+by)\s+([^.!?]+)",
                r"(?:statistical|significant)\s+(?:evidence|support)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, results_text, re.IGNORECASE)
                if match:
                    evidence = self._clean_extracted_text(match.group(1))
                    if len(evidence) > 15:
                        return evidence
        
        return "Supporting evidence requires analysis of the results and discussion sections."
    
    def _extract_data_analysis(self, sections: Dict[str, str]) -> str:
        """Extract data analysis methods"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for analysis patterns
            patterns = [
                r"(?:data\s+)?(?:analysis|analyses)\s+(?:was|were|included?)\s+([^.!?]+)",
                r"(?:statistical\s+)?(?:analysis|tests?|methods?)\s+(?:used|employed|applied)\s+([^.!?]+)",
                r"(?:analyzed|processed|examined)\s+(?:using|with|by)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    analysis = self._clean_extracted_text(match.group(1))
                    if len(analysis) > 10:
                        return analysis
        
        return "Data analysis methods require analysis of the methodology section."
    
    def _extract_theoretical_implications(self, sections: Dict[str, str]) -> str:
        """Extract theoretical implications"""
        for section_name in ["discussion", "conclusion", "implications"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for theoretical implication patterns
                patterns = [
                    r"(?:theoretical\s+)?(?:implications?|consequences?)\s+([^.!?]+)",
                    r"(?:for\s+)?(?:theory|theoretical\s+understanding)\s+([^.!?]+)",
                    r"(?:contributes?\s+to|advances?|extends?)\s+(?:theoretical\s+)?([^.!?]*(?:theory|understanding|knowledge))"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        implication = self._clean_extracted_text(match.group(1))
                        if len(implication) > 15:
                            return implication
        
        return "Theoretical implications require analysis of the discussion section."
    
    def _extract_methodological_contributions(self, sections: Dict[str, str]) -> str:
        """Extract methodological contributions"""
        return self._extract_methodological_insights(sections)
    
    def _extract_strengths(self, sections: Dict[str, str]) -> List[str]:
        """Extract study strengths"""
        strengths = []
        
        for section_name in ["discussion", "conclusion"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for strength patterns
                patterns = [
                    r"(?:strengths?\s+)?(?:of\s+this\s+study\s+)?(?:include[s]?|are)\s+([^.!?]+)",
                    r"(?:advantage[s]?|benefit[s]?)\s+(?:of\s+this\s+approach\s+)?(?:include[s]?|are)\s+([^.!?]+)",
                    r"(?:robust|strong|reliable|valid)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        strength = self._clean_extracted_text(match.group(1))
                        if len(strength) > 10 and len(strength) < 100:
                            strengths.append(strength)
        
        return strengths[:3] if strengths else ["Study strengths require analysis of the discussion section."]
    
    def _extract_future_research(self, sections: Dict[str, str]) -> str:
        """Extract future research directions"""
        return self._extract_future_work(sections)
    
    def _extract_field_advancement(self, sections: Dict[str, str]) -> str:
        """Extract how the work advances the field"""
        for section_name in ["discussion", "conclusion"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for field advancement patterns
                patterns = [
                    r"(?:advances?|contributes?\s+to|improves?)\s+(?:the\s+)?(?:field|discipline|area)\s+([^.!?]+)",
                    r"(?:field\s+)?(?:advancement|progress|development)\s+([^.!?]+)",
                    r"(?:moves?\s+the\s+field\s+forward|pushes?\s+boundaries?)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        advancement = self._clean_extracted_text(match.group(1))
                        if len(advancement) > 15:
                            return advancement
        
        return "Field advancement requires analysis of the discussion and conclusion sections."
    
    def _extract_cross_disciplinary(self, sections: Dict[str, str]) -> str:
        """Extract cross-disciplinary connections"""
        for section_name in ["discussion", "introduction"]:
            if section_name in sections:
                text = sections[section_name]
                # Look for cross-disciplinary patterns
                patterns = [
                    r"(?:cross-disciplinary|interdisciplinary|multidisciplinary)\s+([^.!?]+)",
                    r"(?:connects?|bridges?|links?)\s+(?:different\s+)?(?:fields?|disciplines?)\s+([^.!?]+)",
                    r"(?:applications?\s+in|relevant\s+to)\s+(?:other\s+)?(?:fields?|disciplines?)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        connection = self._clean_extracted_text(match.group(1))
                        if len(connection) > 15:
                            return connection
        
        return "Cross-disciplinary connections require analysis of the discussion section."
    
    def _extract_personal_relevance(self, sections: Dict[str, str]) -> str:
        """Extract personal relevance (generic placeholder)"""
        return "Personal relevance depends on individual research interests and goals."
    
    def _extract_key_takeaways(self, sections: Dict[str, str]) -> List[str]:
        """Extract key takeaways"""
        takeaways = []
        
        # Use key findings as takeaways
        if "conclusion" in sections:
            conclusion_text = sections["conclusion"]
            takeaways.extend(self._extract_findings_from_text(conclusion_text)[:3])
        
        # Add significance as takeaway
        significance = self._extract_significance(sections)
        if significance and significance not in takeaways:
            takeaways.append(significance)
        
        return takeaways[:4] if takeaways else ["Key takeaways require analysis of the conclusion section."]
    
    def _extract_action_items(self, sections: Dict[str, str]) -> List[str]:
        """Extract action items (generic placeholder)"""
        return [
            "Review methodology for potential application to own research",
            "Consider implications for current projects",
            "Explore related work and references",
            "Assess relevance to research objectives"
        ]  
  
    # Focus-specific data extraction methods that are called by templates
    
    def _extract_study_design_detailed(self, sections: Dict[str, str]) -> str:
        """Extract detailed study design for research template"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for detailed design patterns
            patterns = [
                r"(?:study\s+design|research\s+design|experimental\s+design)\s*:?\s*([^.!?]+)",
                r"(?:this\s+)?(?:study|research|experiment)\s+(?:used|employed|adopted)\s+(?:a\s+)?([^.!?]*(?:design|approach|methodology))",
                r"(?:randomized|controlled|cross-sectional|longitudinal|prospective|retrospective)\s+([^.!?]*(?:study|trial|design))",
                r"(?:participants?\s+were\s+)?(?:randomly\s+)?(?:assigned|allocated)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    design = self._clean_extracted_text(match.group(1))
                    if len(design) > 15:
                        return design
        
        # Fallback to basic research design
        return self._extract_research_design(sections)
    
    def _extract_theoretical_propositions(self, sections: Dict[str, str]) -> List[str]:
        """Extract theoretical propositions for theory template"""
        propositions = []
        
        for section_name in ["introduction", "theoretical framework", "theory", "background"]:
            if section_name in sections:
                text = sections[section_name]
                
                # Look for proposition patterns
                patterns = [
                    r"(?:we\s+)?(?:propose|hypothesize|suggest|argue)\s+(?:that\s+)?([^.!?]+)",
                    r"(?:theoretical\s+)?(?:proposition|hypothesis|assumption)\s*:?\s*([^.!?]+)",
                    r"(?:it\s+is\s+)?(?:proposed|hypothesized|suggested)\s+(?:that\s+)?([^.!?]+)",
                    r"(?:our\s+)?(?:theory|framework|model)\s+(?:suggests|proposes|predicts)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        proposition = self._clean_extracted_text(match.group(1))
                        if len(proposition) > 20 and len(proposition) < 200:
                            propositions.append(proposition)
        
        return propositions[:4] if propositions else [
            "Theoretical propositions require analysis of the theoretical framework section",
            "Key assumptions and hypotheses need detailed review",
            "Conceptual relationships require further examination"
        ]
    
    def _extract_experimental_design_detailed(self, sections: Dict[str, str]) -> str:
        """Extract detailed experimental design for method template"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for experimental design patterns
            patterns = [
                r"(?:experimental\s+)?(?:design|setup|procedure)\s*:?\s*([^.!?]+)",
                r"(?:experiments?\s+were\s+)?(?:conducted|performed|carried\s+out)\s+([^.!?]+)",
                r"(?:experimental\s+)?(?:conditions?|treatments?|interventions?)\s+(?:included?|were)\s+([^.!?]+)",
                r"(?:control\s+group|control\s+condition)\s+([^.!?]+)",
                r"(?:independent\s+variable[s]?|dependent\s+variable[s]?)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    design = self._clean_extracted_text(match.group(1))
                    if len(design) > 15:
                        return design
        
        # Fallback to basic methodology
        return self._extract_methodology(sections)
    
    def _extract_review_scope(self, sections: Dict[str, str]) -> str:
        """Extract review scope for review template"""
        for section_name in ["introduction", "methods", "methodology", "abstract"]:
            if section_name in sections:
                text = sections[section_name]
                
                # Look for scope patterns
                patterns = [
                    r"(?:this\s+review\s+)?(?:covers|examines|includes|focuses\s+on)\s+([^.!?]+)",
                    r"(?:scope\s+of\s+this\s+review|review\s+scope)\s*:?\s*([^.!?]+)",
                    r"(?:we\s+)?(?:reviewed|examined|analyzed)\s+([^.!?]*(?:studies|papers|articles|literature))",
                    r"(?:inclusion\s+criteria|search\s+strategy)\s+([^.!?]+)",
                    r"(?:systematic\s+search|literature\s+search)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        scope = self._clean_extracted_text(match.group(1))
                        if len(scope) > 15:
                            return scope
        
        return "Review scope and methodology require analysis of the methods section."
    
    def _extract_overview_from_introduction(self, sections: Dict[str, str]) -> str:
        """Extract overview from introduction for review template"""
        if "introduction" in sections:
            intro_text = sections["introduction"]
            
            # Extract first few sentences as overview
            sentences = intro_text.split('.')[:3]  # First 3 sentences
            overview = '. '.join(sentence.strip() for sentence in sentences if sentence.strip())
            
            if len(overview) > 50:
                return self._clean_extracted_text(overview)
        
        elif "abstract" in sections:
            # Fallback to abstract
            abstract_text = sections["abstract"]
            return self._summarize_text(abstract_text, max_length=200)
        
        return "Overview requires analysis of the introduction section."
    
    # Focus-specific data extraction methods called by _extract_content_data
    
    def _extract_theory_specific_data(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Extract theory-specific data for theory template"""
        sections = analysis_result.sections
        
        return {
            "theoretical_propositions": self._extract_theoretical_propositions(sections),
            "equations": self._extract_equations(sections),
            "assumptions": self._extract_assumptions(sections),
            "theoretical_model": self._extract_theoretical_model(sections),
            "conceptual_relationships": self._extract_conceptual_relationships(sections)
        }
    
    def _extract_research_specific_data(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Extract research-specific data for research template"""
        sections = analysis_result.sections
        
        return {
            "study_design_detailed": self._extract_study_design_detailed(sections),
            "participants": self._extract_participants(sections),
            "measures": self._extract_measures(sections),
            "data_collection": self._extract_data_collection(sections),
            "statistical_analysis": self._extract_statistical_analysis(sections)
        }
    
    def _extract_method_specific_data(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Extract method-specific data for method template"""
        sections = analysis_result.sections
        
        return {
            "experimental_design_detailed": self._extract_experimental_design_detailed(sections),
            "implementation_details": self._extract_implementation_details(sections),
            "validation_approach": self._extract_validation_approach(sections),
            "performance_metrics": self._extract_performance_metrics(sections),
            "comparison_methods": self._extract_comparison_methods(sections)
        }
    
    def _extract_review_specific_data(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Extract review-specific data for review template"""
        sections = analysis_result.sections
        
        return {
            "review_scope": self._extract_review_scope(sections),
            "search_strategy": self._extract_search_strategy(sections),
            "inclusion_criteria": self._extract_inclusion_criteria(sections),
            "literature_synthesis": self._extract_literature_synthesis(sections),
            "research_gaps_detailed": self._extract_research_gaps_detailed(sections),
            "overview_from_introduction": self._extract_overview_from_introduction(sections)
        }
    
    # Additional helper methods for focus-specific data
    
    def _extract_equations(self, sections: Dict[str, str]) -> List[str]:
        """Extract equations from text"""
        equations = []
        
        for section_text in sections.values():
            # Look for equation patterns (basic)
            equation_patterns = [
                r"(?:equation|formula)\s*\(?(\d+)\)?\s*:?\s*([^.!?\n]+)",
                r"([A-Za-z]\s*=\s*[^.!?\n]+)",
                r"(\$[^$]+\$)",  # LaTeX inline math
                r"(\\\[[^\]]+\\\])"  # LaTeX display math
            ]
            
            for pattern in equation_patterns:
                matches = re.finditer(pattern, section_text, re.IGNORECASE)
                for match in matches:
                    equation = match.group(1) if len(match.groups()) > 1 else match.group(0)
                    equation = self._clean_extracted_text(equation)
                    if len(equation) > 5 and equation not in equations:
                        equations.append(equation)
        
        return equations[:5] if equations else ["Mathematical equations require detailed analysis of the paper content."]
    
    def _extract_assumptions(self, sections: Dict[str, str]) -> List[str]:
        """Extract assumptions from text"""
        assumptions = []
        
        for section_name, section_text in sections.items():
            if any(keyword in section_name.lower() for keyword in ["method", "theory", "assumption", "model"]):
                # Look for assumption patterns
                patterns = [
                    r"(?:we\s+)?(?:assume|assumption)\s+(?:that\s+)?([^.!?]+)",
                    r"(?:it\s+is\s+)?(?:assumed|given)\s+(?:that\s+)?([^.!?]+)",
                    r"(?:under\s+the\s+)?(?:assumption|condition)\s+(?:that\s+)?([^.!?]+)"
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, section_text, re.IGNORECASE)
                    for match in matches:
                        assumption = self._clean_extracted_text(match.group(1))
                        if len(assumption) > 15 and len(assumption) < 150:
                            assumptions.append(assumption)
        
        return assumptions[:4] if assumptions else ["Key assumptions require analysis of the theoretical framework."]
    
    def _extract_theoretical_model(self, sections: Dict[str, str]) -> str:
        """Extract theoretical model description"""
        for section_name in ["theory", "model", "theoretical framework", "methods"]:
            if section_name in sections:
                text = sections[section_name]
                
                # Look for model patterns
                patterns = [
                    r"(?:theoretical\s+)?(?:model|framework)\s*:?\s*([^.!?]+)",
                    r"(?:our\s+)?(?:model|approach)\s+(?:is\s+based\s+on|assumes|considers)\s+([^.!?]+)",
                    r"(?:conceptual\s+)?(?:model|framework)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        model = self._clean_extracted_text(match.group(1))
                        if len(model) > 20:
                            return model
        
        return "Theoretical model requires analysis of the theoretical framework section."
    
    def _extract_conceptual_relationships(self, sections: Dict[str, str]) -> str:
        """Extract conceptual relationships"""
        for section_name in ["theory", "introduction", "discussion"]:
            if section_name in sections:
                text = sections[section_name]
                
                # Look for relationship patterns
                patterns = [
                    r"(?:relationship|connection|link)\s+(?:between|among)\s+([^.!?]+)",
                    r"([^.!?]*)\s+(?:is\s+related\s+to|correlates\s+with|influences)\s+([^.!?]+)",
                    r"(?:conceptual\s+)?(?:relationships?|connections?)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        relationship = self._clean_extracted_text(match.group(1))
                        if len(relationship) > 15:
                            return relationship
        
        return "Conceptual relationships require analysis of the theoretical sections."
    
    def _extract_participants(self, sections: Dict[str, str]) -> str:
        """Extract participant information"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for participant patterns
            patterns = [
                r"(?:participants?|subjects?)\s*:?\s*([^.!?]+)",
                r"(?:sample\s+)?(?:consisted\s+of|included)\s+([^.!?]*(?:participants?|subjects?|individuals?))",
                r"(?:recruitment|selection)\s+([^.!?]+)",
                r"(?:inclusion|exclusion)\s+(?:criteria|requirements)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    participants = self._clean_extracted_text(match.group(1))
                    if len(participants) > 15:
                        return participants
        
        return "Participant information requires analysis of the methods section."
    
    def _extract_measures(self, sections: Dict[str, str]) -> List[str]:
        """Extract measurement instruments and variables"""
        measures = []
        
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for measure patterns
            patterns = [
                r"(?:measures?|instruments?|assessments?)\s*:?\s*([^.!?]+)",
                r"(?:we\s+)?(?:used|employed|administered)\s+([^.!?]*(?:scale|questionnaire|test|measure))",
                r"(?:dependent\s+variable[s]?|outcome\s+measure[s]?)\s+([^.!?]+)",
                r"(?:primary\s+outcome|secondary\s+outcome)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, method_text, re.IGNORECASE)
                for match in matches:
                    measure = self._clean_extracted_text(match.group(1))
                    if len(measure) > 10 and len(measure) < 100:
                        measures.append(measure)
        
        return measures[:4] if measures else ["Measurement details require analysis of the methods section."]
    
    def _extract_data_collection(self, sections: Dict[str, str]) -> str:
        """Extract data collection procedures"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for data collection patterns
            patterns = [
                r"(?:data\s+collection|data\s+gathering)\s*:?\s*([^.!?]+)",
                r"(?:procedure|protocol)\s*:?\s*([^.!?]+)",
                r"(?:data\s+were\s+)?(?:collected|gathered|obtained)\s+([^.!?]+)",
                r"(?:administration|implementation)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    collection = self._clean_extracted_text(match.group(1))
                    if len(collection) > 15:
                        return collection
        
        return "Data collection procedures require analysis of the methods section."
    
    def _extract_statistical_analysis(self, sections: Dict[str, str]) -> str:
        """Extract statistical analysis details"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for statistical analysis patterns
            patterns = [
                r"(?:statistical\s+)?(?:analysis|analyses)\s*:?\s*([^.!?]+)",
                r"(?:data\s+were\s+)?(?:analyzed|examined)\s+(?:using|with)\s+([^.!?]+)",
                r"(?:statistical\s+)?(?:tests?|procedures?)\s+(?:included?|used)\s+([^.!?]+)",
                r"(?:significance\s+level|alpha\s+level)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    analysis = self._clean_extracted_text(match.group(1))
                    if len(analysis) > 10:
                        return analysis
        
        return "Statistical analysis details require analysis of the methods section."
    
    def _extract_implementation_details(self, sections: Dict[str, str]) -> str:
        """Extract implementation details for method template"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for implementation patterns
            patterns = [
                r"(?:implementation|development)\s*:?\s*([^.!?]+)",
                r"(?:algorithm|method)\s+(?:was\s+)?(?:implemented|developed)\s+([^.!?]+)",
                r"(?:technical\s+)?(?:details|specifications)\s+([^.!?]+)",
                r"(?:software|platform|framework)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    details = self._clean_extracted_text(match.group(1))
                    if len(details) > 15:
                        return details
        
        return "Implementation details require analysis of the methods section."
    
    def _extract_validation_approach(self, sections: Dict[str, str]) -> str:
        """Extract validation approach"""
        for section_name in ["methods", "methodology", "validation", "evaluation"]:
            if section_name in sections:
                text = sections[section_name]
                
                # Look for validation patterns
                patterns = [
                    r"(?:validation|verification)\s*:?\s*([^.!?]+)",
                    r"(?:to\s+validate|for\s+validation)\s+([^.!?]+)",
                    r"(?:cross-validation|hold-out|bootstrap)\s+([^.!?]+)",
                    r"(?:evaluation\s+)?(?:metrics?|criteria)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        validation = self._clean_extracted_text(match.group(1))
                        if len(validation) > 15:
                            return validation
        
        return "Validation approach requires analysis of the methods section."
    
    def _extract_performance_metrics(self, sections: Dict[str, str]) -> List[str]:
        """Extract performance metrics"""
        metrics = []
        
        for section_name in ["methods", "results", "evaluation"]:
            if section_name in sections:
                text = sections[section_name]
                
                # Look for metric patterns
                patterns = [
                    r"(?:performance\s+)?(?:metrics?|measures?)\s*:?\s*([^.!?]+)",
                    r"(?:accuracy|precision|recall|f1-score|rmse|mae)\s+([^.!?]*)",
                    r"(?:evaluation\s+)?(?:criteria|benchmarks?)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        metric = self._clean_extracted_text(match.group(1) if len(match.groups()) > 0 else match.group(0))
                        if len(metric) > 5 and len(metric) < 100:
                            metrics.append(metric)
        
        return metrics[:4] if metrics else ["Performance metrics require analysis of the results section."]
    
    def _extract_comparison_methods(self, sections: Dict[str, str]) -> str:
        """Extract comparison methods"""
        for section_name in ["methods", "related work", "comparison"]:
            if section_name in sections:
                text = sections[section_name]
                
                # Look for comparison patterns
                patterns = [
                    r"(?:compared\s+(?:to|with|against))\s+([^.!?]+)",
                    r"(?:baseline|benchmark)\s+(?:methods?|approaches?)\s+([^.!?]+)",
                    r"(?:comparison\s+with|versus)\s+([^.!?]+)",
                    r"(?:state-of-the-art|existing)\s+(?:methods?|approaches?)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        comparison = self._clean_extracted_text(match.group(1))
                        if len(comparison) > 15:
                            return comparison
        
        return "Comparison methods require analysis of the methods and related work sections."
    
    def _extract_search_strategy(self, sections: Dict[str, str]) -> str:
        """Extract search strategy for review template"""
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for search strategy patterns
            patterns = [
                r"(?:search\s+strategy|literature\s+search)\s*:?\s*([^.!?]+)",
                r"(?:databases?\s+searched|search\s+terms)\s+([^.!?]+)",
                r"(?:systematic\s+search|comprehensive\s+search)\s+([^.!?]+)",
                r"(?:keywords?|search\s+string)\s*:?\s*([^.!?]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, method_text, re.IGNORECASE)
                if match:
                    strategy = self._clean_extracted_text(match.group(1))
                    if len(strategy) > 15:
                        return strategy
        
        return "Search strategy requires analysis of the methods section."
    
    def _extract_inclusion_criteria(self, sections: Dict[str, str]) -> List[str]:
        """Extract inclusion criteria for review template"""
        criteria = []
        
        if "methods" in sections or "methodology" in sections:
            method_text = sections.get("methods") or sections.get("methodology")
            
            # Look for criteria patterns
            patterns = [
                r"(?:inclusion\s+criteria|eligibility\s+criteria)\s*:?\s*([^.!?]+)",
                r"(?:studies?\s+were\s+)?(?:included\s+if|selected\s+if)\s+([^.!?]+)",
                r"(?:criteria\s+for\s+inclusion)\s+([^.!?]+)"
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, method_text, re.IGNORECASE)
                for match in matches:
                    criterion = self._clean_extracted_text(match.group(1))
                    if len(criterion) > 15 and len(criterion) < 150:
                        criteria.append(criterion)
        
        return criteria[:4] if criteria else ["Inclusion criteria require analysis of the methods section."]
    
    def _extract_literature_synthesis(self, sections: Dict[str, str]) -> str:
        """Extract literature synthesis approach"""
        for section_name in ["methods", "results", "discussion"]:
            if section_name in sections:
                text = sections[section_name]
                
                # Look for synthesis patterns
                patterns = [
                    r"(?:synthesis|meta-analysis)\s*:?\s*([^.!?]+)",
                    r"(?:data\s+)?(?:synthesis|integration)\s+([^.!?]+)",
                    r"(?:qualitative|quantitative)\s+(?:synthesis|analysis)\s+([^.!?]+)",
                    r"(?:thematic\s+analysis|content\s+analysis)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        synthesis = self._clean_extracted_text(match.group(1))
                        if len(synthesis) > 15:
                            return synthesis
        
        return "Literature synthesis approach requires analysis of the methods section."
    
    def _extract_research_gaps_detailed(self, sections: Dict[str, str]) -> List[str]:
        """Extract detailed research gaps for review template"""
        gaps = []
        
        for section_name in ["introduction", "discussion", "conclusion"]:
            if section_name in sections:
                text = sections[section_name]
                
                # Look for detailed gap patterns
                patterns = [
                    r"(?:research\s+gap[s]?|knowledge\s+gap[s]?)\s*:?\s*([^.!?]+)",
                    r"(?:limited\s+research|few\s+studies)\s+(?:on|in|regarding)\s+([^.!?]+)",
                    r"(?:future\s+research\s+should|further\s+investigation)\s+([^.!?]+)",
                    r"(?:remains?\s+unclear|not\s+well\s+understood)\s+([^.!?]+)"
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        gap = self._clean_extracted_text(match.group(1))
                        if len(gap) > 20 and len(gap) < 200:
                            gaps.append(gap)
        
        return gaps[:5] if gaps else ["Research gaps require analysis of the discussion and conclusion sections."]