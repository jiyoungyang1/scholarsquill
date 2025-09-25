"""
Batch processing for ScholarSquill MCP Server
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import logging

from .interfaces import BatchProcessorInterface
from .models import ProcessingOptions, PaperMetadata
from .exceptions import FileError, ProcessingError, ErrorCode, ErrorType


@dataclass
class BatchResult:
    """Result of batch processing operation"""
    total_files: int
    processed_files: int
    failed_files: int
    successful_files: List[str]
    failed_files_details: List[Dict[str, Any]]
    processing_time: float
    output_directory: str


@dataclass
class ProcessingProgress:
    """Progress information for batch processing"""
    current_file: str
    completed: int
    total: int
    percentage: float
    elapsed_time: float
    estimated_remaining: float


class BatchProcessor(BatchProcessorInterface):
    """Batch processor for handling multiple PDF files"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize batch processor
        
        Args:
            logger: Optional logger for progress tracking
        """
        self.logger = logger or logging.getLogger(__name__)
        self._progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
        self._should_stop = False
    
    def set_progress_callback(self, callback: Callable[[ProcessingProgress], None]) -> None:
        """Set callback function for progress updates"""
        self._progress_callback = callback
    
    def stop_processing(self) -> None:
        """Signal to stop batch processing"""
        self._should_stop = True
    
    async def process_directory(self, directory_path: str, options: ProcessingOptions) -> List[Dict]:
        """
        Process directory - batch mode only (minireview is handled separately)
        
        Args:
            directory_path: Path to directory containing PDF files
            options: Processing options to apply
            
        Returns:
            List[Dict]: Results for each processed file
        """
        return await self.process_directory_batch(directory_path, options)
    
    async def process_directory_batch(self, directory_path: str, options: ProcessingOptions) -> List[Dict]:
        """
        Process all PDFs in directory
        
        Args:
            directory_path: Path to directory containing PDF files
            options: Processing options to apply to all files
            
        Returns:
            List[Dict]: Results for each processed file
            
        Raises:
            FileError: If directory doesn't exist or is not accessible
            ProcessingError: If batch processing fails
        """
        start_time = time.time()
        directory = Path(directory_path)
        
        # Validate directory
        if not directory.exists():
            raise FileError(
                f"Directory not found: {directory_path}",
                ErrorCode.FILE_NOT_FOUND,
                file_path=directory_path,
                suggestions=[
                    "Check if the directory path is correct",
                    "Ensure the directory exists and is accessible",
                    "Use absolute path if needed"
                ]
            )
        
        if not directory.is_dir():
            raise FileError(
                f"Path is not a directory: {directory_path}",
                ErrorCode.INVALID_PATH,
                file_path=directory_path,
                suggestions=[
                    "Provide a directory path for batch processing",
                    "Remove --batch flag to process single file"
                ]
            )
        
        # Get all PDF files
        pdf_files = self.get_pdf_files(directory_path)
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in directory: {directory_path}")
            return []
        
        self.logger.info(f"Found {len(pdf_files)} PDF files for batch processing")
        
        # Initialize results tracking
        results = []
        successful_files = []
        failed_files_details = []
        
        # Process each file
        for i, pdf_file in enumerate(pdf_files):
            if self._should_stop:
                self.logger.info("Batch processing stopped by user request")
                break
            
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # Update progress
            progress = ProcessingProgress(
                current_file=pdf_file.name,
                completed=i,
                total=len(pdf_files),
                percentage=(i / len(pdf_files)) * 100,
                elapsed_time=elapsed_time,
                estimated_remaining=self._estimate_remaining_time(i, len(pdf_files), elapsed_time)
            )
            
            if self._progress_callback:
                self._progress_callback(progress)
            
            self.logger.info(f"Processing file {i+1}/{len(pdf_files)}: {pdf_file.name}")
            
            try:
                # Process single file
                result = await self._process_single_file(pdf_file, options)
                results.append(result)
                successful_files.append(str(pdf_file))
                
                self.logger.info(f"Successfully processed: {pdf_file.name}")
                
            except Exception as e:
                # Log error but continue with other files
                error_details = {
                    "file_path": str(pdf_file),
                    "error_message": str(e),
                    "error_type": type(e).__name__
                }
                failed_files_details.append(error_details)
                
                self.logger.error(f"Failed to process {pdf_file.name}: {e}")
                
                # Add error result
                results.append({
                    "success": False,
                    "file_path": str(pdf_file),
                    "error": str(e),
                    "error_type": type(e).__name__
                })
        
        # Final progress update
        total_time = time.time() - start_time
        final_progress = ProcessingProgress(
            current_file="",
            completed=len(pdf_files),
            total=len(pdf_files),
            percentage=100.0,
            elapsed_time=total_time,
            estimated_remaining=0.0
        )
        
        if self._progress_callback:
            self._progress_callback(final_progress)
        
        # Create batch result summary
        batch_result = BatchResult(
            total_files=len(pdf_files),
            processed_files=len([r for r in results if r.get("success", False)]),
            failed_files=len(failed_files_details),
            successful_files=successful_files,
            failed_files_details=failed_files_details,
            processing_time=total_time,
            output_directory=options.output_dir or str(directory)
        )
        
        # Log summary
        self._log_batch_summary(batch_result)
        
        return results
    
    def get_pdf_files(self, directory_path: str) -> List[Path]:
        """
        Get list of PDF files in directory
        
        Args:
            directory_path: Path to directory
            
        Returns:
            List[Path]: List of PDF file paths
            
        Raises:
            FileError: If directory is not accessible
        """
        directory = Path(directory_path)
        
        try:
            # Find all PDF files recursively
            pdf_files = []
            
            # Search in main directory
            for pattern in ['*.pdf', '*.PDF']:
                pdf_files.extend(directory.glob(pattern))
            
            # Also search one level deep in subdirectories
            for pattern in ['*/*.pdf', '*/*.PDF']:
                pdf_files.extend(directory.glob(pattern))
            
            # Remove duplicates and sort
            pdf_files = sorted(list(set(pdf_files)))
            
            # Filter and validate files
            valid_files = []
            for pdf_file in pdf_files:
                if self._is_valid_pdf_file(pdf_file):
                    valid_files.append(pdf_file)
                else:
                    self.logger.warning(f"Skipping invalid PDF file: {pdf_file}")
            
            return valid_files
            
        except PermissionError:
            raise FileError(
                f"Permission denied accessing directory: {directory_path}",
                ErrorCode.FILE_UNREADABLE,
                file_path=directory_path,
                suggestions=[
                    "Check directory permissions",
                    "Run with appropriate user privileges",
                    "Ensure directory is not locked by another process"
                ]
            )
        except Exception as e:
            raise FileError(
                f"Error scanning directory {directory_path}: {e}",
                ErrorCode.FILE_ERROR,
                file_path=directory_path,
                suggestions=[
                    "Ensure directory is accessible",
                    "Check for filesystem errors",
                    "Try with a different directory"
                ]
            )
    
    def _is_valid_pdf_file(self, file_path: Path) -> bool:
        """
        Check if file is a valid PDF file
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if valid PDF file
        """
        try:
            # Basic checks
            if not file_path.exists():
                return False
            
            if not file_path.is_file():
                return False
            
            if file_path.suffix.lower() != '.pdf':
                return False
            
            # Check file size (avoid empty files)
            if file_path.stat().st_size == 0:
                return False
            
            # Check if file is readable
            with open(file_path, 'rb') as f:
                # Read first few bytes to check PDF header
                header = f.read(4)
                if header != b'%PDF':
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def _process_single_file(self, file_path: Path, options: ProcessingOptions) -> Dict[str, Any]:
        """
        Process a single PDF file
        
        Args:
            file_path: Path to PDF file
            options: Processing options
            
        Returns:
            Dict: Processing result
        """
        # This is a placeholder - in the actual implementation, this would
        # call the PDF processor, content analyzer, and note generator
        # For now, we return a mock result structure
        
        try:
            # Simulate processing time based on depth
            if options.depth.value == "quick":
                await asyncio.sleep(0.1)  # Quick processing
            elif options.depth.value == "deep":
                await asyncio.sleep(0.5)  # Deep processing
            else:
                await asyncio.sleep(0.3)  # Standard processing
            
            # Mock successful result
            return {
                "success": True,
                "file_path": str(file_path),
                "output_path": self._generate_output_path(file_path, options),
                "metadata": {
                    "title": f"Sample Paper: {file_path.stem}",
                    "authors": ["Author Name"],
                    "year": 2024
                },
                "processing_options": {
                    "focus": options.focus.value,
                    "depth": options.depth.value,
                    "format": options.format.value
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "file_path": str(file_path),
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _generate_output_path(self, input_path: Path, options: ProcessingOptions) -> str:
        """Generate output path for processed file"""
        output_dir = Path(options.output_dir) if options.output_dir else input_path.parent
        
        # Generate safe filename
        safe_name = self._sanitize_filename(input_path.stem)
        output_filename = f"{safe_name}.md"
        
        return str(output_dir / output_filename)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        safe_filename = filename
        
        for char in unsafe_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # Remove multiple consecutive underscores
        while '__' in safe_filename:
            safe_filename = safe_filename.replace('__', '_')
        
        # Remove leading/trailing underscores
        safe_filename = safe_filename.strip('_')
        
        # Ensure filename is not empty
        if not safe_filename:
            safe_filename = "untitled"
        
        return safe_filename
    
    def _estimate_remaining_time(self, completed: int, total: int, elapsed_time: float) -> float:
        """Estimate remaining processing time"""
        if completed == 0:
            return 0.0
        
        avg_time_per_file = elapsed_time / completed
        remaining_files = total - completed
        return avg_time_per_file * remaining_files
    
    def _log_batch_summary(self, result: BatchResult) -> None:
        """Log batch processing summary"""
        self.logger.info("=" * 50)
        self.logger.info("BATCH PROCESSING SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total files found: {result.total_files}")
        self.logger.info(f"Successfully processed: {result.processed_files}")
        self.logger.info(f"Failed to process: {result.failed_files}")
        self.logger.info(f"Processing time: {result.processing_time:.2f} seconds")
        self.logger.info(f"Output directory: {result.output_directory}")
        
        if result.failed_files > 0:
            self.logger.info("\nFailed files:")
            for failed in result.failed_files_details:
                self.logger.info(f"  - {failed['file_path']}: {failed['error_message']}")
        
        self.logger.info("=" * 50)


class ProgressTracker:
    """Helper class for tracking batch processing progress"""
    
    def __init__(self, total_files: int):
        """Initialize progress tracker"""
        self.total_files = total_files
        self.completed_files = 0
        self.start_time = time.time()
    
    def update(self, completed: int) -> ProcessingProgress:
        """Update progress and return current status"""
        self.completed_files = completed
        elapsed_time = time.time() - self.start_time
        
        percentage = (completed / self.total_files) * 100 if self.total_files > 0 else 0
        
        # Estimate remaining time
        if completed > 0:
            avg_time = elapsed_time / completed
            remaining_files = self.total_files - completed
            estimated_remaining = avg_time * remaining_files
        else:
            estimated_remaining = 0
        
        return ProcessingProgress(
            current_file="",
            completed=completed,
            total=self.total_files,
            percentage=percentage,
            elapsed_time=elapsed_time,
            estimated_remaining=estimated_remaining
        )
    
    def is_complete(self) -> bool:
        """Check if processing is complete"""
        return self.completed_files >= self.total_files


def create_batch_processing_error(message: str, details: Optional[Dict[str, Any]] = None) -> ProcessingError:
    """Create a standardized batch processing error"""
    return ProcessingError(
        message=message,
        error_code=ErrorCode.PROCESSING_FAILED,
        suggestions=[
            "Check individual file processing logs",
            "Ensure all files are valid PDFs",
            "Try processing files individually to isolate issues"
        ],
        details=details
    )