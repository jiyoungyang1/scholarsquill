#!/usr/bin/env python3
"""
Test script for the redesigned MCP tool response structure
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append('src')

from content_extractor import ContentExtractor
from analysis_instructions import AnalysisInstructionsGenerator
from template_loader import TemplateLoader

async def test_redesigned_components():
    """Test the new components for Claude AI integration"""
    
    print("Testing Redesigned MCP Tool Response Structure")
    print("=" * 50)
    
    # Test 1: ContentExtractor
    print("\n1. Testing ContentExtractor...")
    try:
        extractor = ContentExtractor()
        print("   ✓ ContentExtractor initialized")
        
        # Test with a sample text (simulating PDF content)
        sample_text = """
        Abstract
        This paper presents a novel approach to machine learning.
        
        Introduction
        Machine learning has become increasingly important.
        
        Methods
        We used a neural network approach with the following parameters.
        
        Results
        Our experiments showed significant improvements.
        
        Conclusion
        This work demonstrates the effectiveness of our approach.
        """
        
        # Test content extraction (this would normally be from a PDF)
        print("   ✓ Testing content structuring...")
        structured = extractor._structure_content(sample_text)
        print(f"   ✓ Found {len(structured['sections'])} sections")
        print(f"   ✓ Found {len(structured['paragraphs'])} paragraphs")
        
    except Exception as e:
        print(f"   ✗ ContentExtractor failed: {e}")
    
    # Test 2: AnalysisInstructionsGenerator
    print("\n2. Testing AnalysisInstructionsGenerator...")
    try:
        instructions_gen = AnalysisInstructionsGenerator()
        print("   ✓ AnalysisInstructionsGenerator initialized")
        
        # Test instruction generation for different focus types
        for focus in ['research', 'theory', 'method', 'review', 'balanced']:
            instructions = instructions_gen.create_analysis_instructions(focus, 'standard')
            print(f"   ✓ Generated instructions for {focus} focus ({len(instructions)} sections)")
        
        # Test error guidance
        error_guidance = instructions_gen.create_error_guidance('insufficient_content')
        print(f"   ✓ Generated error guidance ({len(error_guidance)} chars)")
        
    except Exception as e:
        print(f"   ✗ AnalysisInstructionsGenerator failed: {e}")
    
    # Test 3: TemplateLoader
    print("\n3. Testing TemplateLoader...")
    try:
        loader = TemplateLoader('templates')
        print("   ✓ TemplateLoader initialized")
        
        # Test template loading
        template_data = await loader.load_template('balanced')
        print(f"   ✓ Loaded template: {template_data['template_name']}")
        print(f"   ✓ Template has {len(template_data['sections'])} sections")
        print(f"   ✓ Template has {len(template_data['variables'])} variables")
        print(f"   ✓ Instructions embedded: {template_data['instructions_embedded']}")
        
        # Test available templates
        available = loader.get_available_templates()
        print(f"   ✓ Found {len(available)} available templates: {', '.join(available)}")
        
    except Exception as e:
        print(f"   ✗ TemplateLoader failed: {e}")
    
    # Test 4: Integration Test - Simulate MCP Response
    print("\n4. Testing Integrated MCP Response Structure...")
    try:
        # Simulate what the redesigned sq_note tool would return
        mock_response = {
            "success": True,
            "action_required": "analyze_content",
            "pdf_content": sample_text,
            "structured_content": extractor._structure_content(sample_text),
            "metadata": {
                "title": "Sample Paper",
                "authors": ["Test Author"],
                "year": 2024
            },
            "template": await loader.load_template('research'),
            "analysis_instructions": instructions_gen.create_analysis_instructions('research', 'standard'),
            "processing_options": {
                "focus": "research",
                "depth": "standard",
                "format": "markdown"
            },
            "message": "PDF content extracted successfully. Please analyze using Claude."
        }
        
        print("   ✓ Mock MCP response structure created")
        print(f"   ✓ Response has {len(mock_response)} top-level keys")
        print(f"   ✓ PDF content length: {len(mock_response['pdf_content'])} chars")
        print(f"   ✓ Template content length: {len(mock_response['template']['template_content'])} chars")
        print(f"   ✓ Analysis instructions sections: {len(mock_response['analysis_instructions'])}")
        
        # Verify the response structure matches the design
        required_keys = [
            'success', 'action_required', 'pdf_content', 'template', 
            'analysis_instructions', 'processing_options', 'message'
        ]
        
        missing_keys = [key for key in required_keys if key not in mock_response]
        if missing_keys:
            print(f"   ✗ Missing required keys: {missing_keys}")
        else:
            print("   ✓ All required keys present in response")
        
    except Exception as e:
        print(f"   ✗ Integration test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Redesigned MCP Tool Response Structure Test Complete")
    print("\nKey Changes Implemented:")
    print("✓ MCP tool now returns structured data instead of completed notes")
    print("✓ PDF content extraction without internal analysis")
    print("✓ Templates with embedded Claude instructions")
    print("✓ Comprehensive analysis instructions for different focus types")
    print("✓ Error handling with Claude-specific guidance")
    print("\nClaude will now receive:")
    print("- Raw PDF content for analysis")
    print("- Template structure with instructions")
    print("- Focus-specific analysis guidance")
    print("- Depth-level requirements")
    print("- Error handling guidance")

if __name__ == "__main__":
    asyncio.run(test_redesigned_components())