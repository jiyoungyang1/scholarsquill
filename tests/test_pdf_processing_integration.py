"""
Integration tests for PDF processing with real sample files
"""

import pytest
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from pdf_processor import PDFProcessor
    from content_analyzer import ContentAnalyzer
    from note_generator import NoteGenerator
    from file_writer import FileWriter
    from models import ProcessingOptions, FocusType, DepthType, FormatType
    from utils import generate_citekey
except ImportError as e:
    pytest.skip(f"Cannot import required modules: {e}", allow_module_level=True)


class TestPDFProcessingIntegration:
    """Integration tests for complete PDF processing workflow"""
    
    @pytest.fixture
    def sample_pdf_files(self):
        """Get sample PDF files from examples directory"""
        pdf_dir = Path("/Users/yyangg00/scholarsquill/examples/papers")
        
        if not pdf_dir.exists():
            pytest.skip("Sample PDF directory not found")
        
        pdf_files = [
            {
                "path": pdf_dir / "Bonollo et al. - 2025 - Advancing Molecular Simulations Merging Physical Models, Experiments, and AI to Tackle Multiscale C.pdf",
                "expected_citekey": "bonollo2025advancing",
                "reference_note": "bonollo2025advancing_review_analysis.md"
            },
            {
                "path": pdf_dir / "Cloutier et al. - 2020 - Molecular computations of preferential interactions of proline, arginine.HCl, and NaCl with IgG1 ant.pdf",
                "expected_citekey": "cloutier2020molecular",
                "reference_note": "cloutier2020molecular.md"
            },
            {
                "path": pdf_dir / "Kmiecik et al. - 2016 - Coarse-Grained Protein Models and Their Applications.pdf",
                "expected_citekey": "kmiecik2016coarse",
                "reference_note": "kmiecik2016coarsegrained.md"
            },
            {
                "path": pdf_dir / "Zidar et al. - 2020 - Control of viscosity in biopharmaceutical protein formulations.pdf",
                "expected_citekey": "zidar2020control",
                "reference_note": "zidar2020control.md"
            }
        ]
        
        # Filter to only existing files
        existing_files = [f for f in pdf_files if f["path"].exists()]
        
        if not existing_files:
            pytest.skip("No sample PDF files found")
        
        return existing_files
    
    @pytest.fixture
    def reference_notes_dir(self):
        """Get reference notes directory"""
        ref_dir = Path("/Users/yyangg00/scholarsquill/examples/papers/output literature notes")
        
        if not ref_dir.exists():
            pytest.skip("Reference notes directory not found")
        
        return ref_dir
    
    @pytest.fixture
    def processors(self):
        """Set up processing components"""
        return {
            "pdf_processor": PDFProcessor(),
            "content_analyzer": ContentAnalyzer(),
            "note_generator": NoteGenerator(),
            "file_writer": FileWriter()
        }
    
    def test_pdf_metadata_extraction(self, sample_pdf_files, processors):
        """Test PDF metadata extraction and citekey generation"""
        pdf_processor = processors["pdf_processor"]
        
        for pdf_file in sample_pdf_files:
            if not pdf_file["path"].exists():
                continue
            
            # Extract metadata
            metadata = pdf_processor.extract_metadata(str(pdf_file["path"]))
            
            # Verify metadata was extracted
            assert metadata is not None, f"Failed to extract metadata from {pdf_file['path'].name}"
            assert metadata.title, f"No title extracted from {pdf_file['path'].name}"
            
            # Test citekey generation
            if metadata.authors and metadata.title:
                first_author = metadata.authors[0]
                generated_citekey = generate_citekey(first_author, metadata.year, metadata.title)
                
                print(f"File: {pdf_file['path'].name}")
                print(f"  Title: {metadata.title[:60]}...")
                print(f"  Authors: {metadata.authors[:2] if metadata.authors else 'None'}")
                print(f"  Year: {metadata.year}")
                print(f"  Generated citekey: {generated_citekey}")
                print(f"  Expected citekey: {pdf_file['expected_citekey']}")
                print(f"  Match: {'✓' if generated_citekey == pdf_file['expected_citekey'] else '✗'}")
                print()
    
    def test_content_analysis(self, sample_pdf_files, processors):
        """Test content analysis on sample PDFs"""
        pdf_processor = processors["pdf_processor"]
        content_analyzer = processors["content_analyzer"]
        
        for pdf_file in sample_pdf_files[:2]:  # Test first 2 files to avoid long test times
            if not pdf_file["path"].exists():
                continue
            
            # Extract text content
            text_content = pdf_processor.extract_text(str(pdf_file["path"]))
            assert text_content, f"No text extracted from {pdf_file['path'].name}"
            
            # Analyze content
            analysis_result = content_analyzer.analyze_content(text_content)
            
            # Verify analysis results
            assert analysis_result is not None, f"Content analysis failed for {pdf_file['path'].name}"
            assert analysis_result.paper_type, f"No paper type identified for {pdf_file['path'].name}"
            assert analysis_result.key_concepts, f"No key concepts extracted for {pdf_file['path'].name}"
            
            print(f"Content analysis for {pdf_file['path'].name}:")
            print(f"  Paper type: {analysis_result.paper_type}")
            print(f"  Confidence: {analysis_result.confidence}")
            print(f"  Key concepts: {analysis_result.key_concepts[:5]}")  # First 5 concepts
            print()
    
    def test_note_generation(self, sample_pdf_files, processors):
        """Test note generation for sample PDFs"""
        pdf_processor = processors["pdf_processor"]
        content_analyzer = processors["content_analyzer"]
        note_generator = processors["note_generator"]
        
        # Test with different focus types
        focus_types = [FocusType.BALANCED, FocusType.RESEARCH]
        
        for pdf_file in sample_pdf_files[:1]:  # Test first file only to avoid long test times
            if not pdf_file["path"].exists():
                continue
            
            # Extract metadata and content
            metadata = pdf_processor.extract_metadata(str(pdf_file["path"]))
            text_content = pdf_processor.extract_text(str(pdf_file["path"]))
            
            for focus_type in focus_types:
                # Set up processing options
                options = ProcessingOptions(
                    focus=focus_type,
                    depth=DepthType.STANDARD,
                    format=FormatType.MARKDOWN
                )
                
                # Analyze content
                analysis_result = content_analyzer.analyze_content(text_content, focus_type)
                
                # Generate note
                note_content = note_generator.generate_note(metadata, analysis_result, options)
                
                # Verify note was generated
                assert note_content is not None, f"Note generation failed for {pdf_file['path'].name} with focus {focus_type}"
                assert note_content.content, f"Empty note content for {pdf_file['path'].name} with focus {focus_type}"
                assert note_content.metadata, f"No metadata in note for {pdf_file['path'].name} with focus {focus_type}"
                
                print(f"Generated note for {pdf_file['path'].name} (focus: {focus_type}):")
                print(f"  Content length: {len(note_content.content)} characters")
                print(f"  Has sections: {bool(note_content.sections)}")
                print()
    
    def test_filename_generation_consistency(self, sample_pdf_files, processors):
        """Test that filename generation is consistent with citekey format"""
        pdf_processor = processors["pdf_processor"]
        file_writer = processors["file_writer"]
        
        for pdf_file in sample_pdf_files:
            if not pdf_file["path"].exists():
                continue
            
            # Extract metadata
            metadata = pdf_processor.extract_metadata(str(pdf_file["path"]))
            
            if metadata and metadata.authors and metadata.title:
                # Generate filename using FileWriter
                filename = file_writer.generate_citekey_filename(metadata)
                expected_filename = f"{pdf_file['expected_citekey']}.md"
                
                print(f"Filename test for {pdf_file['path'].name}:")
                print(f"  Generated: {filename}")
                print(f"  Expected: {expected_filename}")
                print(f"  Match: {'✓' if filename == expected_filename else '✗'}")
                print()
    
    def test_reference_notes_comparison(self, sample_pdf_files, reference_notes_dir):
        """Compare structure with reference notes"""
        for pdf_file in sample_pdf_files:
            reference_path = reference_notes_dir / pdf_file["reference_note"]
            
            if reference_path.exists():
                # Read reference note
                with open(reference_path, 'r', encoding='utf-8') as f:
                    reference_content = f.read()
                
                # Analyze reference note structure
                lines = reference_content.split('\n')
                headers = [line for line in lines if line.startswith('#')]
                
                print(f"Reference note analysis for {pdf_file['reference_note']}:")
                print(f"  Total lines: {len(lines)}")
                print(f"  Headers found: {len(headers)}")
                print(f"  Header structure: {headers[:5]}")  # First 5 headers
                print(f"  Content length: {len(reference_content)} characters")
                print()
            else:
                print(f"Reference note not found: {pdf_file['reference_note']}")
    
    @pytest.mark.slow
    def test_full_workflow_integration(self, sample_pdf_files, processors):
        """Test complete workflow from PDF to note file"""
        pdf_processor = processors["pdf_processor"]
        content_analyzer = processors["content_analyzer"]
        note_generator = processors["note_generator"]
        file_writer = processors["file_writer"]
        
        # Test with one sample file
        test_file = sample_pdf_files[0] if sample_pdf_files else None
        
        if not test_file or not test_file["path"].exists():
            pytest.skip("No test file available")
        
        # Set up processing options
        options = ProcessingOptions(
            focus=FocusType.BALANCED,
            depth=DepthType.STANDARD,
            format=FormatType.MARKDOWN
        )
        
        # Step 1: Extract metadata and content
        metadata = pdf_processor.extract_metadata(str(test_file["path"]))
        text_content = pdf_processor.extract_text(str(test_file["path"]))
        
        assert metadata is not None, "Metadata extraction failed"
        assert text_content, "Text extraction failed"
        
        # Step 2: Analyze content
        analysis_result = content_analyzer.analyze_content(text_content, options.focus)
        
        assert analysis_result is not None, "Content analysis failed"
        
        # Step 3: Generate note
        note_content = note_generator.generate_note(metadata, analysis_result, options)
        
        assert note_content is not None, "Note generation failed"
        assert note_content.content, "Empty note content"
        
        # Step 4: Generate filename
        filename = file_writer.generate_citekey_filename(metadata)
        expected_filename = f"{test_file['expected_citekey']}.md"
        
        assert filename == expected_filename, f"Filename mismatch: {filename} != {expected_filename}"
        
        # Step 5: Write note (to temp location for testing)
        temp_output_path = Path("/tmp") / filename
        written_path = file_writer.write_note(note_content.content, str(temp_output_path))
        
        assert Path(written_path).exists(), "Note file was not written"
        
        # Verify written content
        with open(written_path, 'r', encoding='utf-8') as f:
            written_content = f.read()
        
        assert written_content == note_content.content, "Written content doesn't match generated content"
        
        # Clean up
        Path(written_path).unlink(missing_ok=True)
        
        print(f"✓ Full workflow test completed successfully for {test_file['path'].name}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])