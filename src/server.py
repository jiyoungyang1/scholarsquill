#!/usr/bin/env python3
"""
ScholarsQuill MCP Server
Standalone MCP server for processing scientific PDF papers into structured markdown literature notes
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# MCP imports with fallback to mock
try:
    from mcp.server import Server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
    import mcp.types as types
except ImportError:
    # Fallback to mock MCP for testing
    from .mcp_mock import Server, Tool, ToolResult
    # Create mock types
    class TextContent:
        def __init__(self, text: str):
            self.text = text
    
    class ImageContent:
        def __init__(self, data: str, mimeType: str):
            self.data = data
            self.mimeType = mimeType
    
    class EmbeddedResource:
        def __init__(self, resource: Any):
            self.resource = resource
    
    class Resource:
        def __init__(self, uri: str, name: str, description: str = ""):
            self.uri = uri
            self.name = name
            self.description = description
    
    # Mock types module
    class types:
        TextContent = TextContent
        ImageContent = ImageContent
        EmbeddedResource = EmbeddedResource
        Resource = Resource

# Local imports
try:
    from .models import (
        PaperMetadata, ProcessingOptions, NoteContent, AnalysisResult,
        CommandArgs, FocusType, DepthType, FormatType
    )
    from .interfaces import (
        PDFProcessorInterface, ContentAnalyzerInterface, NoteGeneratorInterface,
        CommandParserInterface, BatchProcessorInterface
    )
    from .pdf_processor import PDFProcessor
    from .content_analyzer import ContentAnalyzer
    from .note_generator import NoteGenerator
    from .command_parser import CommandParser
    from .batch_processor import BatchProcessor
    from .minireview_processor import MiniReviewProcessor
    from .citemap_processor import CitemapProcessor
    from .content_extractor import ContentExtractor
    from .analysis_instructions import AnalysisInstructionsGenerator
    from .template_loader import TemplateLoader
    from .config import ServerConfig
    from .exceptions import (
        PDFProcessingError, ContentAnalysisError, NoteGenerationError,
        CommandParsingError, BatchProcessingError, TemplateError
    )
    from .utils import setup_logging, ensure_directory
except ImportError:
    from models import (
        PaperMetadata, ProcessingOptions, NoteContent, AnalysisResult,
        CommandArgs, FocusType, DepthType, FormatType
    )
    from interfaces import (
        PDFProcessorInterface, ContentAnalyzerInterface, NoteGeneratorInterface,
        CommandParserInterface, BatchProcessorInterface
    )
    from pdf_processor import PDFProcessor
    from content_analyzer import ContentAnalyzer
    from note_generator import NoteGenerator
    from command_parser import CommandParser
    from batch_processor import BatchProcessor
    from minireview_processor import MiniReviewProcessor
    from citemap_processor import CitemapProcessor
    from content_extractor import ContentExtractor
    from analysis_instructions import AnalysisInstructionsGenerator
    from template_loader import TemplateLoader
    from config import ServerConfig
    from exceptions import (
        PDFProcessingError, ContentAnalysisError, NoteGenerationError,
        CommandParsingError, BatchProcessingError, TemplateError
    )
    from utils import setup_logging, ensure_directory

# Configure logging
logger = logging.getLogger("scholarsquill")

class ScholarsQuillServer:
    """Main MCP server class for ScholarsQuill"""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        """
        Initialize the MCP server with AI integration architecture
        
        This server acts as a tool provider that extracts PDF content and provides templates
        and analysis instructions for Claude to perform intelligent analysis and note generation.
        """
        self.config = config or ServerConfig()
        self.server = Server("scholarsquill")
        
        # Setup logging first
        setup_logging(self.config.log_level)
        logger.info("Initializing ScholarsQuill MCP Server with AI integration architecture...")
        
        # Initialize primary AI integration components
        try:
            # ContentExtractor for basic PDF processing without intelligent analysis
            self.content_extractor = ContentExtractor()
            logger.info("✓ ContentExtractor initialized for basic PDF content extraction")
            
            # AnalysisInstructionsGenerator for creating comprehensive Claude guidance
            self.analysis_instructions = AnalysisInstructionsGenerator()
            logger.info("✓ AnalysisInstructionsGenerator initialized for Claude guidance")
            
            # TemplateLoader with embedded analysis instructions
            self.template_loader = TemplateLoader(
                templates_dir=self.config.default_templates_dir
            )
            logger.info(f"✓ TemplateLoader initialized with embedded instructions (dir: {self.config.default_templates_dir})")
            
            # PDFProcessor for low-level PDF operations (still needed for content extraction)
            self.pdf_processor: PDFProcessorInterface = PDFProcessor()
            logger.info("✓ PDFProcessor initialized for low-level PDF operations")
            
        except Exception as e:
            logger.error(f"Failed to initialize core components: {str(e)}")
            raise
        
        # Initialize legacy components only for backward compatibility and non-MCP operations
        # These are NOT used in the main MCP workflow but kept for standalone operation
        try:
            self.content_analyzer: ContentAnalyzerInterface = ContentAnalyzer()
            self.command_parser: CommandParserInterface = CommandParser()
            self.batch_processor: BatchProcessorInterface = BatchProcessor()
            self.minireview_processor = MiniReviewProcessor(templates_dir=self.config.default_templates_dir)
            self.citemap_processor = CitemapProcessor(templates_dir=self.config.default_templates_dir)
            logger.info("✓ Legacy components initialized for backward compatibility")
            
            # NoteGenerator is intentionally removed from MCP workflow
            # It's only used for standalone/legacy operations, not MCP tool calls
            self.note_generator: Optional[NoteGeneratorInterface] = None
            logger.info("✗ NoteGenerator excluded from MCP workflow (AI integration architecture)")
            
        except Exception as e:
            logger.warning(f"Legacy component initialization failed (non-critical): {str(e)}")
        
        # Register MCP tools and resources
        try:
            self._register_tools()
            self._register_resources()
            logger.info("✓ MCP tools and resources registered successfully")
        except Exception as e:
            logger.error(f"Failed to register MCP tools: {str(e)}")
            raise
        
        # Validate component readiness
        self._validate_component_readiness()
        
        logger.info("🚀 ScholarsQuill MCP Server initialized successfully with AI integration architecture")
        logger.info("📋 Architecture: MCP server provides content + templates + instructions → Claude performs analysis")
    
    def _validate_component_readiness(self) -> None:
        """Validate that all required components are properly initialized and ready"""
        try:
            # Validate core AI integration components
            assert self.content_extractor is not None, "ContentExtractor not initialized"
            assert self.analysis_instructions is not None, "AnalysisInstructionsGenerator not initialized"
            assert self.template_loader is not None, "TemplateLoader not initialized"
            assert self.pdf_processor is not None, "PDFProcessor not initialized"
            
            # Test template loader functionality
            available_templates = self.template_loader.get_available_templates()
            assert len(available_templates) > 0, "No templates available"
            logger.info(f"✓ Templates available: {', '.join(available_templates)}")
            
            # Test analysis instructions functionality
            test_instructions = self.analysis_instructions.create_analysis_instructions("balanced", "standard")
            assert "focus_guidance" in test_instructions, "Analysis instructions not properly structured"
            logger.info("✓ Analysis instructions generator working correctly")
            
            # Verify configuration
            assert self.config.default_templates_dir is not None, "Templates directory not configured"
            assert self.config.default_output_dir is not None, "Output directory not configured"
            logger.info("✓ Configuration validated")
            
            logger.info("✅ All components validated and ready for AI integration workflow")
            
        except Exception as e:
            logger.error(f"❌ Component validation failed: {str(e)}")
            raise RuntimeError(f"Server initialization failed validation: {str(e)}")
    
    def _register_tools(self) -> None:
        """Register MCP tools with the server"""
        
        @self.server.tool()
        async def sq_note(
            target: str,
            focus: str = "balanced",
            depth: str = "standard",
            format: str = "markdown",
            batch: bool = False,
            output_dir: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Extract PDF content and provide templates for AI analysis.
            
            This tool extracts PDF content and returns it along with templates and analysis 
            instructions for Claude to perform intelligent content analysis and note generation.
            
            Args:
                target: Path to PDF file or directory (for batch processing)
                focus: Analysis focus (research, theory, review, method, balanced) - default: balanced
                depth: Analysis depth (quick, standard, deep) - default: standard
                format: Output format (markdown) - default: markdown
                batch: Enable batch processing for directories - default: False
                output_dir: Output directory for generated notes - default: literature-notes/
            
            Returns:
                Dict with PDF content, templates, and analysis instructions for Claude
            """
            return await self.extract_content_for_analysis(
                target=target,
                focus=focus,
                depth=depth,
                format=format,
                batch=batch,
                output_dir=output_dir
            )
        
        @self.server.tool()
        async def analyze_paper(
            paper_path: str
        ) -> Dict[str, Any]:
            """
            Analyze and classify a PDF paper without generating notes.
            
            Args:
                paper_path: Path to the PDF file to analyze
            
            Returns:
                Dict with paper classification, metadata, and analysis results
            """
            return await self.analyze_paper_type(paper_path)
        
        @self.server.tool()
        async def sq_codelang(
            target: str,
            field: str = "auto-detect",
            focus: str = "discourse",
            section_filter: str = "all",
            depth: str = "standard",
            batch: bool = False,
            keyword: str = None,
            output_dir: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Extract discourse patterns and domain-specific language from research papers.
            
            Analyzes how authors structure arguments, highlight topics, and use field-specific
            expressions. Identifies linguistic patterns and "code language" of academic discourse.
            
            Args:
                target: Path to PDF file or directory (for batch processing)
                field: Academic field (auto-detect, physics, cs, biology, etc.) - default: auto-detect
                focus: Analysis focus (discourse, architecture, terminology, rhetoric, sections, functions, summary) - default: discourse
                section_filter: Paper sections to analyze (all, introduction, methods, results, discussion) - default: all
                depth: Analysis depth (quick, standard, deep) - default: standard
                batch: Enable batch processing for directories - default: False
                keyword: Keyword for batch filename (Codelang_[keyword]_[focus].md) - default: auto-generated
                output_dir: Output directory for generated analysis - default: codelang-analysis/
            
            Returns:
                Dict with discourse patterns, linguistic analysis, and code language insights
            """
            return await self.extract_discourse_patterns(
                target=target,
                field=field,
                focus=focus,
                section_filter=section_filter,
                depth=depth,
                batch=batch,
                keyword=keyword,
                output_dir=output_dir
            )
        
        @self.server.tool()
        async def sq_citemap(
            target: str,
            batch: bool = False,
            keyword: Optional[str] = None,
            output_dir: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Create citation context maps and reference networks from PDF papers.
            
            Analyzes citation contexts, extracts reference relationships, and builds
            intellectual lineage networks showing how papers connect different ideas.
            
            Args:
                target: Path to PDF file or directory (for batch processing)
                batch: Enable batch processing with cross-reference analysis - default: False
                keyword: Keyword for batch filename (Citemap_[keyword]_[count].md) - default: auto-generated
                output_dir: Output directory for generated citemap - default: citemap-analysis/
            
            Returns:
                Dict with citation contexts, reference networks, and cross-paper analysis
            """
            return await self.create_citation_map(
                target=target,
                batch=batch,
                keyword=keyword,
                output_dir=output_dir
            )
        
        @self.server.tool()
        async def list_templates() -> Dict[str, Any]:
            """
            List available note templates and their descriptions.
            
            Returns:
                Dict with template information and focus area descriptions
            """
            return await self.get_available_templates()
    
    def _register_resources(self) -> None:
        """Register MCP resources with the server"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available ScholarsQuill resources"""
            resources = [
                Resource(
                    uri="scholarsquill://templates/",
                    name="Note Templates",
                    description="Available literature note templates for different focus areas",
                    mimeType="application/json"
                ),
                Resource(
                    uri="scholarsquill://config/",
                    name="Server Configuration",
                    description="Current server configuration and settings",
                    mimeType="application/json"
                )
            ]
            return resources
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read ScholarsQuill resources"""
            if uri == "scholarsquill://templates/":
                templates = await self.get_available_templates()
                return json.dumps(templates, indent=2)
            
            elif uri == "scholarsquill://config/":
                config_dict = {
                    "default_output_dir": self.config.default_output_dir,
                    "default_templates_dir": self.config.default_templates_dir,
                    "max_file_size_mb": self.config.max_file_size_mb,
                    "batch_size_limit": self.config.batch_size_limit,
                    "enable_caching": self.config.enable_caching,
                    "log_level": self.config.log_level
                }
                return json.dumps(config_dict, indent=2)
            
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
    
    async def extract_content_for_analysis(
        self,
        target: str,
        focus: str = "balanced",
        depth: str = "standard",
        format: str = "markdown",
        batch: bool = False,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract PDF content and provide structured data for Claude analysis
        
        Args:
            target: Path to PDF file or directory
            focus: Analysis focus type
            depth: Analysis depth level
            format: Output format
            batch: Whether to process in batch mode
            output_dir: Output directory for notes
        
        Returns:
            Dict with PDF content, templates, and analysis instructions for Claude
        """
        try:
            # Validate inputs
            if batch:
                return await self._extract_batch_content(target, focus, depth, format, output_dir)
            else:
                return await self._extract_single_file_content(target, focus, depth, format, output_dir)
        
        except Exception as e:
            logger.error(f"Error extracting content for analysis: {str(e)}")
            return self._create_error_response(e, "content_extraction")

    async def process_note_command(
        self,
        target: str,
        focus: str = "balanced",
        depth: str = "standard",
        format: str = "markdown",
        batch: bool = False,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process note command by extracting content and providing structured data for Claude analysis
        
        This method now focuses on content extraction and data preparation for AI analysis,
        rather than attempting internal note generation. It returns all necessary components
        for Claude to perform intelligent content analysis and template filling.
        
        Args:
            target: Path to PDF file or directory
            focus: Analysis focus type (research, theory, method, review, balanced)
            depth: Analysis depth level (quick, standard, deep)
            format: Output format (markdown)
            batch: Whether to process in batch mode
            output_dir: Output directory for generated notes
        
        Returns:
            Dict with PDF content, templates, and analysis instructions for Claude
        """
        try:
            logger.info(f"Processing note command: target={target}, focus={focus}, depth={depth}, batch={batch}")
            
            # Validate input parameters
            valid_focus_types = ["research", "theory", "method", "review", "balanced"]
            valid_depth_levels = ["quick", "standard", "deep"]
            valid_formats = ["markdown"]
            
            if focus not in valid_focus_types:
                raise ValueError(f"Invalid focus type '{focus}'. Must be one of: {valid_focus_types}")
            if depth not in valid_depth_levels:
                raise ValueError(f"Invalid depth level '{depth}'. Must be one of: {valid_depth_levels}")
            if format not in valid_formats:
                raise ValueError(f"Invalid format '{format}'. Must be one of: {valid_formats}")
            
            # Set default output directory if not specified
            if not output_dir:
                output_dir = self.config.default_output_dir
            
            # Ensure output directory exists
            ensure_directory(output_dir)
            
            # Use the new content extraction method that returns structured data for Claude
            return await self.extract_content_for_analysis(
                target=target,
                focus=focus,
                depth=depth,
                format=format,
                batch=batch,
                output_dir=output_dir
            )
        
        except Exception as e:
            logger.error(f"Error processing note command: {str(e)}")
            return self._create_error_response(e, "note_command_processing", target)
    
    async def _process_single_file(self, args: CommandArgs) -> Dict[str, Any]:
        """Process a single PDF file with comprehensive error handling and logging"""
        processing_start_time = asyncio.get_event_loop().time()
        file_path = None
        
        try:
            # Step 1: File validation
            logger.info(f"Starting file processing: {args.target}")
            file_path = Path(args.target)
            
            if not file_path.exists():
                logger.error(f"File not found: {args.target}")
                raise FileNotFoundError(f"PDF file not found: {args.target}")
            
            if not file_path.suffix.lower() == '.pdf':
                logger.error(f"Invalid file type: {file_path.suffix}")
                raise ValueError(f"File is not a PDF: {args.target}")
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.max_file_size_mb:
                logger.error(f"File too large: {file_size_mb:.1f}MB (max: {self.config.max_file_size_mb}MB)")
                raise ValueError(f"File too large: {file_size_mb:.1f}MB (max: {self.config.max_file_size_mb}MB)")
            
            logger.info(f"File validation passed - Size: {file_size_mb:.2f}MB")
            
            # Step 2: PDF text extraction
            logger.info("Extracting text from PDF...")
            extraction_start = asyncio.get_event_loop().time()
            
            try:
                text_content = self.pdf_processor.extract_text(str(file_path))
                if not text_content or len(text_content.strip()) < 100:
                    logger.warning("Extracted text is very short, PDF might be image-based or corrupted")
                
                extraction_time = asyncio.get_event_loop().time() - extraction_start
                logger.info(f"Text extraction completed in {extraction_time:.2f}s - Length: {len(text_content)} chars")
                
            except Exception as e:
                logger.error(f"Text extraction failed: {str(e)}")
                raise PDFProcessingError(f"Failed to extract text from PDF: {str(e)}")
            
            # Step 3: Metadata extraction
            logger.info("Extracting metadata from PDF...")
            metadata_start = asyncio.get_event_loop().time()
            
            try:
                metadata = self.pdf_processor.extract_metadata(str(file_path))
                metadata_time = asyncio.get_event_loop().time() - metadata_start
                logger.info(f"Metadata extraction completed in {metadata_time:.2f}s - Title: {metadata.title[:50]}...")
                
            except Exception as e:
                logger.error(f"Metadata extraction failed: {str(e)}")
                raise PDFProcessingError(f"Failed to extract metadata from PDF: {str(e)}")
            
            # Step 4: Content analysis
            logger.info(f"Analyzing content with focus: {args.focus.value}")
            analysis_start = asyncio.get_event_loop().time()
            
            try:
                analysis_result = self.content_analyzer.analyze_content(
                    text_content, args.focus.value
                )
                analysis_time = asyncio.get_event_loop().time() - analysis_start
                logger.info(f"Content analysis completed in {analysis_time:.2f}s - Type: {analysis_result.paper_type} (confidence: {analysis_result.confidence:.2f})")
                
            except Exception as e:
                logger.error(f"Content analysis failed: {str(e)}")
                raise ContentAnalysisError(f"Failed to analyze content: {str(e)}")
            
            # Step 5: Note generation
            logger.info(f"Generating note with depth: {args.depth.value}")
            generation_start = asyncio.get_event_loop().time()
            
            try:
                note_content = self.note_generator.generate_note(
                    text_content, metadata, args.focus.value, args.depth.value
                )
                generation_time = asyncio.get_event_loop().time() - generation_start
                logger.info(f"Note generation completed in {generation_time:.2f}s - Length: {len(note_content)} chars")
                
            except Exception as e:
                logger.error(f"Note generation failed: {str(e)}")
                raise NoteGenerationError(f"Failed to generate note: {str(e)}")
            
            # Step 6: File output
            logger.info("Writing note to file...")
            output_start = asyncio.get_event_loop().time()
            
            try:
                # Generate safe filename
                safe_title = "".join(c for c in metadata.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title[:50] if len(safe_title) > 50 else safe_title
                if not safe_title:
                    safe_title = f"paper_{metadata.year or 'unknown'}"
                
                filename = f"{safe_title}_literature_note.md"
                output_path = Path(args.output_dir) / filename
                
                # Ensure unique filename
                counter = 1
                while output_path.exists():
                    base_name = safe_title
                    filename = f"{base_name}_{counter}_literature_note.md"
                    output_path = Path(args.output_dir) / filename
                    counter += 1
                
                # Write note to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(note_content)
                
                output_time = asyncio.get_event_loop().time() - output_start
                total_time = asyncio.get_event_loop().time() - processing_start_time
                
                logger.info(f"File written successfully in {output_time:.2f}s: {output_path}")
                logger.info(f"Total processing time: {total_time:.2f}s")
                
            except Exception as e:
                logger.error(f"File output failed: {str(e)}")
                raise ProcessingError(f"Failed to write note file: {str(e)}")
            
            # Step 7: Compile successful result
            result = {
                "success": True,
                "note_content": note_content,
                "output_path": str(output_path),
                "source_path": str(file_path),
                "metadata": {
                    "title": metadata.title,
                    "first_author": metadata.first_author,
                    "authors": metadata.authors,
                    "year": metadata.year,
                    "citekey": metadata.citekey,
                    "journal": metadata.journal,
                    "doi": metadata.doi,
                    "page_count": metadata.page_count,
                    "abstract": metadata.abstract
                },
                "analysis": {
                    "paper_type": analysis_result.paper_type,
                    "confidence": analysis_result.confidence,
                    "key_concepts": analysis_result.key_concepts,
                    "sections_found": list(analysis_result.sections.keys()),
                    "equations_found": len(analysis_result.equations),
                    "methodologies_found": len(analysis_result.methodologies)
                },
                "processing_options": {
                    "focus": args.focus.value,
                    "depth": args.depth.value,
                    "format": args.format.value
                },
                "file_info": {
                    "size_mb": round(file_size_mb, 2),
                    "note_length": len(note_content),
                    "text_length": len(text_content)
                },
                "timing": {
                    "total_time_seconds": round(total_time, 2),
                    "extraction_time_seconds": round(extraction_time, 2),
                    "analysis_time_seconds": round(analysis_time, 2),
                    "generation_time_seconds": round(generation_time, 2)
                }
            }
            
            logger.info("Single file processing completed successfully")
            return result
        
        except (FileNotFoundError, ValueError, PDFProcessingError, ContentAnalysisError, NoteGenerationError) as e:
            # These are expected errors that should be returned to the user
            logger.error(f"Processing failed for {args.target}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "source_path": str(file_path) if file_path else args.target,
                "processing_stage": self._get_processing_stage_from_error(e)
            }
        
        except Exception as e:
            # Unexpected errors
            logger.exception(f"Unexpected error processing {args.target}: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__,
                "source_path": str(file_path) if file_path else args.target,
                "processing_stage": "unknown"
            }
    
    def _get_processing_stage_from_error(self, error: Exception) -> str:
        """Determine processing stage from error type"""
        if isinstance(error, (FileNotFoundError, ValueError)):
            return "file_validation"
        elif isinstance(error, PDFProcessingError):
            return "pdf_processing"
        elif isinstance(error, ContentAnalysisError):
            return "content_analysis"
        elif isinstance(error, NoteGenerationError):
            return "note_generation"
        else:
            return "unknown"
    
    async def _process_batch(self, args: CommandArgs) -> Dict[str, Any]:
        """Process multiple PDF files in batch mode with comprehensive error handling"""
        batch_start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Directory validation
            logger.info(f"Starting batch processing: {args.target}")
            dir_path = Path(args.target)
            
            if not dir_path.exists():
                logger.error(f"Directory not found: {args.target}")
                raise FileNotFoundError(f"Directory not found: {args.target}")
            
            if not dir_path.is_dir():
                logger.error(f"Target is not a directory: {args.target}")
                raise ValueError(f"Target is not a directory: {args.target}")
            
            # Step 2: Find PDF files
            pdf_files = list(dir_path.glob("*.pdf"))
            if not pdf_files:
                logger.warning(f"No PDF files found in directory: {args.target}")
                return {
                    "success": True,
                    "batch_results": [],
                    "summary": {
                        "total_files": 0,
                        "successful": 0,
                        "failed": 0,
                        "success_rate": 0,
                        "message": "No PDF files found in directory"
                    },
                    "processing_options": {
                        "focus": args.focus.value,
                        "depth": args.depth.value,
                        "format": args.format.value
                    },
                    "source_directory": str(dir_path),
                    "output_directory": args.output_dir
                }
            
            # Check batch size limit
            if len(pdf_files) > self.config.batch_size_limit:
                logger.error(f"Too many files: {len(pdf_files)} (max: {self.config.batch_size_limit})")
                raise ValueError(f"Too many files: {len(pdf_files)} (max: {self.config.batch_size_limit})")
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            # Step 3: Create processing options
            options = ProcessingOptions(
                focus=args.focus,
                depth=args.depth,
                format=args.format,
                batch=True,
                output_dir=args.output_dir
            )
            
            # Step 4: Process directory using batch processor
            logger.info("Starting batch processing with BatchProcessor...")
            processing_start = asyncio.get_event_loop().time()
            
            try:
                results = self.batch_processor.process_directory(str(dir_path), options)
                processing_time = asyncio.get_event_loop().time() - processing_start
                logger.info(f"Batch processing completed in {processing_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Batch processor failed: {str(e)}")
                raise BatchProcessingError(f"Batch processing failed: {str(e)}")
            
            # Step 5: Analyze results
            successful = [r for r in results if r.get("success", False)]
            failed = [r for r in results if not r.get("success", False)]
            
            # Log detailed results
            logger.info(f"Batch processing summary:")
            logger.info(f"  Total files: {len(results)}")
            logger.info(f"  Successful: {len(successful)}")
            logger.info(f"  Failed: {len(failed)}")
            
            if failed:
                logger.warning("Failed files:")
                for fail in failed[:5]:  # Log first 5 failures
                    logger.warning(f"  - {fail.get('source_path', 'unknown')}: {fail.get('error', 'unknown error')}")
                if len(failed) > 5:
                    logger.warning(f"  ... and {len(failed) - 5} more failures")
            
            # Step 6: Calculate statistics
            total_time = asyncio.get_event_loop().time() - batch_start_time
            success_rate = len(successful) / len(results) if results else 0
            
            # Collect timing statistics from successful results
            timing_stats = {}
            if successful:
                total_times = [r.get("timing", {}).get("total_time_seconds", 0) for r in successful]
                if total_times:
                    timing_stats = {
                        "average_per_file_seconds": sum(total_times) / len(total_times),
                        "fastest_file_seconds": min(total_times),
                        "slowest_file_seconds": max(total_times)
                    }
            
            # Step 7: Compile comprehensive result
            result = {
                "success": True,
                "batch_results": results,
                "summary": {
                    "total_files": len(results),
                    "successful": len(successful),
                    "failed": len(failed),
                    "success_rate": round(success_rate, 3),
                    "total_processing_time_seconds": round(total_time, 2)
                },
                "processing_options": {
                    "focus": args.focus.value,
                    "depth": args.depth.value,
                    "format": args.format.value
                },
                "source_directory": str(dir_path),
                "output_directory": args.output_dir,
                "timing_statistics": timing_stats,
                "error_summary": self._compile_error_summary(failed) if failed else None
            }
            
            logger.info(f"Batch processing completed successfully in {total_time:.2f}s")
            return result
        
        except (FileNotFoundError, ValueError, BatchProcessingError) as e:
            # Expected errors
            logger.error(f"Batch processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "source_directory": args.target,
                "processing_stage": "batch_setup"
            }
        
        except Exception as e:
            # Unexpected errors
            logger.exception(f"Unexpected error in batch processing: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected batch processing error: {str(e)}",
                "error_type": type(e).__name__,
                "source_directory": args.target,
                "processing_stage": "unknown"
            }
    
    def _compile_error_summary(self, failed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compile summary of errors from failed results"""
        error_types = {}
        error_stages = {}
        
        for result in failed_results:
            error_type = result.get("error_type", "unknown")
            error_stage = result.get("processing_stage", "unknown")
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            error_stages[error_stage] = error_stages.get(error_stage, 0) + 1
        
        return {
            "error_types": error_types,
            "error_stages": error_stages,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None,
            "most_common_stage": max(error_stages.items(), key=lambda x: x[1])[0] if error_stages else None
        }
    
    async def analyze_paper_type(self, paper_path: str) -> Dict[str, Any]:
        """Analyze and classify a paper without generating notes"""
        try:
            # Validate file exists
            file_path = Path(paper_path)
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {paper_path}")
            
            if not file_path.suffix.lower() == '.pdf':
                raise ValueError(f"File is not a PDF: {paper_path}")
            
            # Extract text and metadata
            text_content = self.pdf_processor.extract_text(str(file_path))
            metadata = self.pdf_processor.extract_metadata(str(file_path))
            
            # Classify paper type
            paper_type, confidence = self.content_analyzer.classify_paper_type(text_content)
            
            # Extract sections
            sections = self.content_analyzer.extract_sections(text_content)
            
            return {
                "success": True,
                "paper_type": paper_type,
                "confidence_score": confidence,
                "metadata": {
                    "title": metadata.title,
                    "first_author": metadata.first_author,
                    "authors": metadata.authors,
                    "year": metadata.year,
                    "journal": metadata.journal,
                    "page_count": metadata.page_count
                },
                "sections_detected": list(sections.keys()),
                "text_length": len(text_content),
                "source_path": str(file_path)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing paper: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _extract_single_file_content(
        self,
        target: str,
        focus: str,
        depth: str,
        format: str,
        output_dir: Optional[str]
    ) -> Dict[str, Any]:
        """Extract content from a single PDF file for Claude analysis"""
        try:
            # Step 1: Validate file
            file_path = Path(target)
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {target}")
            
            if not file_path.suffix.lower() == '.pdf':
                raise ValueError(f"File is not a PDF: {target}")
            
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.max_file_size_mb:
                raise ValueError(f"File too large: {file_size_mb:.1f}MB (max: {self.config.max_file_size_mb}MB)")
            
            logger.info(f"Extracting content for Claude analysis: {target}")
            
            # Step 2: Extract PDF content and metadata
            content_data = await self.content_extractor.extract_for_analysis(str(file_path))
            
            # Step 3: Load appropriate template
            template_data = await self.template_loader.load_template(focus)
            
            # Step 4: Generate analysis instructions
            analysis_instructions = self.analysis_instructions.create_analysis_instructions(focus, depth)
            
            # Step 5: Prepare output directory info
            if not output_dir:
                output_dir = self.config.default_codelang_output_dir
            
            # Generate suggested filename
            metadata = content_data.get("metadata", {})
            safe_title = self._generate_safe_filename(metadata.get("title", "paper"))
            suggested_filename = f"{safe_title}_literature_note.md"
            
            # Step 6: Return structured data for Claude
            return {
                "success": True,
                "action_required": "analyze_content",
                "pdf_content": content_data["raw_content"],
                "structured_content": content_data["structured_content"],
                "metadata": content_data["metadata"],
                "template": template_data,
                "analysis_instructions": analysis_instructions,
                "processing_options": {
                    "focus": focus,
                    "depth": depth,
                    "format": format
                },
                "output_info": {
                    "suggested_directory": output_dir,
                    "suggested_filename": suggested_filename,
                    "full_suggested_path": str(Path(output_dir) / suggested_filename)
                },
                "file_info": {
                    "source_path": str(file_path),
                    "size_mb": round(file_size_mb, 2),
                    "content_stats": content_data["content_stats"]
                },
                "message": (
                    f"PDF content extracted successfully from '{file_path.name}'. "
                    f"\\n\\n**ANALYSIS TASK:**\\n"
                    f"1. Read the entire PDF content thoroughly\\n"
                    f"2. Follow the comprehensive analysis instructions provided\\n"
                    f"3. Focus on {focus} aspects with {depth} level of detail\\n"
                    f"4. Fill the template with actual content from the paper (NO placeholders)\\n"
                    f"5. Use specific evidence and examples from the paper\\n"
                    f"6. Maintain academic tone and ensure accuracy\\n\\n"
                    f"The template includes embedded instructions for each section. "
                    f"Please produce a complete literature note following the template structure "
                    f"and analysis guidelines provided."
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to extract content from {target}: {str(e)}")
            return self._create_error_response(e, "single_file_extraction", target)
    
    async def _extract_batch_content(
        self,
        target: str,
        focus: str,
        depth: str,
        format: str,
        output_dir: Optional[str]
    ) -> Dict[str, Any]:
        """Extract content from multiple PDF files for Claude analysis"""
        try:
            # Step 1: Validate directory
            dir_path = Path(target)
            if not dir_path.exists():
                raise FileNotFoundError(f"Directory not found: {target}")
            
            if not dir_path.is_dir():
                raise ValueError(f"Target is not a directory: {target}")
            
            # Step 2: Find PDF files
            pdf_files = list(dir_path.glob("*.pdf"))
            if not pdf_files:
                return {
                    "success": True,
                    "action_required": "none",
                    "message": "No PDF files found in directory",
                    "batch_results": [],
                    "summary": {
                        "total_files": 0,
                        "files_found": []
                    }
                }
            
            # Check batch size limit
            if len(pdf_files) > self.config.batch_size_limit:
                raise ValueError(f"Too many files: {len(pdf_files)} (max: {self.config.batch_size_limit})")
            
            logger.info(f"Extracting content from {len(pdf_files)} PDF files for batch analysis")
            
            # Step 3: Load template once for all files
            template_data = await self.template_loader.load_template(focus)
            
            # Step 4: Generate analysis instructions once for all files
            analysis_instructions = self.analysis_instructions.create_analysis_instructions(focus, depth)
            
            # Step 5: Extract content from each file
            batch_results = []
            successful_extractions = 0
            
            for pdf_file in pdf_files:
                try:
                    # Extract content for this file
                    content_data = await self.content_extractor.extract_for_analysis(str(pdf_file))
                    
                    # Generate suggested filename
                    metadata = content_data.get("metadata", {})
                    safe_title = self._generate_safe_filename(metadata.get("title", pdf_file.stem))
                    suggested_filename = f"{safe_title}_literature_note.md"
                    
                    file_result = {
                        "success": True,
                        "source_file": str(pdf_file),
                        "pdf_content": content_data["raw_content"],
                        "structured_content": content_data["structured_content"],
                        "metadata": content_data["metadata"],
                        "suggested_filename": suggested_filename,
                        "content_stats": content_data["content_stats"]
                    }
                    
                    batch_results.append(file_result)
                    successful_extractions += 1
                    
                except Exception as e:
                    logger.error(f"Failed to extract content from {pdf_file}: {str(e)}")
                    file_result = {
                        "success": False,
                        "source_file": str(pdf_file),
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    batch_results.append(file_result)
            
            # Step 6: Prepare output directory info
            if not output_dir:
                output_dir = self.config.default_output_dir
            
            # Step 7: Return structured batch data for Claude
            return {
                "success": True,
                "action_required": "analyze_batch_content",
                "batch_results": batch_results,
                "template": template_data,
                "analysis_instructions": analysis_instructions,
                "processing_options": {
                    "focus": focus,
                    "depth": depth,
                    "format": format,
                    "batch": True
                },
                "output_info": {
                    "suggested_directory": output_dir
                },
                "summary": {
                    "total_files": len(pdf_files),
                    "successful_extractions": successful_extractions,
                    "failed_extractions": len(pdf_files) - successful_extractions,
                    "success_rate": successful_extractions / len(pdf_files) if pdf_files else 0
                },
                "message": (
                    f"Batch extraction complete: {successful_extractions}/{len(pdf_files)} PDF files processed successfully. "
                    f"\\n\\n**BATCH ANALYSIS TASK:**\\n"
                    f"1. Analyze each PDF file's content individually\\n"
                    f"2. Follow the comprehensive analysis instructions for each file\\n"
                    f"3. Focus on {focus} aspects with {depth} level of detail\\n"
                    f"4. Generate a separate literature note for each file\\n"
                    f"5. Fill templates with actual content (NO placeholders)\\n"
                    f"6. Use specific evidence from each paper\\n"
                    f"7. Maintain consistent quality across all notes\\n\\n"
                    f"Process each file independently using the same template and analysis guidelines. "
                    f"Each note should be complete and self-contained."
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to extract batch content from {target}: {str(e)}")
            return self._create_error_response(e, "batch_extraction", target)
    
    def _generate_safe_filename(self, title: str) -> str:
        """Generate a safe filename from paper title"""
        if not title:
            return "paper"
        
        # Keep only alphanumeric characters, spaces, hyphens, and underscores
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        
        # Limit length and handle empty results
        safe_title = safe_title[:50] if len(safe_title) > 50 else safe_title
        if not safe_title:
            safe_title = "paper"
        
        # Replace spaces with underscores
        safe_title = safe_title.replace(' ', '_')
        
        return safe_title
    
    def _create_error_response(self, error: Exception, context: str, target: str = None) -> Dict[str, Any]:
        """
        Create comprehensive error response with structured guidance for Claude
        
        Args:
            error: The exception that occurred
            context: Context of the error (e.g., "content_extraction", "template_loading")
            target: Source file/directory path
            
        Returns:
            Dict with comprehensive error information and Claude-specific guidance
        """
        error_type = type(error).__name__
        
        # Determine error category for Claude guidance
        claude_error_type = self._determine_claude_error_type(error, context)
        
        # Get comprehensive guidance for Claude
        claude_guidance = self.analysis_instructions.create_error_guidance(
            claude_error_type,
            context={
                "error_type": error_type,
                "context": context,
                "target": target,
                "error_message": str(error)
            }
        )
        
        # Create fallback instructions if normal processing failed
        fallback_instructions = self.analysis_instructions.create_fallback_instructions(
            focus="balanced",  # Default to balanced focus for fallback
            depth="standard",  # Default to standard depth for fallback
            fallback_reason=claude_error_type
        )
        
        # Generate user-friendly suggestions
        user_suggestions = self._generate_user_suggestions(error, context)
        
        # Create comprehensive error response
        error_response = {
            "success": False,
            "error": str(error),
            "error_type": error_type,
            "context": context,
            "source_path": target,
            "timestamp": asyncio.get_event_loop().time(),
            
            # User-facing guidance
            "user_suggestions": user_suggestions,
            "troubleshooting_tips": self._get_troubleshooting_tips(error),
            
            # Claude-specific guidance
            "claude_guidance": claude_guidance,
            "fallback_instructions": fallback_instructions,
            "analysis_instructions": self._create_emergency_analysis_instructions(claude_error_type),
            
            # Comprehensive message for Claude
            "message": self._create_claude_error_message(error, context, claude_guidance, target)
        }
        
        return error_response
    
    def _determine_claude_error_type(self, error: Exception, context: str) -> str:
        """
        Determine the appropriate Claude error type based on the exception and context
        
        Args:
            error: The exception that occurred
            context: Error context
            
        Returns:
            String identifying the error type for Claude guidance
        """
        error_str = str(error).lower()
        
        if isinstance(error, FileNotFoundError):
            return "file_access_error"
        elif isinstance(error, PermissionError):
            return "file_access_error"
        elif isinstance(error, PDFProcessingError):
            if "corrupted" in error_str or "extraction" in error_str:
                return "corrupted_pdf"
            else:
                return "unsupported_format"
        elif isinstance(error, ValueError):
            if "not a pdf" in error_str:
                return "unsupported_format"
            elif "too large" in error_str:
                return "file_access_error"
            elif "short" in error_str or "insufficient" in error_str:
                return "insufficient_content"
            else:
                return "unsupported_format"
        elif isinstance(error, TemplateError):
            return "template_error"
        elif isinstance(error, ContentAnalysisError):
            return "insufficient_content"
        elif "network" in error_str or "connection" in error_str:
            return "network_error"
        elif "focus" in error_str or "mismatch" in error_str:
            return "focus_mismatch"
        else:
            return "insufficient_content"  # Default fallback
    
    def _generate_user_suggestions(self, error: Exception, context: str) -> List[str]:
        """Generate user-friendly troubleshooting suggestions"""
        suggestions = []
        
        if isinstance(error, FileNotFoundError):
            suggestions = [
                "Check that the PDF file or directory exists",
                "Verify the file path is correct and accessible",
                "Ensure you have read permissions for the file/directory"
            ]
        elif isinstance(error, ValueError) and "not a PDF" in str(error):
            suggestions = [
                "Ensure the file has a .pdf extension",
                "Verify the file is actually a PDF document",
                "Try converting the file to PDF format first"
            ]
        elif isinstance(error, ValueError) and "too large" in str(error):
            suggestions = [
                f"File exceeds maximum size limit of {self.config.max_file_size_mb}MB",
                "Try with a smaller PDF file",
                "Consider splitting large documents into smaller parts",
                "Compress the PDF to reduce file size"
            ]
        elif isinstance(error, PDFProcessingError):
            suggestions = [
                "The PDF file may be corrupted or password-protected",
                "Try with a different PDF file",
                "Ensure the PDF contains extractable text (not just images)",
                "If the PDF is image-based, consider using OCR preprocessing"
            ]
        elif isinstance(error, TemplateError):
            suggestions = [
                "Check that the template directory exists and is accessible",
                "Verify template files are present and properly formatted",
                "Try using the default 'balanced' template"
            ]
        else:
            suggestions = [
                "Check that the file is a valid, readable PDF",
                "Try with a different PDF file",
                "Ensure you have proper file permissions",
                "Verify the file is not corrupted or encrypted"
            ]
        
        return suggestions
    
    def _get_troubleshooting_tips(self, error: Exception) -> List[str]:
        """Get additional troubleshooting tips for the user"""
        tips = []
        
        if isinstance(error, PDFProcessingError):
            tips = [
                "For image-based PDFs, text extraction may be limited",
                "Consider using PDFs with selectable text for best results",
                "Password-protected PDFs need to be unlocked before processing"
            ]
        elif isinstance(error, FileNotFoundError):
            tips = [
                "Use absolute file paths to avoid path resolution issues",
                "Check that the file hasn't been moved or renamed recently"
            ]
        elif isinstance(error, ValueError) and "too large" in str(error):
            tips = [
                "Large academic papers can be processed by splitting them into sections",
                "Consider extracting specific chapters or sections if the full document is too large"
            ]
        
        return tips
    
    def _create_emergency_analysis_instructions(self, error_type: str) -> Dict[str, Any]:
        """Create emergency analysis instructions for Claude when normal processing fails"""
        return {
            "emergency_mode": True,
            "error_type": error_type,
            "instructions": [
                "Work with whatever content is available from the extraction attempt",
                "Clearly indicate sections where analysis is limited due to errors",
                "Provide the most comprehensive analysis possible given the constraints",
                "Use fallback approaches and note all limitations in your response",
                "Focus on extracting maximum value from any readable content"
            ],
            "quality_expectations": "Provide useful analysis despite technical limitations, with clear documentation of constraints and adaptations made"
        }
    
    def _create_claude_error_message(self, error: Exception, context: str, claude_guidance: Dict[str, Any], target: str = None) -> str:
        """Create a comprehensive error message specifically for Claude"""
        error_type = type(error).__name__
        
        base_message = f"""
**ERROR ENCOUNTERED**: {error_type} in {context}

**SITUATION**: {claude_guidance.get('primary_guidance', 'An error occurred during processing')}

**ANALYSIS INSTRUCTIONS FOR CLAUDE**:
{chr(10).join(f"- {instruction}" for instruction in claude_guidance.get('analysis_approach', []))}

**TEMPLATE ADAPTATIONS**:
{chr(10).join(f"- {adaptation}" for adaptation in claude_guidance.get('template_adaptations', []))}

**QUALITY EXPECTATIONS**: {claude_guidance.get('quality_expectations', 'Provide the best possible analysis given the limitations')}

**SOURCE**: {target or 'Unknown'}
**CONTEXT**: {context}
**ERROR DETAILS**: {str(error)}

Please proceed with analysis using the guidance above, clearly noting any limitations or adaptations required due to this error.
"""
        
        return base_message.strip()
    
    def _create_comprehensive_analysis_message(self, focus: str, depth: str, target: str) -> str:
        """Create comprehensive analysis message for successful content extraction"""
        file_path = Path(target)
        
        message = f"""**PDF CONTENT EXTRACTED SUCCESSFULLY** from '{file_path.name}'

**ANALYSIS TASK FOR CLAUDE:**

**Step 1: Content Understanding**
- Read the entire PDF content thoroughly before beginning analysis
- Understand the paper's structure, main arguments, and methodology
- Identify key sections relevant to the {focus} focus area

**Step 2: Analysis Guidelines**
- Follow the comprehensive analysis instructions provided in the analysis_instructions field
- Focus specifically on {focus} aspects with {depth} level of detail
- Extract information according to the focus-specific guidelines and depth requirements

**Step 3: Template Completion**
- Use the provided template structure as your guide
- Fill ALL sections with actual content from the paper (NO placeholder text)
- Follow the HTML comment instructions within each template section
- Ensure each section contains meaningful analysis derived from the paper

**Step 4: Quality Requirements**
- Use specific evidence and examples from the paper to support your analysis
- Include direct quotes when they effectively illustrate key points
- Provide page references when possible for important claims
- Maintain academic tone and ensure accuracy throughout
- Create a self-contained note that's comprehensible without the original paper

**Step 5: Focus-Specific Emphasis**
- For {focus} focus: Pay special attention to the key areas outlined in the analysis instructions
- Adapt section depth and detail to match the {depth} analysis level
- Ensure your analysis aligns with the specific focus requirements

**IMPORTANT REMINDERS:**
- The template includes detailed HTML comments with section-specific instructions
- Follow these embedded instructions carefully for each section
- Produce a complete, professional literature note
- Replace ALL template placeholders with actual analysis content

Please proceed with your analysis using the PDF content, template, and comprehensive instructions provided."""
        
        return message
    
    def _detect_edge_cases(self, content_data: Dict[str, Any], target: str, focus: str) -> Dict[str, Any]:
        """
        Detect edge cases in the content and provide appropriate guidance for Claude
        
        Args:
            content_data: Extracted content data
            target: Source file path
            focus: Analysis focus type
            
        Returns:
            Dict with edge case information and guidance
        """
        edge_cases = []
        warnings = []
        adaptations = []
        severity_levels = []
        
        raw_content = content_data.get("raw_content", "")
        content_stats = content_data.get("content_stats", {})
        
        # Check for short content
        if len(raw_content.strip()) < 500:
            edge_cases.append("short_content")
            warnings.append("Document contains very limited content for comprehensive analysis")
            adaptations.append("Focus on extracting maximum value from available content")
            severity_levels.append("high")
        elif len(raw_content.strip()) < 2000:
            edge_cases.append("short_content")
            warnings.append("Document content is shorter than typical academic papers")
            adaptations.append("Adapt analysis depth to match available content")
            severity_levels.append("medium")
        
        # Check for mixed language content
        non_ascii_ratio = sum(1 for c in raw_content if ord(c) > 127) / max(len(raw_content), 1)
        if non_ascii_ratio > 0.1:
            edge_cases.append("mixed_language")
            warnings.append("Document contains significant non-English or special character content")
            adaptations.append("Focus analysis on clearly readable English portions")
            severity_levels.append("medium")
        
        # Check for highly technical content
        technical_indicators = ["algorithm", "equation", "formula", "theorem", "proof", "matrix", "coefficient"]
        technical_count = sum(1 for indicator in technical_indicators if indicator in raw_content.lower())
        if technical_count > 20:
            edge_cases.append("technical_content")
            warnings.append("Document contains highly technical or specialized content")
            adaptations.append("Focus on general principles and broader implications")
            severity_levels.append("low")
        
        # Check for image-heavy documents (based on low text extraction)
        if content_stats.get("word_count", 0) < 1000 and Path(target).stat().st_size > 1000000:  # Large file, few words
            edge_cases.append("image_heavy")
            warnings.append("Document appears to be image-heavy with limited extractable text")
            adaptations.append("Focus on text-based content and note visual content limitations")
            severity_levels.append("high")
        
        # Check for old format documents (based on formatting patterns)
        old_format_indicators = ["scanned", "typewriter", "dot matrix"]
        if any(indicator in raw_content.lower() for indicator in old_format_indicators):
            edge_cases.append("old_format")
            warnings.append("Document appears to use older formatting or may be scanned")
            adaptations.append("Adapt to document's native structure and focus on content extraction")
            severity_levels.append("medium")
        
        # Check for focus mismatch
        focus_keywords = {
            "research": ["study", "experiment", "participants", "results", "methodology"],
            "theory": ["theory", "model", "framework", "conceptual", "theoretical"],
            "method": ["method", "approach", "technique", "procedure", "algorithm"],
            "review": ["review", "literature", "synthesis", "meta-analysis", "systematic"]
        }
        
        if focus in focus_keywords:
            focus_word_count = sum(1 for keyword in focus_keywords[focus] 
                                 if keyword in raw_content.lower())
            total_words = content_stats.get("word_count", 1)
            focus_ratio = focus_word_count / max(total_words / 100, 1)  # Per 100 words
            
            if focus_ratio < 0.5:  # Less than 0.5 focus keywords per 100 words
                edge_cases.append("focus_mismatch")
                warnings.append(f"Document content may not align well with {focus} focus area")
                adaptations.append(f"Adapt analysis to emphasize available {focus}-related content")
                severity_levels.append("medium")
        
        # Determine overall severity
        if not edge_cases:
            overall_severity = "none"
        elif "high" in severity_levels:
            overall_severity = "high"
        elif severity_levels.count("medium") >= 2:
            overall_severity = "high"
        elif "medium" in severity_levels:
            overall_severity = "medium"
        else:
            overall_severity = "low"
        
        # Generate comprehensive guidance for detected edge cases
        edge_case_guidance = {}
        for case_type, severity in zip(edge_cases, severity_levels):
            guidance = self.analysis_instructions.create_edge_case_guidance(case_type, severity)
            edge_case_guidance[case_type] = guidance
        
        # Create response
        has_edge_cases = len(edge_cases) > 0
        primary_warning = warnings[0] if warnings else None
        
        return {
            "has_edge_cases": has_edge_cases,
            "edge_cases": edge_cases,
            "warnings": warnings,
            "adaptations": adaptations,
            "severity": overall_severity,
            "primary_warning": primary_warning,
            "guidance": edge_case_guidance,
            "content_analysis": {
                "content_length": len(raw_content),
                "word_count": content_stats.get("word_count", 0),
                "non_ascii_ratio": round(non_ascii_ratio, 3),
                "technical_indicators": technical_count,
                "file_size_mb": round(Path(target).stat().st_size / (1024 * 1024), 2)
            }
        }
    
    async def _extract_single_file_content(
        self,
        target: str,
        focus: str = "balanced",
        depth: str = "standard",
        format: str = "markdown",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract content from a single PDF file for Claude analysis
        
        Args:
            target: Path to PDF file
            focus: Analysis focus type
            depth: Analysis depth level
            format: Output format
            output_dir: Output directory for notes
        
        Returns:
            Dict with PDF content, templates, and analysis instructions for Claude
        """
        try:
            logger.info(f"Extracting content for AI analysis: {target}")
            
            # Step 1: Extract PDF content using ContentExtractor
            content_data = await self.content_extractor.extract_for_analysis(target)
            
            # Step 2: Load appropriate template
            template_data = await self.template_loader.load_template(focus)
            
            # Step 3: Generate analysis instructions for Claude
            analysis_instructions = self.analysis_instructions.create_analysis_instructions(focus, depth)
            
            # Step 4: Detect edge cases and provide guidance
            edge_case_info = self._detect_edge_cases(content_data, target, focus)
            
            # Step 5: Return structured data for Claude to analyze
            response = {
                "success": True,
                "action_required": "analyze_content",
                "pdf_content": content_data["raw_content"],
                "structured_content": content_data["structured_content"],
                "metadata": content_data["metadata"],
                "content_stats": content_data["content_stats"],
                "template": template_data,
                "analysis_instructions": analysis_instructions,
                "focus": focus,
                "depth": depth,
                "format": format,
                "output_dir": output_dir or self.config.default_output_dir,
                "source_path": target,
                "message": self._create_comprehensive_analysis_message(focus, depth, target)
            }
            
            # Add edge case guidance if detected
            if edge_case_info["has_edge_cases"]:
                response["edge_case_guidance"] = edge_case_info["guidance"]
                response["edge_case_warnings"] = edge_case_info["warnings"]
                response["analysis_adaptations"] = edge_case_info["adaptations"]
                response["message"] += f"\n\n**EDGE CASE DETECTED**: {edge_case_info['primary_warning']}\n\nPlease follow the additional edge case guidance provided."
            
            return response
            
        except Exception as e:
            logger.error(f"Content extraction failed for {target}: {str(e)}")
            return self._create_error_response(e, "content_extraction", target)
    
    async def _extract_batch_content(
        self,
        target: str,
        focus: str = "balanced",
        depth: str = "standard",
        format: str = "markdown",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract content from multiple PDF files for Claude analysis
        
        Args:
            target: Path to directory containing PDF files
            focus: Analysis focus type
            depth: Analysis depth level
            format: Output format
            output_dir: Output directory for notes
        
        Returns:
            Dict with batch processing results for Claude
        """
        try:
            logger.info(f"Starting batch content extraction: {target}")
            
            # Step 1: Validate directory
            dir_path = Path(target)
            if not dir_path.exists():
                raise FileNotFoundError(f"Directory not found: {target}")
            
            if not dir_path.is_dir():
                raise ValueError(f"Target is not a directory: {target}")
            
            # Step 2: Find PDF files
            pdf_files = list(dir_path.glob("*.pdf"))
            if not pdf_files:
                return {
                    "success": True,
                    "action_required": "none",
                    "batch_results": [],
                    "message": "No PDF files found in directory",
                    "source_directory": target,
                    "total_files": 0
                }
            
            # Check batch size limit
            if len(pdf_files) > self.config.batch_size_limit:
                raise ValueError(f"Too many files: {len(pdf_files)} (max: {self.config.batch_size_limit})")
            
            logger.info(f"Found {len(pdf_files)} PDF files for batch processing")
            
            # Step 3: Process each file
            batch_results = []
            successful = 0
            failed = 0
            
            for pdf_file in pdf_files:
                try:
                    result = await self._extract_single_file_content(
                        str(pdf_file), focus, depth, format, output_dir
                    )
                    batch_results.append(result)
                    
                    if result.get("success", False):
                        successful += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    logger.error(f"Failed to process {pdf_file}: {str(e)}")
                    error_result = self._create_error_response(e, "batch_file_processing", str(pdf_file))
                    batch_results.append(error_result)
                    failed += 1
            
            # Step 4: Load template for batch processing guidance
            template_data = await self.template_loader.load_template(focus)
            
            # Step 5: Generate batch analysis instructions
            batch_instructions = self.analysis_instructions.create_batch_analysis_instructions(focus, depth, len(pdf_files))
            
            return {
                "success": True,
                "action_required": "analyze_batch_content",
                "batch_results": batch_results,
                "template": template_data,
                "analysis_instructions": batch_instructions,
                "focus": focus,
                "depth": depth,
                "format": format,
                "output_dir": output_dir or self.config.default_output_dir,
                "source_directory": target,
                "summary": {
                    "total_files": len(pdf_files),
                    "successful_extractions": successful,
                    "failed_extractions": failed,
                    "success_rate": successful / len(pdf_files) if pdf_files else 0
                },
                "message": f"Batch content extraction completed. {successful}/{len(pdf_files)} files processed successfully. Please analyze each paper's content and generate literature notes."
            }
            
        except Exception as e:
            logger.error(f"Batch content extraction failed: {str(e)}")
            return self._create_error_response(e, "batch_content_extraction", target)
    
    async def get_available_templates(self) -> Dict[str, Any]:
        """Get information about available note templates"""
        try:
            templates = {
                "research": {
                    "name": "Research Paper",
                    "description": "Comprehensive analysis template for research papers",
                    "focus": "research",
                    "sections": [
                        "Citation",
                        "Executive Summary",
                        "Research Problem",
                        "Key Findings",
                        "Methodology",
                        "Implications",
                        "Limitations",
                        "Future Research Directions"
                    ]
                },
                "theory": {
                    "name": "Theoretical Paper",
                    "description": "Template emphasizing theoretical frameworks and mathematical models",
                    "focus": "theory",
                    "sections": [
                        "Citation",
                        "Theoretical Framework",
                        "Key Concepts",
                        "Mathematical Models",
                        "Equations and Formulations",
                        "Theoretical Contributions",
                        "Applications"
                    ]
                },
                "review": {
                    "name": "Literature Review",
                    "description": "Comprehensive template for literature review and survey papers",
                    "focus": "review",
                    "sections": [
                        "Citation",
                        "Review Scope",
                        "Research Categories",
                        "Chronological Structure",
                        "Key Themes",
                        "Research Gaps",
                        "Future Perspectives"
                    ]
                },
                "method": {
                    "name": "Methodology Paper",
                    "description": "Template focusing on experimental procedures and methodological approaches",
                    "focus": "method",
                    "sections": [
                        "Citation",
                        "Methodological Overview",
                        "Materials and Methods",
                        "Experimental Design",
                        "Statistical Analysis",
                        "Validation Approaches",
                        "Technical Implementation"
                    ]
                },
                "balanced": {
                    "name": "Balanced Analysis",
                    "description": "General-purpose template covering all aspects",
                    "focus": "balanced",
                    "sections": [
                        "Citation",
                        "Summary",
                        "Key Contributions",
                        "Methodology",
                        "Results",
                        "Discussion",
                        "Implications"
                    ]
                }
            }
            
            return {
                "success": True,
                "templates": templates,
                "focus_types": [focus.value for focus in FocusType],
                "depth_levels": [depth.value for depth in DepthType],
                "supported_formats": [fmt.value for fmt in FormatType]
            }
        
        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    # Codelang Focus Mapping
    CODELANG_FOCUS_MAPPING = {
        "discourse": "full",  # All sections
        "architecture": [
            "argument_structure", "topic_highlighting", "logical_transitions"
        ],
        "terminology": [
            "domain_terminology", "mathematical_language", "methodological_expressions"
        ],
        "rhetoric": [
            "evidence_presentation", "authority_expressions", "contribution_claims"
        ],
        "sections": [
            "introduction_patterns", "methods_patterns", "results_patterns", "discussion_patterns"
        ],
        "functions": [
            "linguistic_functions", "discovered_functions"
        ],
        "summary": [
            "primary_strategy", "field_conventions", "language_innovations", "frequency_analysis"
        ]
    }
    
    async def extract_discourse_patterns(
        self,
        target: str,
        field: str = "auto-detect",
        focus: str = "discourse",
        section_filter: str = "all",
        depth: str = "standard",
        batch: bool = False,
        keyword: str = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract discourse patterns and code language from research papers
        
        Args:
            target: Path to PDF file or directory
            field: Academic field for context
            focus: Analysis focus type
            section_filter: Which sections to analyze
            depth: Analysis depth
            batch: Whether to process multiple files
            output_dir: Output directory
        
        Returns:
            Dict with discourse analysis results
        """
        try:
            logger.info(f"Starting codelang analysis: target={target}, focus={focus}, batch={batch}")
            
            # Set default output directory
            if not output_dir:
                output_dir = self.config.default_codelang_output_dir
            
            # Ensure output directory exists
            ensure_directory(output_dir)
            
            if batch:
                return await self._extract_batch_discourse_patterns(
                    target, field, focus, section_filter, depth, keyword, output_dir
                )
            else:
                return await self._extract_single_discourse_patterns(
                    target, field, focus, section_filter, depth, output_dir
                )
        
        except Exception as e:
            logger.error(f"Error in discourse pattern extraction: {str(e)}")
            return self._create_error_response(e, "discourse_extraction", target)
    
    async def _extract_single_discourse_patterns(
        self,
        target: str,
        field: str,
        focus: str,
        section_filter: str,
        depth: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """Extract discourse patterns from a single PDF file"""
        try:
            # Step 1: Extract PDF content
            content_data = await self.content_extractor.extract_for_analysis(target)
            
            # Step 2: Load codelang template
            template_data = await self.template_loader.load_template("codelang")
            
            # Step 3: Generate discourse analysis instructions
            analysis_instructions = self.analysis_instructions.create_discourse_analysis_instructions(
                focus, depth, field, section_filter
            )
            
            # Step 4: Filter template based on focus
            focused_template = self._filter_template_by_focus(template_data, focus)
            
            # Step 5: Generate output filename
            metadata = content_data.get("metadata", {})
            filename = self._generate_codelang_filename(metadata, focus)
            
            return {
                "success": True,
                "action_required": "analyze_discourse_patterns",
                "pdf_content": content_data["raw_content"],
                "structured_content": content_data["structured_content"],
                "metadata": content_data["metadata"],
                "template": focused_template,
                "analysis_instructions": analysis_instructions,
                "focus": focus,
                "field": field,
                "section_filter": section_filter,
                "depth": depth,
                "output_info": {
                    "suggested_directory": output_dir,
                    "suggested_filename": filename,
                    "full_suggested_path": str(Path(output_dir) / filename)
                },
                "message": f"Single PDF ready for codelang analysis with focus on {focus}. Generate discourse pattern analysis."
            }
            
        except Exception as e:
            logger.error(f"Single discourse extraction failed: {str(e)}")
            return self._create_error_response(e, "single_discourse_extraction", target)
    
    async def _extract_batch_discourse_patterns(
        self,
        target: str,
        field: str,
        focus: str,
        section_filter: str,
        depth: str,
        keyword: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Extract discourse patterns from multiple PDFs and combine into single analysis
        
        Unlike sq:note batch processing, this creates ONE combined output file
        analyzing patterns across all papers.
        """
        try:
            # Step 1: Handle file list or directory
            if "," in target:
                # Comma-separated file list
                file_paths = [path.strip() for path in target.split(",")]
                pdf_files = []
                for file_path in file_paths:
                    pdf_path = Path(file_path)
                    if pdf_path.exists() and pdf_path.suffix.lower() == '.pdf':
                        pdf_files.append(pdf_path)
                    else:
                        logger.warning(f"Skipping invalid/missing file: {file_path}")
            else:
                # Directory path
                dir_path = Path(target)
                if not dir_path.exists() or not dir_path.is_dir():
                    raise ValueError(f"Invalid directory: {target}")
                pdf_files = list(dir_path.glob("*.pdf"))
            
            if not pdf_files:
                return {
                    "success": True,
                    "action_required": "none", 
                    "message": "No valid PDF files found",
                    "batch_results": [],
                    "total_files": 0
                }
            
            # Check batch size limit
            if len(pdf_files) > self.config.batch_size_limit:
                raise ValueError(f"Too many files: {len(pdf_files)} (max: {self.config.batch_size_limit})")
            
            logger.info(f"Processing {len(pdf_files)} PDFs for combined codelang analysis")
            
            # Step 2: Extract content from all PDFs
            all_content = []
            all_metadata = []
            successful_files = []
            failed_files = []
            
            for pdf_file in pdf_files:
                try:
                    content_data = await self.content_extractor.extract_for_analysis(str(pdf_file))
                    all_content.append({
                        "file": str(pdf_file),
                        "content": content_data["raw_content"],
                        "metadata": content_data["metadata"]
                    })
                    all_metadata.append(content_data["metadata"])
                    successful_files.append(str(pdf_file))
                except Exception as e:
                    logger.error(f"Failed to extract from {pdf_file}: {str(e)}")
                    failed_files.append({"file": str(pdf_file), "error": str(e)})
            
            # Step 3: Load template and create combined analysis instructions
            template_data = await self.template_loader.load_template("codelang")
            focused_template = self._filter_template_by_focus(template_data, focus)
            
            # Step 4: Create batch analysis instructions
            batch_instructions = self.analysis_instructions.create_batch_discourse_instructions(
                focus, depth, field, section_filter, len(successful_files)
            )
            
            # Step 5: Generate combined output filename
            combined_filename = self._generate_batch_codelang_filename(focus, len(successful_files), keyword)
            
            return {
                "success": True,
                "action_required": "analyze_combined_discourse_patterns",
                "batch_content": all_content,
                "combined_metadata": all_metadata,
                "template": focused_template,
                "analysis_instructions": batch_instructions,
                "focus": focus,
                "field": field,
                "section_filter": section_filter,
                "depth": depth,
                "output_info": {
                    "suggested_directory": output_dir,
                    "suggested_filename": combined_filename,
                    "full_suggested_path": str(Path(output_dir) / combined_filename)
                },
                "summary": {
                    "total_files": len(pdf_files),
                    "successful_extractions": len(successful_files),
                    "failed_extractions": len(failed_files),
                    "success_rate": len(successful_files) / len(pdf_files) if pdf_files else 0
                },
                "failed_files": failed_files,
                "message": f"Batch codelang analysis ready: {len(successful_files)} papers combined for {focus} analysis. Generate single comprehensive discourse analysis."
            }
            
        except Exception as e:
            logger.error(f"Batch discourse extraction failed: {str(e)}")
            return self._create_error_response(e, "batch_discourse_extraction", target)
    
    def _filter_template_by_focus(self, template_data: Dict[str, Any], focus: str) -> Dict[str, Any]:
        """Filter template sections based on focus option"""
        if focus == "discourse":
            return template_data  # Return full template
        
        # Get focus mapping
        focus_sections = self.CODELANG_FOCUS_MAPPING.get(focus, [])
        
        # Create filtered template metadata
        filtered_template = template_data.copy()
        filtered_template["focus_filter"] = focus
        filtered_template["included_sections"] = focus_sections
        filtered_template["analysis_scope"] = f"Focused analysis on {focus} patterns"
        
        return filtered_template
    
    def _generate_codelang_filename(self, metadata: Dict[str, Any], focus: str) -> str:
        """Generate filename for single codelang analysis: Codelang_[citekey].md"""
        citekey = metadata.get("citekey", "unknown")
        if not citekey or citekey == "unknown":
            # Generate citekey from available metadata
            first_author = metadata.get("first_author", "unknown")
            year = metadata.get("year", "unknown")
            title_words = metadata.get("title", "paper").split()[:2]
            title_part = "".join(word.lower() for word in title_words if word.isalnum())
            citekey = f"{first_author.lower()}{year}{title_part}" if first_author != "unknown" else f"paper{year}"
        
        # Clean citekey for filename
        safe_citekey = "".join(c for c in citekey if c.isalnum() or c in ('_', '-'))
        return f"Codelang_{safe_citekey}.md"
    
    def _generate_batch_codelang_filename(self, focus: str, file_count: int, keyword: str = None) -> str:
        """Generate filename for batch codelang analysis: Codelang_[keyword]_[focus].md"""
        if not keyword:
            # Generate keyword from timestamp or use generic term
            from datetime import datetime
            keyword = datetime.now().strftime("%Y%m%d")
        
        # Clean keyword for filename
        safe_keyword = "".join(c for c in keyword if c.isalnum() or c in ('_', '-'))
        return f"Codelang_{safe_keyword}_{focus}.md"
    
    async def create_citation_map(
        self,
        target: str,
        batch: bool = False,
        keyword: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create citation context maps and reference networks from research papers
        
        Args:
            target: Path to PDF file or directory
            batch: Whether to process multiple files with cross-reference analysis
            keyword: Keyword for batch filename (optional)
            output_dir: Output directory for generated citemap
        
        Returns:
            Dict with citation contexts, reference networks, and cross-paper analysis
        """
        try:
            logger.info(f"Starting citemap analysis: target={target}, batch={batch}")
            
            # Set default output directory
            if not output_dir:
                output_dir = self.config.default_output_dir + "/citemap-analysis"
            
            # Ensure output directory exists
            ensure_directory(output_dir)
            
            # Create processing options
            from .models import ProcessingOptions, FocusType, DepthType, FormatType
            options = ProcessingOptions(
                focus=FocusType.BALANCED,  # Default focus for citemap
                depth=DepthType.STANDARD,  # Default depth for citemap
                format=FormatType.MARKDOWN,  # Default format
                output_dir=output_dir
            )
            
            if batch:
                # Process directory with cross-reference analysis
                target_path = Path(target)
                if not target_path.exists():
                    raise FileNotFoundError(f"Directory not found: {target}")
                
                if not target_path.is_dir():
                    raise ValueError(f"Target must be a directory for batch processing: {target}")
                
                result = await self.citemap_processor.create_batch_citemap(target_path, options)
                
                if result["success"]:
                    batch_summary = result.get("batch_summary", {})
                    logger.info(f"Batch citemap completed: {batch_summary.get('processed_papers', 0)} papers analyzed")
                    
                    return {
                        "success": True,
                        "batch_summary": batch_summary,
                        "output_path": result["output_path"],
                        "individual_files": result.get("individual_files", []),
                        "message": (
                            f"Batch citation context mapping completed for {batch_summary.get('total_papers', 0)} papers. "
                            f"Generated comprehensive cross-reference analysis with {batch_summary.get('common_sources_found', 0)} common sources "
                            f"and {batch_summary.get('cross_references_identified', 0)} cross-references identified."
                        )
                    }
                else:
                    return result
            
            else:
                # Process single file
                target_path = Path(target)
                if not target_path.exists():
                    raise FileNotFoundError(f"PDF file not found: {target}")
                
                if not target_path.suffix.lower() == '.pdf':
                    raise ValueError(f"File is not a PDF: {target}")
                
                result = await self.citemap_processor.create_citemap(target_path, options)
                
                if result["success"]:
                    analysis_summary = result.get("analysis_summary", {})
                    logger.info(f"Single citemap completed: {analysis_summary.get('total_citations', 0)} citations analyzed")
                    
                    return {
                        "success": True,
                        "analysis_summary": analysis_summary,
                        "output_path": result["output_path"],
                        "metadata": result.get("metadata", {}),
                        "message": (
                            f"Citation context mapping completed for '{target_path.name}'. "
                            f"Extracted {analysis_summary.get('total_citations', 0)} citation contexts "
                            f"from {analysis_summary.get('unique_references', 0)} unique references. "
                            f"Generated network with {analysis_summary.get('network_nodes', 0)} nodes "
                            f"and {analysis_summary.get('network_edges', 0)} edges."
                        )
                    }
                else:
                    return result
            
        except Exception as e:
            logger.error(f"Error in citation mapping: {str(e)}")
            return self._create_error_response(e, "citation_mapping", target)
    
    async def initialize(self) -> None:
        """Initialize the MCP server"""
        try:
            # Ensure required directories exist
            ensure_directory(self.config.default_output_dir)
            ensure_directory(self.config.default_templates_dir)
            
            logger.info("MCP server initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing server: {str(e)}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the MCP server gracefully"""
        try:
            logger.info("Shutting down MCP server...")
            # Cleanup resources if needed
            logger.info("MCP server shutdown complete")
        
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
    
    def get_server(self) -> Server:
        """Get the MCP server instance"""
        return self.server


async def main():
    """Main entry point for the MCP server"""
    from mcp.server.stdio import stdio_server
    
    # Create server instance
    config = ServerConfig()
   _server = ScholarsQuillServer(config)
    
    # Initialize server
    await_server.initialize()
    
    logger.info("Starting ScholarsQuill MCP Server...")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await_server.get_server().run(
                read_stream,
                write_stream,
               _server.get_server().create_initialization_options()
            )
    finally:
        await_server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())