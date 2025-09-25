#!/usr/bin/env python3
"""
Test the redesigned sq_note tool functionality
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append('src')

from content_extractor import ContentExtractor
from analysis_instructions import AnalysisInstructionsGenerator
from template_loader import TemplateLoader

class MockPDFProcessor:
    """Mock PDF processor for testing"""
    
    def extract_text(self, pdf_path: str) -> str:
        return """
        Abstract
        This paper presents a comprehensive study on machine learning applications in healthcare.
        We developed a novel neural network architecture that achieves state-of-the-art performance.
        
        1. Introduction
        Healthcare applications of machine learning have gained significant attention in recent years.
        The ability to analyze large datasets and identify patterns has revolutionized medical diagnosis.
        
        2. Methods
        We employed a deep learning approach using convolutional neural networks.
        The dataset consisted of 10,000 medical images from various sources.
        Data preprocessing included normalization and augmentation techniques.
        
        3. Results
        Our model achieved 95.2% accuracy on the test set, outperforming existing methods.
        The precision was 94.8% and recall was 96.1%.
        Statistical significance was confirmed using t-tests (p < 0.001).
        
        4. Discussion
        The results demonstrate the effectiveness of our approach.
        The high accuracy suggests potential for clinical deployment.
        However, further validation on diverse populations is needed.
        
        5. Conclusion
        We presented a novel machine learning approach for healthcare applications.
        Future work will focus on expanding the dataset and improving interpretability.
        
        References
        [1] Smith, J. et al. (2023). Machine Learning in Healthcare. Nature Medicine.
        [2] Johnson, A. (2022). Deep Learning Applications. JAMA.
        """
    
    def extract_metadata(self, pdf_path: str):
        class MockMetadata:
            def __init__(self):
                self.title = "Machine Learning Applications in Healthcare: A Comprehensive Study"
                self.first_author = "Smith"
                self.authors = ["Smith, J.", "Johnson, A.", "Brown, K."]
                self.year = 2024
                self.journal = "Journal of Medical AI"
                self.doi = "10.1000/example.doi"
                self.citekey = "smith2024machine"
                self.page_count = 12
                self.abstract = "This paper presents a comprehensive study on machine learning applications..."
                self.keywords = ["machine learning", "healthcare", "neural networks"]
            
            def to_dict(self):
                return {
                    "title": self.title,
                    "first_author": self.first_author,
                    "authors": self.authors,
                    "year": self.year,
                    "journal": self.journal,
                    "doi": self.doi,
                    "citekey": self.citekey,
                    "page_count": self.page_count,
                    "abstract": self.abstract,
                    "keywords": self.keywords
                }
        
        return MockMetadata()

async def simulate_redesigned_sq_note(
    target: str,
    focus: str = "balanced",
    depth: str = "standard"
):
    """
    Simulate the redesigned sq_note tool that returns structured data for Claude
    """
    
    print(f"Simulating redesigned sq_note tool call:")
    print(f"  Target: {target}")
    print(f"  Focus: {focus}")
    print(f"  Depth: {depth}")
    print()
    
    try:
        # Step 1: Initialize components (like the server would)
        content_extractor = ContentExtractor()
        analysis_instructions = AnalysisInstructionsGenerator()
        template_loader = TemplateLoader('templates')
        pdf_processor = MockPDFProcessor()
        
        # Step 2: Validate file (simplified for test)
        file_path = Path(target)
        print(f"✓ File validation: {target}")
        
        # Step 3: Extract PDF content and metadata
        print("✓ Extracting PDF content...")
        raw_content = pdf_processor.extract_text(str(file_path))
        metadata = pdf_processor.extract_metadata(str(file_path))
        
        # Step 4: Structure content for analysis
        print("✓ Structuring content for AI analysis...")
        structured_content = content_extractor._structure_content(raw_content)
        content_stats = content_extractor._calculate_content_stats(raw_content)
        
        # Step 5: Load appropriate template
        print(f"✓ Loading template for {focus} focus...")
        template_data = await template_loader.load_template(focus)
        
        # Step 6: Generate analysis instructions
        print(f"✓ Generating analysis instructions for {focus}/{depth}...")
        instructions = analysis_instructions.create_analysis_instructions(focus, depth)
        
        # Step 7: Generate suggested filename
        safe_title = "".join(c for c in metadata.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:50].replace(' ', '_')
        suggested_filename = f"{safe_title}_literature_note.md"
        
        # Step 8: Return structured data for Claude (NEW BEHAVIOR)
        response = {
            "success": True,
            "action_required": "analyze_content",
            "pdf_content": raw_content,
            "structured_content": structured_content,
            "metadata": metadata.to_dict(),
            "template": template_data,
            "analysis_instructions": instructions,
            "processing_options": {
                "focus": focus,
                "depth": depth,
                "format": "markdown"
            },
            "output_info": {
                "suggested_directory": "literature-notes",
                "suggested_filename": suggested_filename,
                "full_suggested_path": f"literature-notes/{suggested_filename}"
            },
            "file_info": {
                "source_path": str(file_path),
                "size_mb": 0.5,  # Mock size
                "content_stats": content_stats
            },
            "message": (
                f"PDF content extracted successfully from '{file_path.name}'. "
                f"Please analyze the content using the provided template and instructions, "
                f"focusing on {focus} aspects with {depth} depth. "
                f"Fill the template with actual content from the paper, not placeholder text."
            )
        }
        
        print("✓ Structured response created for Claude analysis")
        print()
        
        return response
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": f"Failed to extract content: {str(e)}"
        }

async def test_redesigned_sq_note():
    """Test the redesigned sq_note functionality"""
    
    print("Testing Redesigned sq_note Tool")
    print("=" * 40)
    print()
    
    # Test different focus types
    test_cases = [
        ("sample_paper.pdf", "research", "standard"),
        ("sample_paper.pdf", "theory", "deep"),
        ("sample_paper.pdf", "method", "quick"),
    ]
    
    for i, (target, focus, depth) in enumerate(test_cases, 1):
        print(f"Test Case {i}: {focus.upper()} focus with {depth.upper()} depth")
        print("-" * 50)
        
        response = await simulate_redesigned_sq_note(target, focus, depth)
        
        if response["success"]:
            print("✓ SUCCESS - Claude will receive:")
            print(f"  - PDF content: {len(response['pdf_content'])} characters")
            print(f"  - Structured sections: {len(response['structured_content']['sections'])}")
            print(f"  - Template: {response['template']['template_name']}")
            print(f"  - Instructions: {len(response['analysis_instructions'])} sections")
            print(f"  - Focus guidance: {response['analysis_instructions']['focus_guidance']['primary_focus']}")
            print(f"  - Depth guidance: {response['analysis_instructions']['depth_guidance']['detail_level']}")
            print(f"  - Suggested filename: {response['output_info']['suggested_filename']}")
            print(f"  - Action required: {response['action_required']}")
            
            # Show what Claude would see in the message
            print(f"\nClaude receives this message:")
            print(f"'{response['message']}'")
            
        else:
            print("✗ FAILED:")
            print(f"  Error: {response['error']}")
        
        print("\n" + "=" * 60 + "\n")
    
    print("Key Differences from Old Implementation:")
    print("OLD: sq_note returned completed literature notes with placeholder text")
    print("NEW: sq_note returns structured data for Claude to analyze")
    print()
    print("What Claude Now Receives:")
    print("✓ Raw PDF content for intelligent analysis")
    print("✓ Template with embedded analysis instructions")
    print("✓ Focus-specific extraction guidelines")
    print("✓ Depth-specific detail requirements")
    print("✓ Structured content with basic sections detected")
    print("✓ Comprehensive metadata for context")
    print("✓ Clear action instructions (analyze_content)")
    print("✓ Error guidance for edge cases")
    print()
    print("What Claude Will Do:")
    print("1. Read and understand the PDF content")
    print("2. Follow the focus-specific analysis instructions")
    print("3. Fill the template with actual content (not placeholders)")
    print("4. Generate meaningful literature notes")
    print("5. Save the notes to the suggested location")

if __name__ == "__main__":
    asyncio.run(test_redesigned_sq_note())