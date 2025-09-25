"""
Integration tests for ScholarsQuill MCP Server
"""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from src.server import ScholarsQuillServer
from src.config import ServerConfig
from src.models import PaperMetadata, FocusType, DepthType, FormatType
from src.exceptions import FileError, ProcessingError


class TestScholarsQuillServer:
    """Test cases for the main MCP server class"""
    
    @pytest.fixture
    def server_config(self):
        """Create test server configuration"""
        return ServerConfig(
            default_output_dir="test-output",
            default_templates_dir="test-templates",
            max_file_size_mb=10,
            batch_size_limit=5,
            enable_caching=False,
            log_level="DEBUG"
        )
    
    @pytest.fixture
    def server(self, server_config):
        """Create test server instance"""
        return ScholarsQuillServer(server_config)
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample paper metadata"""
        return PaperMetadata(
            title="Test Paper Title",
            first_author="Smith",
            authors=["Smith, John", "Doe, Jane"],
            year=2023,
            citekey="smith2023test",
            journal="Test Journal",
            doi="10.1000/test",
            page_count=10
        )
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """Test server initialization"""
        assert server.config is not None
        assert server.pdf_processor is not None
        assert server.content_analyzer is not None
        assert server.note_generator is not None
        assert server.command_parser is not None
        assert server.batch_processor is not None
        
        # Test initialization method
        await server.initialize()
        
        # Check that directories are created
        assert Path(server.config.default_output_dir).exists()
    
    @pytest.mark.asyncio
    async def test_process_single_file_success(self, server, sample_metadata, tmp_path):
        """Test successful single file processing"""
        # Create a test PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("dummy pdf content")
        
        # Mock the components
        with patch.object(server.pdf_processor, 'extract_text', return_value="Sample text content"), \
             patch.object(server.pdf_processor, 'extract_metadata', return_value=sample_metadata), \
             patch.object(server.content_analyzer, 'analyze_content') as mock_analyze, \
             patch.object(server.note_generator, 'generate_note', return_value="# Test Note\n\nContent"):
            
            # Setup mock analysis result
            mock_analyze.return_value = Mock(
                paper_type="research",
                confidence=0.9,
                sections={"abstract": "test abstract", "introduction": "test intro"},
                key_concepts=["concept1", "concept2"]
            )
            
            # Process the file
            result = await server.process_note_command(
                target=str(test_pdf),
                focus="research",
                depth="standard"
            )
            
            # Verify result
            assert result["success"] is True
            assert "note_content" in result
            assert "output_path" in result
            assert "metadata" in result
            assert "analysis" in result
            assert result["metadata"]["title"] == "Test Paper Title"
            assert result["analysis"]["paper_type"] == "research"
    
    @pytest.mark.asyncio
    async def test_process_single_file_not_found(self, server):
        """Test processing non-existent file"""
        result = await server.process_note_command(
            target="nonexistent.pdf"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "FileNotFoundError" in result["error_type"]
    
    @pytest.mark.asyncio
    async def test_process_single_file_invalid_pdf(self, server, tmp_path):
        """Test processing non-PDF file"""
        # Create a non-PDF file
        test_file = tmp_path / "test.txt"
        test_file.write_text("not a pdf")
        
        result = await server.process_note_command(
            target=str(test_file)
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "ValueError" in result["error_type"]
    
    @pytest.mark.asyncio
    async def test_process_batch_success(self, server, sample_metadata, tmp_path):
        """Test successful batch processing"""
        # Create test directory with PDF files
        test_dir = tmp_path / "pdfs"
        test_dir.mkdir()
        
        pdf1 = test_dir / "paper1.pdf"
        pdf2 = test_dir / "paper2.pdf"
        pdf1.write_text("dummy pdf 1")
        pdf2.write_text("dummy pdf 2")
        
        # Mock batch processor
        mock_results = [
            {"success": True, "file_path": str(pdf1), "output_path": "output1.md"},
            {"success": True, "file_path": str(pdf2), "output_path": "output2.md"}
        ]
        
        with patch.object(server.batch_processor, 'process_directory', return_value=mock_results):
            result = await server.process_note_command(
                target=str(test_dir),
                batch=True
            )
            
            assert result["success"] is True
            assert "batch_results" in result
            assert "summary" in result
            assert result["summary"]["total_files"] == 2
            assert result["summary"]["successful"] == 2
            assert result["summary"]["failed"] == 0
    
    @pytest.mark.asyncio
    async def test_analyze_paper_type_success(self, server, sample_metadata, tmp_path):
        """Test successful paper type analysis"""
        # Create test PDF
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("dummy pdf content")
        
        with patch.object(server.pdf_processor, 'extract_text', return_value="Sample research content"), \
             patch.object(server.pdf_processor, 'extract_metadata', return_value=sample_metadata), \
             patch.object(server.content_analyzer, 'classify_paper_type', return_value=("research", 0.85)), \
             patch.object(server.content_analyzer, 'extract_sections', return_value={"abstract": "test"}):
            
            result = await server.analyze_paper_type(str(test_pdf))
            
            assert result["success"] is True
            assert result["paper_type"] == "research"
            assert result["confidence_score"] == 0.85
            assert "metadata" in result
            assert "sections_detected" in result
    
    @pytest.mark.asyncio
    async def test_get_available_templates(self, server):
        """Test getting available templates"""
        result = await server.get_available_templates()
        
        assert result["success"] is True
        assert "templates" in result
        assert "focus_types" in result
        assert "depth_levels" in result
        assert "supported_formats" in result
        
        # Check that all focus types are included
        templates = result["templates"]
        assert "research" in templates
        assert "theory" in templates
        assert "review" in templates
        assert "method" in templates
        assert "balanced" in templates
        
        # Check template structure
        research_template = templates["research"]
        assert "name" in research_template
        assert "description" in research_template
        assert "focus" in research_template
        assert "sections" in research_template
    
    @pytest.mark.asyncio
    async def test_mcp_tool_registration(self, server):
        """Test that MCP tools are properly registered"""
        mcp_server = server.get_server()
        
        # Check that tools are registered (this would require access to server internals)
        # For now, just verify the server instance exists
        assert mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_processing_error(self, server, tmp_path):
        """Test error handling for processing errors"""
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_text("dummy pdf content")
        
        # Mock a processing error
        with patch.object(server.pdf_processor, 'extract_text', side_effect=Exception("Processing failed")):
            result = await server.process_note_command(target=str(test_pdf))
            
            assert result["success"] is False
            assert "error" in result
            assert "error_type" in result
    
    @pytest.mark.asyncio
    async def test_command_parsing_integration(self, server):
        """Test command parsing integration"""
        # Mock command parser
        with patch.object(server.command_parser, 'parse_command') as mock_parse, \
             patch.object(server.command_parser, 'validate_arguments', return_value=True):
            
            # Setup mock return value
            from src.models import CommandArgs
            mock_args = CommandArgs(
                target="test.pdf",
                focus=FocusType.RESEARCH,
                depth=DepthType.STANDARD,
                format=FormatType.MARKDOWN
            )
            mock_parse.return_value = mock_args
            
            # This would trigger command parsing
            result = await server.process_note_command(
                target="test.pdf",
                focus="research"
            )
            
            # Verify command parser was called
            mock_parse.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_file_size_validation(self, server, tmp_path):
        """Test file size validation"""
        # Create a file that exceeds the size limit
        test_pdf = tmp_path / "large.pdf"
        # Write content that would exceed the 10MB limit set in test config
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        test_pdf.write_text(large_content)
        
        result = await server.process_note_command(target=str(test_pdf))
        
        assert result["success"] is False
        assert "error" in result
        assert "too large" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_shutdown_gracefully(self, server):
        """Test graceful server shutdown"""
        # This should not raise any exceptions
        await server.shutdown()


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance"""
    
    @pytest.fixture
    def server(self):
        """Create server for protocol testing"""
        config = ServerConfig(log_level="DEBUG")
        return ScholarsQuillServer(config)
    
    @pytest.mark.asyncio
    async def test_tool_schema_definitions(self, server):
        """Test that tools have proper schema definitions"""
        # This would require access to MCP server internals
        # For now, verify server can be created without errors
        assert server is not None
        
        # Test that the main tool method exists and is callable
        assert hasattr(server, 'process_note_command')
        assert callable(server.process_note_command)
    
    @pytest.mark.asyncio
    async def test_resource_listing(self, server):
        """Test resource listing functionality"""
        # The resource listing is handled by the MCP decorators
        # We can test the underlying methods
        templates = await server.get_available_templates()
        assert templates["success"] is True
    
    @pytest.mark.asyncio
    async def test_error_response_format(self, server):
        """Test that error responses follow MCP format"""
        result = await server.analyze_paper_type("nonexistent.pdf")
        
        assert result["success"] is False
        assert "error" in result
        assert "error_type" in result
        
        # Error should be a string (MCP compatible)
        assert isinstance(result["error"], str)
        assert isinstance(result["error_type"], str)


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end integration tests"""
    
    @pytest.fixture
    def server(self):
        """Create server for end-to-end testing"""
        config = ServerConfig(
            default_output_dir="test-e2e-output",
            log_level="DEBUG"
        )
        return ScholarsQuillServer(config)
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, server, tmp_path):
        """Test complete workflow from PDF to note"""
        # This test would require actual PDF processing capabilities
        # For now, we'll mock the components but test the full flow
        
        test_pdf = tmp_path / "research_paper.pdf"
        test_pdf.write_text("dummy research paper content")
        
        sample_metadata = PaperMetadata(
            title="Advanced Machine Learning Techniques",
            first_author="Johnson",
            authors=["Johnson, Alice", "Smith, Bob"],
            year=2023,
            citekey="johnson2023advanced",
            journal="AI Research Journal",
            doi="10.1000/ai.2023.001",
            page_count=15
        )
        
        with patch.object(server.pdf_processor, 'extract_text', return_value="Research paper content about ML"), \
             patch.object(server.pdf_processor, 'extract_metadata', return_value=sample_metadata), \
             patch.object(server.content_analyzer, 'analyze_content') as mock_analyze, \
             patch.object(server.note_generator, 'generate_note', return_value="# Research Note\n\nML content"):
            
            mock_analyze.return_value = Mock(
                paper_type="research",
                confidence=0.92,
                sections={"abstract": "ML abstract", "methodology": "ML methods"},
                key_concepts=["machine learning", "neural networks"]
            )
            
            # Process with different focus types
            for focus in ["research", "theory", "balanced"]:
                result = await server.process_note_command(
                    target=str(test_pdf),
                    focus=focus,
                    depth="standard"
                )
                
                assert result["success"] is True
                assert result["processing_options"]["focus"] == focus
                assert Path(result["output_path"]).exists()
                
                # Clean up
                Path(result["output_path"]).unlink()
    
    @pytest.mark.asyncio
    async def test_batch_processing_workflow(self, server, tmp_path):
        """Test batch processing workflow"""
        # Create test directory with multiple PDFs
        batch_dir = tmp_path / "batch_test"
        batch_dir.mkdir()
        
        # Create multiple test PDFs
        for i in range(3):
            pdf_file = batch_dir / f"paper_{i}.pdf"
            pdf_file.write_text(f"Content of paper {i}")
        
        # Mock batch processing
        mock_results = []
        for i in range(3):
            mock_results.append({
                "success": True,
                "file_path": str(batch_dir / f"paper_{i}.pdf"),
                "output_path": f"output_{i}.md",
                "metadata": {"title": f"Paper {i}"}
            })
        
        with patch.object(server.batch_processor, 'process_directory', return_value=mock_results):
            result = await server.process_note_command(
                target=str(batch_dir),
                batch=True,
                focus="balanced"
            )
            
            assert result["success"] is True
            assert result["summary"]["total_files"] == 3
            assert result["summary"]["successful"] == 3
            assert result["summary"]["success_rate"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])