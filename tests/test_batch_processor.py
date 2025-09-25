"""
Unit tests for BatchProcessor
"""

import pytest
import tempfile
import shutil
import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from src.batch_processor import BatchProcessor, BatchResult, ProcessingProgress, ProgressTracker
from src.models import ProcessingOptions, FocusType, DepthType
from src.exceptions import FileError, ErrorCode


class TestBatchProcessor:
    """Test cases for BatchProcessor class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = BatchProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        
        # Create test PDF files
        self.pdf_files = []
        for i in range(3):
            pdf_file = self.test_dir / f"test_{i}.pdf"
            with open(pdf_file, 'wb') as f:
                f.write(b'%PDF-1.4\n%test content')
            self.pdf_files.append(pdf_file)
        
        # Create a non-PDF file
        self.txt_file = self.test_dir / "test.txt"
        self.txt_file.write_text("not a pdf")
        
        # Create a subdirectory with PDF
        self.subdir = self.test_dir / "subdir"
        self.subdir.mkdir()
        self.sub_pdf = self.subdir / "sub_test.pdf"
        with open(self.sub_pdf, 'wb') as f:
            f.write(b'%PDF-1.4\n%sub content')
    
    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_get_pdf_files_success(self):
        """Test successful PDF file discovery"""
        pdf_files = self.processor.get_pdf_files(str(self.test_dir))
        
        # Should find main PDFs and subdirectory PDF
        assert len(pdf_files) == 4  # 3 main + 1 sub
        
        # Check that all files are Path objects and exist
        for pdf_file in pdf_files:
            assert isinstance(pdf_file, Path)
            assert pdf_file.exists()
            assert pdf_file.suffix.lower() == '.pdf'
    
    def test_get_pdf_files_excludes_non_pdf(self):
        """Test that non-PDF files are excluded"""
        pdf_files = self.processor.get_pdf_files(str(self.test_dir))
        
        # Should not include the .txt file
        pdf_paths = [str(f) for f in pdf_files]
        assert str(self.txt_file) not in pdf_paths
    
    def test_get_pdf_files_empty_directory(self):
        """Test handling empty directory"""
        empty_dir = self.test_dir / "empty"
        empty_dir.mkdir()
        
        pdf_files = self.processor.get_pdf_files(str(empty_dir))
        assert len(pdf_files) == 0
    
    def test_get_pdf_files_nonexistent_directory(self):
        """Test error handling for nonexistent directory"""
        with pytest.raises(FileError) as exc_info:
            self.processor.get_pdf_files("/nonexistent/directory")
        
        assert exc_info.value.error_code == ErrorCode.FILE_NOT_FOUND
    
    def test_is_valid_pdf_file_valid(self):
        """Test validation of valid PDF file"""
        assert self.processor._is_valid_pdf_file(self.pdf_files[0]) is True
    
    def test_is_valid_pdf_file_invalid_extension(self):
        """Test validation rejects non-PDF extension"""
        assert self.processor._is_valid_pdf_file(self.txt_file) is False
    
    def test_is_valid_pdf_file_empty_file(self):
        """Test validation rejects empty file"""
        empty_pdf = self.test_dir / "empty.pdf"
        empty_pdf.touch()
        
        assert self.processor._is_valid_pdf_file(empty_pdf) is False
    
    def test_is_valid_pdf_file_invalid_header(self):
        """Test validation rejects file without PDF header"""
        fake_pdf = self.test_dir / "fake.pdf"
        fake_pdf.write_text("not a real pdf")
        
        assert self.processor._is_valid_pdf_file(fake_pdf) is False
    
    def test_is_valid_pdf_file_nonexistent(self):
        """Test validation rejects nonexistent file"""
        nonexistent = self.test_dir / "nonexistent.pdf"
        assert self.processor._is_valid_pdf_file(nonexistent) is False
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        test_cases = [
            ("normal_filename", "normal_filename"),
            ("file with spaces", "file with spaces"),
            ("file<>:\"/\\|?*", "file___________"),
            ("file__with__multiple__underscores", "file_with_multiple_underscores"),
            ("___leading_and_trailing___", "leading_and_trailing"),
            ("", "untitled"),
            ("!!!@#$%^&*()", "___________"),
        ]
        
        for input_name, expected in test_cases:
            result = self.processor._sanitize_filename(input_name)
            assert result == expected
    
    def test_generate_output_path_default_dir(self):
        """Test output path generation with default directory"""
        options = ProcessingOptions()
        output_path = self.processor._generate_output_path(self.pdf_files[0], options)
        
        expected_path = str(self.pdf_files[0].parent / "test_0.md")
        assert output_path == expected_path
    
    def test_generate_output_path_custom_dir(self):
        """Test output path generation with custom directory"""
        output_dir = str(self.test_dir / "output")
        options = ProcessingOptions(output_dir=output_dir)
        output_path = self.processor._generate_output_path(self.pdf_files[0], options)
        
        expected_path = str(Path(output_dir) / "test_0.md")
        assert output_path == expected_path
    
    def test_estimate_remaining_time(self):
        """Test remaining time estimation"""
        # Test with no completed files
        remaining = self.processor._estimate_remaining_time(0, 10, 0.0)
        assert remaining == 0.0
        
        # Test with some completed files
        remaining = self.processor._estimate_remaining_time(2, 10, 20.0)
        assert remaining == 80.0  # (20/2) * (10-2) = 10 * 8 = 80
    
    @pytest.mark.asyncio
    async def test_process_single_file_success(self):
        """Test successful processing of single file"""
        options = ProcessingOptions(focus=FocusType.RESEARCH)
        result = await self.processor._process_single_file(self.pdf_files[0], options)
        
        assert result["success"] is True
        assert result["file_path"] == str(self.pdf_files[0])
        assert "output_path" in result
        assert "metadata" in result
        assert "processing_options" in result
    
    @pytest.mark.asyncio
    async def test_process_directory_success(self):
        """Test successful directory processing"""
        options = ProcessingOptions()
        
        results = await self.processor.process_directory(str(self.test_dir), options)
        
        # Should process all PDF files
        assert len(results) == 4  # 3 main + 1 sub
        
        # All should be successful (mock implementation)
        successful_results = [r for r in results if r.get("success", False)]
        assert len(successful_results) == 4
    
    @pytest.mark.asyncio
    async def test_process_directory_nonexistent(self):
        """Test error handling for nonexistent directory"""
        options = ProcessingOptions()
        
        with pytest.raises(FileError) as exc_info:
            await self.processor.process_directory("/nonexistent", options)
        
        assert exc_info.value.error_code == ErrorCode.FILE_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_process_directory_file_instead_of_dir(self):
        """Test error handling when file provided instead of directory"""
        options = ProcessingOptions()
        
        with pytest.raises(FileError) as exc_info:
            await self.processor.process_directory(str(self.pdf_files[0]), options)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_PATH
    
    def test_progress_callback(self):
        """Test progress callback functionality"""
        progress_updates = []
        
        def progress_callback(progress: ProcessingProgress):
            progress_updates.append(progress)
        
        self.processor.set_progress_callback(progress_callback)
        
        # Progress callback should be set
        assert self.processor._progress_callback is not None
    
    def test_stop_processing(self):
        """Test stopping processing functionality"""
        assert self.processor._should_stop is False
        
        self.processor.stop_processing()
        assert self.processor._should_stop is True
    
    @pytest.mark.asyncio
    async def test_process_directory_empty_results(self):
        """Test processing directory with no PDF files"""
        empty_dir = self.test_dir / "empty"
        empty_dir.mkdir()
        
        options = ProcessingOptions()
        results = await self.processor.process_directory(str(empty_dir), options)
        
        assert len(results) == 0


class TestProgressTracker:
    """Test cases for ProgressTracker class"""
    
    def test_progress_tracker_initialization(self):
        """Test progress tracker initialization"""
        tracker = ProgressTracker(total_files=10)
        
        assert tracker.total_files == 10
        assert tracker.completed_files == 0
        assert tracker.start_time > 0
    
    def test_progress_tracker_update(self):
        """Test progress tracker update"""
        tracker = ProgressTracker(total_files=10)
        
        # Simulate some time passing
        time.sleep(0.1)
        
        progress = tracker.update(completed=3)
        
        assert progress.completed == 3
        assert progress.total == 10
        assert progress.percentage == 30.0
        assert progress.elapsed_time > 0
    
    def test_progress_tracker_zero_total(self):
        """Test progress tracker with zero total files"""
        tracker = ProgressTracker(total_files=0)
        progress = tracker.update(completed=0)
        
        assert progress.percentage == 0
    
    def test_progress_tracker_is_complete(self):
        """Test progress tracker completion check"""
        tracker = ProgressTracker(total_files=5)
        
        assert tracker.is_complete() is False
        
        tracker.update(completed=5)
        assert tracker.is_complete() is True
        
        tracker.update(completed=10)  # Over completion
        assert tracker.is_complete() is True


class TestBatchResult:
    """Test cases for BatchResult dataclass"""
    
    def test_batch_result_creation(self):
        """Test BatchResult creation"""
        result = BatchResult(
            total_files=10,
            processed_files=8,
            failed_files=2,
            successful_files=["file1.pdf", "file2.pdf"],
            failed_files_details=[{"file_path": "file3.pdf", "error": "error"}],
            processing_time=45.5,
            output_directory="/output"
        )
        
        assert result.total_files == 10
        assert result.processed_files == 8
        assert result.failed_files == 2
        assert len(result.successful_files) == 2
        assert len(result.failed_files_details) == 1
        assert result.processing_time == 45.5


class TestProcessingProgress:
    """Test cases for ProcessingProgress dataclass"""
    
    def test_processing_progress_creation(self):
        """Test ProcessingProgress creation"""
        progress = ProcessingProgress(
            current_file="test.pdf",
            completed=5,
            total=10,
            percentage=50.0,
            elapsed_time=30.0,
            estimated_remaining=30.0
        )
        
        assert progress.current_file == "test.pdf"
        assert progress.completed == 5
        assert progress.total == 10
        assert progress.percentage == 50.0
        assert progress.elapsed_time == 30.0
        assert progress.estimated_remaining == 30.0


if __name__ == "__main__":
    pytest.main([__file__])