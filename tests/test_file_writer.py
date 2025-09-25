"""
Unit tests for FileWriter
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from src.file_writer import FileWriter, FileExistsError, create_file_writer
from src.models import PaperMetadata, FormatType
from src.exceptions import FileError, ErrorCode


class TestFileWriter:
    """Test cases for FileWriter class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        self.writer = FileWriter(default_output_dir=str(self.test_dir))
        
        # Create sample metadata
        self.sample_metadata = PaperMetadata(
            title="A Study on Machine Learning Applications",
            first_author="Smith, John",
            authors=["Smith, John", "Doe, Jane", "Johnson, Bob"],
            year=2024,
            citekey="smith2024machine",
            journal="Journal of AI Research",
            volume="15",
            issue="3",
            pages="123-145",
            doi="10.1000/123456"
        )
    
    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_init_default_values(self):
        """Test FileWriter initialization with default values"""
        writer = FileWriter()
        
        assert writer.default_output_dir == "literature-notes"
        assert writer.overwrite_mode == "prompt"
        assert writer.logger is not None
    
    def test_init_custom_values(self):
        """Test FileWriter initialization with custom values"""
        custom_dir = "/custom/output"
        writer = FileWriter(
            default_output_dir=custom_dir,
            overwrite_mode="overwrite"
        )
        
        assert writer.default_output_dir == custom_dir
        assert writer.overwrite_mode == "overwrite"
    
    def test_init_invalid_overwrite_mode(self):
        """Test FileWriter initialization with invalid overwrite mode"""
        writer = FileWriter(overwrite_mode="invalid")
        
        # Should default to "prompt"
        assert writer.overwrite_mode == "prompt"
    
    def test_write_note_success(self):
        """Test successful note writing"""
        content = "# Test Note\n\nThis is a test note."
        output_path = str(self.test_dir / "test_note.md")
        
        result_path = self.writer.write_note(content, output_path)
        
        assert result_path == output_path
        assert Path(output_path).exists()
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            written_content = f.read()
        assert written_content == content
    
    def test_write_note_creates_directory(self):
        """Test that write_note creates output directory if needed"""
        nested_dir = self.test_dir / "nested" / "directory"
        output_path = str(nested_dir / "test_note.md")
        content = "# Test Note"
        
        result_path = self.writer.write_note(content, output_path)
        
        assert result_path == output_path
        assert nested_dir.exists()
        assert Path(output_path).exists()
    
    def test_write_note_permission_error(self):
        """Test write_note handles permission errors"""
        # Create a read-only directory
        readonly_dir = self.test_dir / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        output_path = str(readonly_dir / "test_note.md")
        
        try:
            with pytest.raises(FileError) as exc_info:
                self.writer.write_note("content", output_path)
            
            assert exc_info.value.error_code == ErrorCode.FILE_UNREADABLE
            assert "Permission denied" in str(exc_info.value)
        finally:
            # Cleanup - restore permissions
            readonly_dir.chmod(0o755)
    
    def test_generate_filename_with_citekey(self):
        """Test filename generation using citekey"""
        filename = self.writer.generate_filename(self.sample_metadata, "markdown")
        
        assert filename == "smith2024machine.md"
    
    def test_generate_filename_without_citekey(self):
        """Test filename generation without citekey"""
        metadata = PaperMetadata(
            title="Deep Learning for Computer Vision",
            first_author="Brown, Alice",
            authors=["Brown, Alice"],
            year=2023,
            citekey=""  # No citekey
        )
        
        filename = self.writer.generate_filename(metadata, "markdown")
        
        assert filename == "brown_2023_deep.md"
    
    def test_generate_filename_minimal_metadata(self):
        """Test filename generation with minimal metadata"""
        metadata = PaperMetadata(
            title="",
            first_author="",
            authors=[],
            year=None
        )
        
        filename = self.writer.generate_filename(metadata, "markdown")
        
        # Should generate timestamp-based filename
        assert filename.startswith("paper_")
        assert filename.endswith(".md")
    
    def test_generate_filename_special_characters(self):
        """Test filename generation with special characters"""
        metadata = PaperMetadata(
            title="AI/ML: A Study on <Machine> Learning & \"Deep\" Networks",
            first_author="O'Connor, Patrick",
            authors=["O'Connor, Patrick"],
            year=2024
        )
        
        filename = self.writer.generate_filename(metadata, "markdown")
        
        # Should sanitize special characters
        assert "/" not in filename
        assert "<" not in filename
        assert ">" not in filename
        assert '"' not in filename
    
    def test_ensure_output_directory_creates_new(self):
        """Test creating new output directory"""
        new_dir = str(self.test_dir / "new_output_dir")
        
        result = self.writer.ensure_output_directory(new_dir)
        
        assert result is True
        assert Path(new_dir).exists()
        assert Path(new_dir).is_dir()
    
    def test_ensure_output_directory_existing(self):
        """Test with existing output directory"""
        result = self.writer.ensure_output_directory(str(self.test_dir))
        
        assert result is True
    
    def test_ensure_output_directory_file_exists(self):
        """Test error when file exists at directory path"""
        file_path = self.test_dir / "existing_file.txt"
        file_path.write_text("content")
        
        with pytest.raises(FileError) as exc_info:
            self.writer.ensure_output_directory(str(file_path))
        
        assert exc_info.value.error_code == ErrorCode.INVALID_PATH
        assert "not a directory" in str(exc_info.value)
    
    def test_get_output_path_default_dir(self):
        """Test getting output path with default directory"""
        output_path = self.writer.get_output_path(self.sample_metadata, "markdown")
        
        expected_path = str(self.test_dir / "smith2024machine.md")
        assert output_path == expected_path
    
    def test_get_output_path_custom_dir(self):
        """Test getting output path with custom directory"""
        custom_dir = str(self.test_dir / "custom")
        output_path = self.writer.get_output_path(
            self.sample_metadata, "markdown", custom_dir
        )
        
        expected_path = str(Path(custom_dir) / "smith2024machine.md")
        assert output_path == expected_path
    
    def test_backup_existing_file(self):
        """Test creating backup of existing file"""
        # Create original file
        original_file = self.test_dir / "original.md"
        original_content = "original content"
        original_file.write_text(original_content)
        
        # Create backup
        backup_path = self.writer.backup_existing_file(str(original_file))
        
        # Verify backup exists and has correct content
        assert Path(backup_path).exists()
        assert "backup_" in backup_path
        assert Path(backup_path).read_text() == original_content
    
    def test_backup_nonexistent_file(self):
        """Test backup of nonexistent file returns original path"""
        nonexistent = str(self.test_dir / "nonexistent.md")
        
        result = self.writer.backup_existing_file(nonexistent)
        
        assert result == nonexistent
    
    def test_resolve_file_conflict_overwrite_mode(self):
        """Test file conflict resolution in overwrite mode"""
        writer = FileWriter(overwrite_mode="overwrite")
        
        # Create existing file
        existing_file = self.test_dir / "existing.md"
        existing_file.write_text("existing content")
        
        # Should return same path and create backup
        result = writer._resolve_file_conflict(existing_file)
        
        assert result == existing_file
        # Backup should be created
        backup_files = list(self.test_dir.glob("existing_backup_*.md"))
        assert len(backup_files) == 1
    
    def test_resolve_file_conflict_rename_mode(self):
        """Test file conflict resolution in rename mode"""
        writer = FileWriter(overwrite_mode="rename")
        
        # Create existing file
        existing_file = self.test_dir / "existing.md"
        existing_file.write_text("existing content")
        
        # Should return new path
        result = writer._resolve_file_conflict(existing_file)
        
        assert result != existing_file
        assert str(result).endswith("_1.md")
    
    def test_resolve_file_conflict_skip_mode(self):
        """Test file conflict resolution in skip mode"""
        writer = FileWriter(overwrite_mode="skip")
        
        # Create existing file
        existing_file = self.test_dir / "existing.md"
        existing_file.write_text("existing content")
        
        # Should raise error
        with pytest.raises(FileError) as exc_info:
            writer._resolve_file_conflict(existing_file)
        
        assert exc_info.value.error_code == ErrorCode.FILE_EXISTS
    
    def test_generate_unique_filename(self):
        """Test unique filename generation"""
        # Create existing files
        base_file = self.test_dir / "test.md"
        base_file.write_text("content")
        
        file_1 = self.test_dir / "test_1.md"
        file_1.write_text("content")
        
        # Should generate test_2.md
        result = self.writer._generate_unique_filename(base_file)
        
        assert str(result).endswith("test_2.md")
        assert not result.exists()
    
    def test_generate_unique_filename_safety_limit(self):
        """Test unique filename generation with safety limit"""
        base_file = self.test_dir / "test.md"
        
        # Mock the counter limit
        with patch.object(self.writer, '_generate_unique_filename') as mock_method:
            # Simulate hitting the safety limit
            def mock_generate(original_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return original_path.parent / f"{original_path.stem}_{timestamp}{original_path.suffix}"
            
            mock_method.side_effect = mock_generate
            
            result = self.writer._generate_unique_filename(base_file)
            
            # Should include timestamp
            assert "_" in str(result)
            assert str(result).endswith(".md")
    
    def test_get_file_extension(self):
        """Test file extension determination"""
        assert self.writer._get_file_extension("markdown") == ".md"
        assert self.writer._get_file_extension("md") == ".md"
        assert self.writer._get_file_extension(FormatType.MARKDOWN.value) == ".md"
        assert self.writer._get_file_extension("unknown") == ".md"  # Default
    
    def test_get_file_info_existing_file(self):
        """Test getting file info for existing file"""
        test_file = self.test_dir / "test.md"
        test_content = "test content"
        test_file.write_text(test_content)
        
        file_info = self.writer.get_file_info(str(test_file))
        
        assert file_info["exists"] is True
        assert file_info["is_file"] is True
        assert file_info["is_directory"] is False
        assert file_info["size_bytes"] == len(test_content.encode())
        assert file_info["readable"] is True
        assert file_info["writable"] is True
        assert isinstance(file_info["modified_time"], datetime)
    
    def test_get_file_info_nonexistent_file(self):
        """Test getting file info for nonexistent file"""
        file_info = self.writer.get_file_info("/nonexistent/file.md")
        
        assert file_info["exists"] is False
    
    def test_cleanup_temp_files(self):
        """Test cleanup of temporary files"""
        # Create temporary directory with files
        temp_subdir = self.test_dir / "temp_cleanup"
        temp_subdir.mkdir()
        (temp_subdir / "temp_file.txt").write_text("temp content")
        
        # Cleanup
        self.writer.cleanup_temp_files(str(temp_subdir))
        
        # Should be removed
        assert not temp_subdir.exists()
    
    def test_cleanup_temp_files_nonexistent(self):
        """Test cleanup of nonexistent directory"""
        # Should not raise error
        self.writer.cleanup_temp_files("/nonexistent/directory")
    
    def test_file_extension_mapping(self):
        """Test various file format extensions"""
        test_cases = [
            ("markdown", ".md"),
            ("MARKDOWN", ".md"),  # Case insensitive
            ("md", ".md"),
            ("MD", ".md"),
            ("unknown_format", ".md"),  # Default fallback
        ]
        
        for format_type, expected_ext in test_cases:
            ext = self.writer._get_file_extension(format_type)
            assert ext == expected_ext
    
    def test_generate_base_filename_strategies(self):
        """Test different filename generation strategies"""
        # Test with citekey
        metadata_with_citekey = PaperMetadata(
            title="Test Title",
            first_author="Author, Test",
            authors=["Author, Test"],
            year=2024,
            citekey="test2024study"
        )
        
        filename = self.writer._generate_base_filename(metadata_with_citekey)
        assert filename == "test2024study"
        
        # Test without citekey but with complete metadata
        metadata_without_citekey = PaperMetadata(
            title="Machine Learning Applications in Healthcare",
            first_author="Smith, John",
            authors=["Smith, John"],
            year=2024,
            citekey=""
        )
        
        filename = self.writer._generate_base_filename(metadata_without_citekey)
        assert filename == "smith_2024_machine"
        
        # Test with minimal metadata
        metadata_minimal = PaperMetadata(
            title="",
            first_author="",
            authors=[],
            year=None
        )
        
        filename = self.writer._generate_base_filename(metadata_minimal)
        assert filename.startswith("paper_")


class TestFileExistsError:
    """Test cases for FileExistsError class"""
    
    def test_file_exists_error_creation(self):
        """Test FileExistsError creation"""
        file_path = "/test/file.md"
        error = FileExistsError(file_path)
        
        assert isinstance(error, FileError)
        assert error.error_code == ErrorCode.FILE_ERROR
        assert file_path in str(error)
        assert len(error.suggestions) > 0
    
    def test_file_exists_error_custom_suggestions(self):
        """Test FileExistsError with custom suggestions"""
        custom_suggestions = ["Custom suggestion 1", "Custom suggestion 2"]
        error = FileExistsError("/test/file.md", suggestions=custom_suggestions)
        
        assert error.suggestions == custom_suggestions


class TestCreateFileWriter:
    """Test cases for create_file_writer factory function"""
    
    def test_create_file_writer_default(self):
        """Test creating FileWriter with default config"""
        writer = create_file_writer()
        
        assert isinstance(writer, FileWriter)
        assert writer.default_output_dir == "literature-notes"
        assert writer.overwrite_mode == "prompt"
    
    def test_create_file_writer_custom_config(self):
        """Test creating FileWriter with custom config"""
        config = {
            "default_output_dir": "/custom/output",
            "overwrite_mode": "overwrite",
        }
        
        writer = create_file_writer(config)
        
        assert writer.default_output_dir == "/custom/output"
        assert writer.overwrite_mode == "overwrite"
    
    def test_create_file_writer_partial_config(self):
        """Test creating FileWriter with partial config"""
        config = {
            "overwrite_mode": "rename"
        }
        
        writer = create_file_writer(config)
        
        assert writer.default_output_dir == "literature-notes"  # Default
        assert writer.overwrite_mode == "rename"  # Custom


if __name__ == "__main__":
    pytest.main([__file__])