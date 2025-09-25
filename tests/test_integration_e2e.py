"""
End-to-end integration tests for ScholarsQuill Kiro MCP Server
Tests complete workflow from PDF input to markdown output
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from src.server import ScholarsQuillKiroServer
from src.main import ScholarsQuillKiroCLI
from src.config import ServerConfig
from src.models import PaperMetadata, AnalysisResult, FocusType, DepthType


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        
        # Create subdirectories
        (workspace / "pdfs").mkdir()
        (workspace / "output").mkdir()
        (workspace / "templates").mkdir()
        
        yield workspace


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing"""
    return """
    Title: Advanced Machine Learning Techniques for Scientific Research
    
    Abstract:
    This paper presents novel machine learning approaches for analyzing scientific data.
    We propose a new neural network architecture that improves accuracy by 15%.
    
    1. Introduction
    Machine learning has revolutionized scientific research in recent years.
    Our work builds upon previous studies in deep learning and neural networks.
    
    2. Methodology
    We used a dataset of 10,000 scientific papers to train our model.
    The neural network consists of 5 layers with ReLU activation functions.
    
    3. Results
    Our approach achieved 92% accuracy on the test set.
    The model showed significant improvements over baseline methods.
    
    4. Conclusion
    This work demonstrates the potential of advanced ML techniques in science.
    Future work will explore applications to other domains.
    
    References:
    [1] Smith, J. et al. (2022). Deep Learning for Science. Nature.
    [2] Doe, A. (2021). Neural Networks in Research. Science.
    """


@pytest.fixture
def sample_metadata():
    """Sample paper metadata"""
    return PaperMetadata(
        title="Advanced Machine Learning Techniques for Scientific Research",
        first_author="Johnson",
        authors=["Johnson, Alice", "Smith, Bob", "Doe, Carol"],
        year=2023,
        citekey="johnson2023advanced",
        journal="Journal of Machine Learning Research",
        doi="10.1000/jmlr.2023.001",
        page_count=12,
        abstract="This paper presents novel machine learning approaches for analyzing scientific data."
    )


@pytest.fixture
def sample_analysis_result():
    """Sample content analysis result"""
    return AnalysisResult(
        paper_type="research",
        confidence=0.89,
        sections={
            "abstract": "This paper presents novel machine learning approaches...",
            "introduction": "Machine learning has revolutionized scientific research...",
            "methodology": "We used a dataset of 10,000 scientific papers...",
            "results": "Our approach achieved 92% accuracy on the test set...",
            "conclusion": "This work demonstrates the potential of advanced ML..."
        },
        key_concepts=["machine learning", "neural networks", "scientific research", "deep learning"],
        equations=["accuracy = correct_predictions / total_predictions"],
        methodologies=["neural network training", "dataset analysis", "performance evaluation"]
    )


@pytest.fixture
def sample_note_content():
    """Sample generated note content"""
    return """# Advanced Machine Learning Techniques for Scientific Research

> [!Metadata]
> **FirstAuthor**:: Johnson, Alice
> **Author**:: , Smith, Bob
> **Author**:: , Doe, Carol
> **Title**:: Advanced Machine Learning Techniques for Scientific Research
> **Year**:: 2023
> **Citekey**:: johnson2023advanced
> **itemType**:: journalArticle
> **Journal**:: *Journal of Machine Learning Research*
> **DOI**:: 10.1000/jmlr.2023.001

## Executive Summary

This research paper presents novel machine learning approaches for analyzing scientific data, achieving 92% accuracy through a new neural network architecture.

## Key Findings

- Proposed neural network architecture improves accuracy by 15%
- Achieved 92% accuracy on test dataset of 10,000 scientific papers
- Demonstrated significant improvements over baseline methods

## Methodology

The study employed a 5-layer neural network with ReLU activation functions, trained on a comprehensive dataset of scientific papers.

## Implications

This work demonstrates the potential for advanced ML techniques to revolutionize scientific research across multiple domains.

## Future Research Directions

- Exploration of applications to other scientific domains
- Investigation of larger datasets and more complex architectures
"""


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_single_file_workflow(
        self, temp_workspace, sample_pdf_content, sample_metadata, 
        sample_analysis_result, sample_note_content
    ):
        """Test complete workflow for single file processing"""
        # Setup
        config = ServerConfig(
            default_output_dir=str(temp_workspace / "output"),
            default_templates_dir=str(temp_workspace / "templates"),
            log_level="DEBUG"
        )
        server = ScholarsQuillKiroServer(config)
        await server.initialize()
        
        # Create test PDF file
        test_pdf = temp_workspace / "pdfs" / "test_paper.pdf"
        test_pdf.write_text(sample_pdf_content)
        
        # Mock all components
        with patch.object(server.pdf_processor, 'extract_text', return_value=sample_pdf_content), \
             patch.object(server.pdf_processor, 'extract_metadata', return_value=sample_metadata), \
             patch.object(server.content_analyzer, 'analyze_content', return_value=sample_analysis_result), \
             patch.object(server.note_generator, 'generate_note', return_value=sample_note_content):
            
            # Execute workflow
            result = await server.process_note_command(
                target=str(test_pdf),
                focus="research",
                depth="standard"
            )
            
            # Verify result structure
            assert result["success"] is True
            assert "note_content" in result
            assert "output_path" in result
            assert "metadata" in result
            assert "analysis" in result
            assert "timing" in result
            
            # Verify metadata
            metadata = result["metadata"]
            assert metadata["title"] == sample_metadata.title
            assert metadata["first_author"] == sample_metadata.first_author
            assert metadata["year"] == sample_metadata.year
            
            # Verify analysis
            analysis = result["analysis"]
            assert analysis["paper_type"] == "research"
            assert analysis["confidence"] == 0.89
            assert len(analysis["key_concepts"]) == 4
            
            # Verify file was created
            output_path = Path(result["output_path"])
            assert output_path.exists()
            assert output_path.read_text() == sample_note_content
            
            # Verify timing information
            timing = result["timing"]
            assert "total_time_seconds" in timing
            assert "extraction_time_seconds" in timing
            assert "analysis_time_seconds" in timing
            assert "generation_time_seconds" in timing
        
        await server.shutdown()
    
    @pytest.mark.asyncio
    async def test_complete_batch_workflow(
        self, temp_workspace, sample_pdf_content, sample_metadata,
        sample_analysis_result, sample_note_content
    ):
        """Test complete workflow for batch processing"""
        # Setup
        config = ServerConfig(
            default_output_dir=str(temp_workspace / "output"),
            batch_size_limit=10,
            log_level="DEBUG"
        )
        server = ScholarsQuillKiroServer(config)
        await server.initialize()
        
        # Create multiple test PDF files
        pdf_dir = temp_workspace / "pdfs"
        test_files = []
        for i in range(3):
            test_pdf = pdf_dir / f"paper_{i}.pdf"
            test_pdf.write_text(f"Paper {i} content: {sample_pdf_content}")
            test_files.append(test_pdf)
        
        # Mock batch processor
        mock_batch_results = []
        for i, test_file in enumerate(test_files):
            mock_batch_results.append({
                "success": True,
                "file_path": str(test_file),
                "output_path": str(temp_workspace / "output" / f"paper_{i}_literature_note.md"),
                "metadata": {
                    "title": f"Test Paper {i}",
                    "first_author": "TestAuthor",
                    "year": 2023
                },
                "timing": {"total_time_seconds": 2.5}
            })
        
        with patch.object(server.batch_processor, 'process_directory', return_value=mock_batch_results):
            # Execute batch workflow
            result = await server.process_note_command(
                target=str(pdf_dir),
                focus="balanced",
                depth="standard",
                batch=True
            )
            
            # Verify batch result structure
            assert result["success"] is True
            assert "batch_results" in result
            assert "summary" in result
            assert "timing_statistics" in result
            
            # Verify summary
            summary = result["summary"]
            assert summary["total_files"] == 3
            assert summary["successful"] == 3
            assert summary["failed"] == 0
            assert summary["success_rate"] == 1.0
            
            # Verify timing statistics
            timing_stats = result["timing_statistics"]
            assert "average_per_file_seconds" in timing_stats
            assert "fastest_file_seconds" in timing_stats
            assert "slowest_file_seconds" in timing_stats
        
        await server.shutdown()
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, temp_workspace):
        """Test error handling throughout the workflow"""
        config = ServerConfig(
            default_output_dir=str(temp_workspace / "output"),
            log_level="DEBUG"
        )
        server = ScholarsQuillKiroServer(config)
        await server.initialize()
        
        # Test file not found
        result = await server.process_note_command(target="nonexistent.pdf")
        assert result["success"] is False
        assert "FileNotFoundError" in result["error_type"]
        assert result["processing_stage"] == "file_validation"
        
        # Test invalid file type
        text_file = temp_workspace / "not_a_pdf.txt"
        text_file.write_text("This is not a PDF")
        
        result = await server.process_note_command(target=str(text_file))
        assert result["success"] is False
        assert "ValueError" in result["error_type"]
        assert result["processing_stage"] == "file_validation"
        
        # Test PDF processing error
        test_pdf = temp_workspace / "test.pdf"
        test_pdf.write_text("dummy content")
        
        with patch.object(server.pdf_processor, 'extract_text', side_effect=Exception("PDF extraction failed")):
            result = await server.process_note_command(target=str(test_pdf))
            assert result["success"] is False
            assert result["processing_stage"] == "pdf_processing"
        
        await server.shutdown()
    
    @pytest.mark.asyncio
    async def test_different_focus_types(
        self, temp_workspace, sample_pdf_content, sample_metadata,
        sample_analysis_result, sample_note_content
    ):
        """Test workflow with different focus types"""
        config = ServerConfig(
            default_output_dir=str(temp_workspace / "output"),
            log_level="DEBUG"
        )
        server = ScholarsQuillKiroServer(config)
        await server.initialize()
        
        test_pdf = temp_workspace / "test.pdf"
        test_pdf.write_text(sample_pdf_content)
        
        focus_types = ["research", "theory", "review", "method", "balanced"]
        
        with patch.object(server.pdf_processor, 'extract_text', return_value=sample_pdf_content), \
             patch.object(server.pdf_processor, 'extract_metadata', return_value=sample_metadata), \
             patch.object(server.content_analyzer, 'analyze_content', return_value=sample_analysis_result), \
             patch.object(server.note_generator, 'generate_note', return_value=sample_note_content):
            
            for focus in focus_types:
                result = await server.process_note_command(
                    target=str(test_pdf),
                    focus=focus,
                    depth="standard"
                )
                
                assert result["success"] is True
                assert result["processing_options"]["focus"] == focus
                
                # Verify unique output files
                output_path = Path(result["output_path"])
                assert output_path.exists()
                
                # Clean up for next iteration
                output_path.unlink()
        
        await server.shutdown()


class TestCLIIntegration:
    """Test CLI integration with the server"""
    
    @pytest.mark.asyncio
    async def test_cli_single_file_processing(
        self, temp_workspace, sample_pdf_content, sample_metadata,
        sample_analysis_result, sample_note_content
    ):
        """Test CLI single file processing"""
        cli = ScholarsQuillKiroCLI()
        
        config = ServerConfig(
            default_output_dir=str(temp_workspace / "output"),
            log_level="DEBUG"
        )
        await cli.initialize(config)
        
        # Create test file
        test_pdf = temp_workspace / "test.pdf"
        test_pdf.write_text(sample_pdf_content)
        
        # Mock components
        with patch.object(cli.server.pdf_processor, 'extract_text', return_value=sample_pdf_content), \
             patch.object(cli.server.pdf_processor, 'extract_metadata', return_value=sample_metadata), \
             patch.object(cli.server.content_analyzer, 'analyze_content', return_value=sample_analysis_result), \
             patch.object(cli.server.note_generator, 'generate_note', return_value=sample_note_content):
            
            result = await cli.process_file(
                str(test_pdf),
                focus="research",
                depth="deep",
                verbose=True
            )
            
            assert result["success"] is True
            assert result["processing_options"]["focus"] == "research"
            assert result["processing_options"]["depth"] == "deep"
        
        await cli.shutdown()
    
    @pytest.mark.asyncio
    async def test_cli_batch_processing(self, temp_workspace):
        """Test CLI batch processing"""
        cli = ScholarsQuillKiroCLI()
        
        config = ServerConfig(
            default_output_dir=str(temp_workspace / "output"),
            log_level="DEBUG"
        )
        await cli.initialize(config)
        
        # Create test directory with PDFs
        pdf_dir = temp_workspace / "pdfs"
        for i in range(2):
            (pdf_dir / f"paper_{i}.pdf").write_text(f"Content {i}")
        
        # Mock batch processing
        mock_results = [
            {"success": True, "file_path": str(pdf_dir / "paper_0.pdf")},
            {"success": True, "file_path": str(pdf_dir / "paper_1.pdf")}
        ]
        
        with patch.object(cli.server.batch_processor, 'process_directory', return_value=mock_results):
            result = await cli.process_batch(
                str(pdf_dir),
                focus="theory",
                verbose=True
            )
            
            assert result["success"] is True
            assert result["summary"]["total_files"] == 2
        
        await cli.shutdown()
    
    @pytest.mark.asyncio
    async def test_cli_paper_analysis(
        self, temp_workspace, sample_pdf_content, sample_metadata
    ):
        """Test CLI paper analysis"""
        cli = ScholarsQuillKiroCLI()
        
        config = ServerConfig(log_level="DEBUG")
        await cli.initialize(config)
        
        test_pdf = temp_workspace / "test.pdf"
        test_pdf.write_text(sample_pdf_content)
        
        with patch.object(cli.server.pdf_processor, 'extract_text', return_value=sample_pdf_content), \
             patch.object(cli.server.pdf_processor, 'extract_metadata', return_value=sample_metadata), \
             patch.object(cli.server.content_analyzer, 'classify_paper_type', return_value=("research", 0.85)), \
             patch.object(cli.server.content_analyzer, 'extract_sections', return_value={"abstract": "test"}):
            
            result = await cli.analyze_paper(str(test_pdf), verbose=True)
            
            assert result["success"] is True
            assert result["paper_type"] == "research"
            assert result["confidence_score"] == 0.85
        
        await cli.shutdown()
    
    @pytest.mark.asyncio
    async def test_cli_template_listing(self, temp_workspace):
        """Test CLI template listing"""
        cli = ScholarsQuillKiroCLI()
        
        config = ServerConfig(log_level="DEBUG")
        await cli.initialize(config)
        
        result = await cli.list_templates(verbose=True)
        
        assert result["success"] is True
        assert "templates" in result
        assert len(result["templates"]) == 5  # research, theory, review, method, balanced
        
        # Verify all expected templates are present
        expected_templates = ["research", "theory", "review", "method", "balanced"]
        for template_name in expected_templates:
            assert template_name in result["templates"]
        
        await cli.shutdown()


class TestMCPServerIntegration:
    """Test MCP server protocol integration"""
    
    @pytest.mark.asyncio
    async def test_mcp_tool_execution(
        self, temp_workspace, sample_pdf_content, sample_metadata,
        sample_analysis_result, sample_note_content
    ):
        """Test MCP tool execution through server"""
        config = ServerConfig(
            default_output_dir=str(temp_workspace / "output"),
            log_level="DEBUG"
        )
        server = ScholarsQuillKiroServer(config)
        await server.initialize()
        
        test_pdf = temp_workspace / "test.pdf"
        test_pdf.write_text(sample_pdf_content)
        
        # Mock components for MCP tool execution
        with patch.object(server.pdf_processor, 'extract_text', return_value=sample_pdf_content), \
             patch.object(server.pdf_processor, 'extract_metadata', return_value=sample_metadata), \
             patch.object(server.content_analyzer, 'analyze_content', return_value=sample_analysis_result), \
             patch.object(server.note_generator, 'generate_note', return_value=sample_note_content):
            
            # This simulates what would happen when MCP calls the tool
            result = await server.process_note_command(
                target=str(test_pdf),
                focus="research",
                depth="standard"
            )
            
            # Verify MCP-compatible response format
            assert isinstance(result, dict)
            assert "success" in result
            assert result["success"] is True
            
            # Verify all required fields are present and properly typed
            assert isinstance(result["note_content"], str)
            assert isinstance(result["output_path"], str)
            assert isinstance(result["metadata"], dict)
            assert isinstance(result["analysis"], dict)
            assert isinstance(result["timing"], dict)
        
        await server.shutdown()
    
    @pytest.mark.asyncio
    async def test_mcp_error_response_format(self, temp_workspace):
        """Test MCP error response format"""
        config = ServerConfig(log_level="DEBUG")
        server = ScholarsQuillKiroServer(config)
        await server.initialize()
        
        # Test with non-existent file
        result = await server.process_note_command(target="nonexistent.pdf")
        
        # Verify MCP-compatible error response
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "error_type" in result
        
        # Verify error fields are strings (MCP compatible)
        assert isinstance(result["error"], str)
        assert isinstance(result["error_type"], str)
        
        await server.shutdown()


@pytest.mark.integration
class TestPerformanceAndScaling:
    """Test performance and scaling characteristics"""
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(
        self, temp_workspace, sample_pdf_content, sample_metadata,
        sample_analysis_result, sample_note_content
    ):
        """Test concurrent file processing"""
        config = ServerConfig(
            default_output_dir=str(temp_workspace / "output"),
            log_level="DEBUG"
        )
        server = ScholarsQuillKiroServer(config)
        await server.initialize()
        
        # Create multiple test files
        test_files = []
        for i in range(5):
            test_pdf = temp_workspace / f"paper_{i}.pdf"
            test_pdf.write_text(f"Paper {i}: {sample_pdf_content}")
            test_files.append(test_pdf)
        
        # Mock components
        with patch.object(server.pdf_processor, 'extract_text', return_value=sample_pdf_content), \
             patch.object(server.pdf_processor, 'extract_metadata', return_value=sample_metadata), \
             patch.object(server.content_analyzer, 'analyze_content', return_value=sample_analysis_result), \
             patch.object(server.note_generator, 'generate_note', return_value=sample_note_content):
            
            # Process files concurrently
            tasks = []
            for test_file in test_files:
                task = server.process_note_command(
                    target=str(test_file),
                    focus="balanced"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # Verify all succeeded
            for result in results:
                assert result["success"] is True
            
            # Verify unique output files
            output_paths = [result["output_path"] for result in results]
            assert len(set(output_paths)) == len(output_paths)  # All unique
        
        await server.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])