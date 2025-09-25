"""
Unit tests for CommandParser
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.command_parser import CommandParser, create_command_validation_error
from src.models import CommandArgs, FocusType, DepthType, FormatType
from src.exceptions import ValidationError, ErrorCode


class TestCommandParser:
    """Test cases for CommandParser class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = CommandParser()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_pdf = Path(self.temp_dir) / "test.pdf"
        
        # Create a fake PDF file for testing
        with open(self.temp_pdf, 'wb') as f:
            f.write(b'%PDF-1.4\n%test content')
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if self.temp_pdf.exists():
            self.temp_pdf.unlink()
        os.rmdir(self.temp_dir)
    
    def test_parse_simple_command(self):
        """Test parsing simple command with just target"""
        command = f"/sq:note {self.temp_pdf}"
        args = self.parser.parse_command(command)
        
        assert args.target == str(self.temp_pdf)
        assert args.focus == FocusType.BALANCED
        assert args.depth == DepthType.STANDARD
        assert args.format == FormatType.MARKDOWN
        assert args.batch is False
        assert args.output_dir is None
    
    def test_parse_command_without_prefix(self):
        """Test parsing command without /sq:note prefix"""
        command = f"{self.temp_pdf} --focus research"
        args = self.parser.parse_command(command)
        
        assert args.target == str(self.temp_pdf)
        assert args.focus == FocusType.RESEARCH
    
    def test_parse_command_with_all_options(self):
        """Test parsing command with all options"""
        output_dir = str(Path(self.temp_dir) / "output")
        command = f"/sq:note {self.temp_pdf} --focus theory --depth deep --format markdown --batch --output-dir {output_dir}"
        args = self.parser.parse_command(command)
        
        assert args.target == str(self.temp_pdf)
        assert args.focus == FocusType.THEORY
        assert args.depth == DepthType.DEEP
        assert args.format == FormatType.MARKDOWN
        assert args.batch is True
        assert args.output_dir == output_dir
    
    def test_parse_command_with_short_options(self):
        """Test parsing command with short options"""
        command = f"/sq:note {self.temp_pdf} -b"
        args = self.parser.parse_command(command)
        
        assert args.batch is True
    
    def test_parse_command_with_aliases(self):
        """Test parsing command with focus and depth aliases"""
        command = f"/sq:note {self.temp_pdf} --focus r --depth q"
        args = self.parser.parse_command(command)
        
        assert args.focus == FocusType.RESEARCH
        assert args.depth == DepthType.QUICK
    
    def test_parse_command_with_quoted_paths(self):
        """Test parsing command with quoted file paths"""
        quoted_path = f'"{self.temp_pdf}"'
        command = f"/sq:note {quoted_path}"
        args = self.parser.parse_command(command)
        
        assert args.target == str(self.temp_pdf)
    
    def test_parse_empty_command(self):
        """Test parsing empty command raises error"""
        with pytest.raises(ValidationError) as exc_info:
            self.parser.parse_command("/sq:note")
        
        assert exc_info.value.error_code == ErrorCode.INVALID_ARGUMENTS
        assert "Target file or directory is required" in str(exc_info.value)
    
    def test_parse_command_missing_focus_value(self):
        """Test parsing command with missing focus value"""
        command = f"/sq:note {self.temp_pdf} --focus"
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.parse_command(command)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_ARGUMENTS
        assert "--focus requires a value" in str(exc_info.value)
    
    def test_parse_command_invalid_focus(self):
        """Test parsing command with invalid focus type"""
        command = f"/sq:note {self.temp_pdf} --focus invalid"
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.parse_command(command)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_FOCUS
    
    def test_parse_command_invalid_depth(self):
        """Test parsing command with invalid depth level"""
        command = f"/sq:note {self.temp_pdf} --depth invalid"
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.parse_command(command)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_DEPTH
    
    def test_parse_command_invalid_format(self):
        """Test parsing command with invalid format type"""
        command = f"/sq:note {self.temp_pdf} --format invalid"
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.parse_command(command)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_FORMAT
    
    def test_parse_command_unknown_option(self):
        """Test parsing command with unknown option"""
        command = f"/sq:note {self.temp_pdf} --unknown option"
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.parse_command(command)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_ARGUMENTS
        assert "Unknown option: --unknown" in str(exc_info.value)
    
    def test_parse_command_invalid_syntax(self):
        """Test parsing command with invalid shell syntax"""
        command = f"/sq:note {self.temp_pdf} --focus 'unclosed quote"
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.parse_command(command)
        
        assert "Invalid command syntax" in str(exc_info.value)
    
    def test_validate_single_file_success(self):
        """Test successful validation of single file arguments"""
        args = CommandArgs(target=str(self.temp_pdf))
        
        result = self.parser.validate_arguments(args)
        assert result is True
    
    def test_validate_batch_directory_success(self):
        """Test successful validation of batch directory arguments"""
        args = CommandArgs(target=self.temp_dir, batch=True)
        
        result = self.parser.validate_arguments(args)
        assert result is True
    
    def test_validate_file_not_found(self):
        """Test validation error when file not found"""
        args = CommandArgs(target="/nonexistent/file.pdf")
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.validate_arguments(args)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_PATH
        assert "File not found" in str(exc_info.value)
    
    def test_validate_directory_not_found(self):
        """Test validation error when directory not found for batch"""
        args = CommandArgs(target="/nonexistent/directory", batch=True)
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.validate_arguments(args)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_PATH
        assert "Directory not found" in str(exc_info.value)
    
    def test_validate_file_not_pdf(self):
        """Test validation error when file is not a PDF"""
        txt_file = Path(self.temp_dir) / "test.txt"
        txt_file.write_text("test content")
        
        args = CommandArgs(target=str(txt_file))
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.validate_arguments(args)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_PATH
        assert "Target must be a PDF file" in str(exc_info.value)
        
        txt_file.unlink()
    
    def test_validate_batch_with_file(self):
        """Test validation error when batch flag used with file"""
        args = CommandArgs(target=str(self.temp_pdf), batch=True)
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.validate_arguments(args)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_PATH
        assert "Batch processing requires a directory" in str(exc_info.value)
    
    def test_validate_invalid_output_dir(self):
        """Test validation error when output dir is not a directory"""
        args = CommandArgs(target=str(self.temp_pdf), output_dir=str(self.temp_pdf))
        
        with pytest.raises(ValidationError) as exc_info:
            self.parser.validate_arguments(args)
        
        assert exc_info.value.error_code == ErrorCode.INVALID_PATH
        assert "Output path must be a directory" in str(exc_info.value)
    
    def test_focus_aliases(self):
        """Test all focus type aliases"""
        focus_tests = [
            ('r', FocusType.RESEARCH),
            ('research', FocusType.RESEARCH),
            ('t', FocusType.THEORY),
            ('theory', FocusType.THEORY),
            ('rev', FocusType.REVIEW),
            ('review', FocusType.REVIEW),
            ('m', FocusType.METHOD),
            ('method', FocusType.METHOD),
            ('methodology', FocusType.METHOD),
            ('b', FocusType.BALANCED),
            ('balanced', FocusType.BALANCED),
        ]
        
        for alias, expected_type in focus_tests:
            command = f"/sq:note {self.temp_pdf} --focus {alias}"
            args = self.parser.parse_command(command)
            assert args.focus == expected_type
    
    def test_depth_aliases(self):
        """Test all depth level aliases"""
        depth_tests = [
            ('q', DepthType.QUICK),
            ('quick', DepthType.QUICK),
            ('fast', DepthType.QUICK),
            ('s', DepthType.STANDARD),
            ('standard', DepthType.STANDARD),
            ('normal', DepthType.STANDARD),
            ('d', DepthType.DEEP),
            ('deep', DepthType.DEEP),
            ('detailed', DepthType.DEEP),
            ('comprehensive', DepthType.DEEP),
        ]
        
        for alias, expected_type in depth_tests:
            command = f"/sq:note {self.temp_pdf} --depth {alias}"
            args = self.parser.parse_command(command)
            assert args.depth == expected_type
    
    def test_format_aliases(self):
        """Test all format type aliases"""
        format_tests = [
            ('md', FormatType.MARKDOWN),
            ('markdown', FormatType.MARKDOWN),
        ]
        
        for alias, expected_type in format_tests:
            command = f"/sq:note {self.temp_pdf} --format {alias}"
            args = self.parser.parse_command(command)
            assert args.format == expected_type
    
    def test_get_help_text(self):
        """Test help text generation"""
        help_text = self.parser.get_help_text()
        
        assert "/sq:note" in help_text
        assert "--focus" in help_text
        assert "--depth" in help_text
        assert "--format" in help_text
        assert "--batch" in help_text
        assert "--output-dir" in help_text
        assert "Examples:" in help_text


class TestCreateCommandValidationError:
    """Test the create_command_validation_error helper function"""
    
    def test_create_validation_error(self):
        """Test creating a validation error"""
        error = create_command_validation_error(
            field="focus",
            value="invalid",
            valid_options=["research", "theory", "review"]
        )
        
        assert isinstance(error, ValidationError)
        assert error.error_code == ErrorCode.INVALID_ARGUMENTS
        assert "Invalid focus: invalid" in str(error)
        assert "research, theory, review" in error.suggestions[0]


if __name__ == "__main__":
    pytest.main([__file__])