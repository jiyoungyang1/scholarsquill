#!/usr/bin/env python3
"""
Core ScholarsQuill Server functionality without MCP dependencies
Used for testing and standalone operation
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Local imports
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
from .config import ServerConfig
from .exceptions import (
    PDFProcessingError, ContentAnalysisError, NoteGenerationError,
    CommandParsingError, BatchProcessingError
)
from .utils import setup_logging, ensure_directory

# Configure logging
logger = logging.getLogger("scholarsquill-core")


class ScholarsQuillCore:
    """Core functionality for ScholarsQuill without MCP dependencies"""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        """Initialize the core server with configuration"""
        self.config = config or ServerConfig()
        
        # Initialize core components
        self.pdf_processor: PDFProcessorInterface = PDFProcessor()
        self.content_analyzer: ContentAnalyzerInterface = ContentAnalyzer()
        self.note_generator: NoteGeneratorInterface = NoteGenerator()
        self.command_parser: CommandParserInterface = CommandParser()
        self.batch_processor: BatchProcessorInterface = BatchProcessor()
        self.minireview_processor = MiniReviewProcessor()
        self.citemap_processor = CitemapProcessor()
        
        # Setup logging
        setup_logging(self.config.log_level)
        
        logger.info("ScholarsQuill Core initialized")
    
    async def initialize(self) -> None:
        """Initialize the core server"""
        try:
            # Ensure required directories exist
            ensure_directory(self.config.default_output_dir)
            ensure_directory(self.config.default_templates_dir)
            
            logger.info("Core server initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing server: {str(e)}")
            raise
    
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
        Main method to process note generation commands
        
        Args:
            target: Path to PDF file or directory
            focus: Analysis focus type
            depth: Analysis depth level
            format: Output format
            batch: Whether to process in batch mode
            output_dir: Output directory for notes
        
        Returns:
            Dict with processing results
        """
        try:
            # Parse and validate command arguments
            command_str = f"/sq:note {target}"
            if focus != "balanced":
                command_str += f" --focus {focus}"
            if depth != "standard":
                command_str += f" --depth {depth}"
            if format != "markdown":
                command_str += f" --format {format}"
            if batch:
                command_str += " --batch yes"
            if output_dir:
                command_str += f" --output {output_dir}"
            
            args = self.command_parser.parse_command(command_str)
            
            if not self.command_parser.validate_arguments(args):
                raise CommandParsingError("Invalid command arguments")
            
            # Set default output directory if not specified
            if not args.output_dir:
                args.output_dir = self.config.default_output_dir
            
            # Ensure output directory exists
            ensure_directory(args.output_dir)
            
            # Process based on batch mode
            if args.batch:
                return await self._process_batch(args)
            else:
                return await self._process_single_file(args)
        
        except Exception as e:
            logger.error(f"Error processing note command: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
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
    
    async def shutdown(self) -> None:
        """Shutdown the core server gracefully"""
        try:
            logger.info("Shutting down core server...")
            # Cleanup resources if needed
            logger.info("Core server shutdown complete")
        
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")