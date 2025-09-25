#!/usr/bin/env python3
"""
Basic test script for ScholarsQuill Kiro Server components
Tests the core logic without MCP dependencies
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import PaperMetadata, AnalysisResult, FocusType, DepthType, FormatType
from config import ServerConfig
from exceptions import PDFProcessingError, ContentAnalysisError, NoteGenerationError


def test_config():
    """Test configuration classes"""
    print("Testing configuration...")
    
    # Test default config
    config = ServerConfig()
    assert config.default_output_dir == "literature-notes"
    assert config.max_file_size_mb == 50
    assert config.batch_size_limit == 100
    
    # Test validation
    config.validate()
    
    print("✓ Configuration tests passed")


def test_models():
    """Test data models"""
    print("Testing data models...")
    
    # Test PaperMetadata
    metadata = PaperMetadata(
        title="Test Paper",
        first_author="Smith",
        authors=["Smith, John", "Doe, Jane"],
        year=2023
    )
    assert metadata.title == "Test Paper"
    assert len(metadata.authors) == 2
    
    # Test AnalysisResult
    analysis = AnalysisResult(
        paper_type="research",
        confidence=0.85,
        sections={"abstract": "test"},
        key_concepts=["concept1", "concept2"]
    )
    assert analysis.paper_type == "research"
    assert len(analysis.key_concepts) == 2
    
    print("✓ Data model tests passed")


def test_exceptions():
    """Test exception classes"""
    print("Testing exceptions...")
    
    # Test PDFProcessingError
    error = PDFProcessingError("Test error", None)
    assert "Test error" in str(error)
    
    # Test error response
    response = error.to_error_response()
    assert response.success is False
    assert "Test error" in response.error_message
    
    print("✓ Exception tests passed")


async def test_server_logic():
    """Test server logic without MCP dependencies"""
    print("Testing server logic...")
    
    # Mock the imports for server_core
    with patch.dict('sys.modules', {
        'src.models': sys.modules['models'],
        'src.interfaces': sys.modules['interfaces'],
        'src.pdf_processor': sys.modules['pdf_processor'],
        'src.content_analyzer': sys.modules['content_analyzer'],
        'src.note_generator': sys.modules['note_generator'],
        'src.command_parser': sys.modules['command_parser'],
        'src.batch_processor': sys.modules['batch_processor'],
        'src.config': sys.modules['config'],
        'src.exceptions': sys.modules['exceptions'],
        'src.utils': sys.modules['utils']
    }):
        # Import core server (no MCP dependencies)
        from server_core import ScholarsQuillKiroCore
    
    # Create server with test config
    config = ServerConfig(
        default_output_dir="test-output",
        log_level="DEBUG"
    )
    
    server = ScholarsQuillKiroCore(config)
    
    # Test that components are initialized
    assert server.config is not None
    assert server.pdf_processor is not None
    assert server.content_analyzer is not None
    assert server.note_generator is not None
    assert server.command_parser is not None
    assert server.batch_processor is not None
    
    print("✓ Server initialization tests passed")
    
    # Test error handling methods
    from exceptions import FileError, ErrorCode, ErrorType
    file_error = FileError("Test file error", ErrorCode.FILE_NOT_FOUND)
    stage = server._get_processing_stage_from_error(file_error)
    assert stage == "file_validation"
    
    print("✓ Server error handling tests passed")
    
    # Test template retrieval
    templates = await server.get_available_templates()
    assert templates["success"] is True
    assert "templates" in templates
    assert len(templates["templates"]) == 5
    
    print("✓ Template retrieval tests passed")


def test_utilities():
    """Test utility functions"""
    print("Testing utilities...")
    
    from utils import sanitize_filename, generate_citekey, format_file_size
    
    # Test filename sanitization
    safe_name = sanitize_filename("Test<>File|Name?.pdf")
    assert "<" not in safe_name
    assert ">" not in safe_name
    assert "|" not in safe_name
    
    # Test citekey generation
    citekey = generate_citekey("Smith, John", 2023, "Machine Learning Paper")
    assert "smith" in citekey.lower()
    assert "2023" in citekey
    assert "machine" in citekey.lower()
    
    # Test file size formatting
    size_str = format_file_size(1024 * 1024)  # 1MB
    assert "1.0 MB" == size_str
    
    print("✓ Utility function tests passed")


async def main():
    """Run all tests"""
    print("Running ScholarsQuill Kiro Server Tests")
    print("=" * 50)
    
    try:
        test_config()
        test_models()
        test_exceptions()
        await test_server_logic()
        test_utilities()
        
        print("=" * 50)
        print("✓ All tests passed successfully!")
        return 0
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))