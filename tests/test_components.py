#!/usr/bin/env python3
"""
Test individual components of ScholarsQuill Kiro
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Test that basic modules can be imported"""
    print("Testing basic imports...")
    
    try:
        from models import PaperMetadata, FocusType, DepthType
        from config import ServerConfig
        from exceptions import PDFProcessingError
        from utils import sanitize_filename, generate_citekey
        print("✓ Basic imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_models():
    """Test data models"""
    print("Testing data models...")
    
    from models import PaperMetadata, FocusType, DepthType, ProcessingOptions
    
    # Test PaperMetadata
    metadata = PaperMetadata(
        title="Test Paper",
        first_author="Smith",
        authors=["Smith, John", "Doe, Jane"],
        year=2023
    )
    assert metadata.title == "Test Paper"
    assert len(metadata.authors) == 2
    
    # Test ProcessingOptions
    options = ProcessingOptions(
        focus=FocusType.RESEARCH,
        depth=DepthType.DEEP
    )
    assert options.focus == FocusType.RESEARCH
    assert options.depth == DepthType.DEEP
    
    print("✓ Data models work correctly")
    return True


def test_config():
    """Test configuration"""
    print("Testing configuration...")
    
    from config import ServerConfig, ConfigManager
    
    # Test default config
    config = ServerConfig()
    assert config.default_output_dir == "literature-notes"
    assert config.max_file_size_mb == 50
    
    # Test validation
    config.validate()
    
    # Test config manager
    manager = ConfigManager()
    assert manager.server is not None
    assert manager.processing is not None
    
    print("✓ Configuration works correctly")
    return True


def test_utilities():
    """Test utility functions"""
    print("Testing utilities...")
    
    from utils import sanitize_filename, generate_citekey, format_file_size
    
    # Test filename sanitization
    safe_name = sanitize_filename("Test<>File|Name?.pdf")
    assert "<" not in safe_name
    assert ">" not in safe_name
    assert "|" not in safe_name
    assert "?" not in safe_name
    
    # Test citekey generation
    citekey = generate_citekey("Smith, John", 2023, "Machine Learning Paper")
    assert "smith" in citekey.lower()
    assert "2023" in citekey
    
    # Test file size formatting
    size_str = format_file_size(1024 * 1024)  # 1MB
    assert "1.0 MB" == size_str
    
    print("✓ Utilities work correctly")
    return True


def test_exceptions():
    """Test exception handling"""
    print("Testing exceptions...")
    
    from exceptions import (
        PDFProcessingError, ContentAnalysisError, NoteGenerationError,
        ErrorCode, ErrorType, create_file_not_found_error
    )
    
    # Test basic exception
    error = PDFProcessingError("Test error", ErrorCode.TEXT_EXTRACTION_FAILED)
    assert "Test error" in str(error)
    assert error.error_code == ErrorCode.TEXT_EXTRACTION_FAILED
    
    # Test error response
    response = error.to_error_response()
    assert response.success is False
    assert "Test error" in response.error_message
    
    # Test helper function
    file_error = create_file_not_found_error("test.pdf")
    assert "test.pdf" in str(file_error)
    assert file_error.error_code == ErrorCode.FILE_NOT_FOUND
    
    print("✓ Exception handling works correctly")
    return True


def test_interfaces():
    """Test that interfaces are properly defined"""
    print("Testing interfaces...")
    
    from interfaces import (
        PDFProcessorInterface, ContentAnalyzerInterface, NoteGeneratorInterface,
        CommandParserInterface, BatchProcessorInterface
    )
    
    # Test that interfaces have required methods
    assert hasattr(PDFProcessorInterface, 'extract_text')
    assert hasattr(PDFProcessorInterface, 'extract_metadata')
    assert hasattr(ContentAnalyzerInterface, 'analyze_content')
    assert hasattr(NoteGeneratorInterface, 'generate_note')
    assert hasattr(CommandParserInterface, 'parse_command')
    assert hasattr(BatchProcessorInterface, 'process_directory')
    
    print("✓ Interfaces are properly defined")
    return True


def main():
    """Run all component tests"""
    print("Running ScholarsQuill Kiro Component Tests")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_models,
        test_config,
        test_utilities,
        test_exceptions,
        test_interfaces
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All component tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())