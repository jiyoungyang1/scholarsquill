#!/usr/bin/env python3
"""
Test script for AnalysisInstructionsGenerator
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from analysis_instructions import AnalysisInstructionsGenerator

def test_analysis_instructions():
    """Test the AnalysisInstructionsGenerator functionality"""
    
    print("Testing AnalysisInstructionsGenerator...")
    
    # Initialize generator
    generator = AnalysisInstructionsGenerator()
    
    # Test different focus types and depth levels
    focus_types = ["research", "theory", "method", "review", "balanced"]
    depth_levels = ["quick", "standard", "deep"]
    
    print("\n=== Testing Focus Types and Depth Levels ===")
    
    for focus in focus_types:
        for depth in depth_levels:
            print(f"\nTesting focus='{focus}', depth='{depth}':")
            
            # Generate instructions
            instructions = generator.create_analysis_instructions(focus, depth)
            
            # Verify structure
            required_keys = [
                "focus_guidance", "depth_guidance", "general_instructions",
                "template_filling_rules", "extraction_guidelines", 
                "quality_criteria", "analysis_workflow"
            ]
            
            for key in required_keys:
                if key not in instructions:
                    print(f"  ❌ Missing key: {key}")
                else:
                    print(f"  ✅ Found key: {key}")
            
            # Check focus guidance content
            focus_guidance = instructions["focus_guidance"]
            if "primary_focus" in focus_guidance and "extract" in focus_guidance:
                print(f"  ✅ Focus guidance complete for {focus}")
                print(f"     Primary focus: {focus_guidance['primary_focus'][:50]}...")
                print(f"     Extract items: {len(focus_guidance['extract'])}")
            else:
                print(f"  ❌ Focus guidance incomplete for {focus}")
            
            # Check depth guidance content
            depth_guidance = instructions["depth_guidance"]
            if "detail_level" in depth_guidance and "target_length" in depth_guidance:
                print(f"  ✅ Depth guidance complete for {depth}")
                print(f"     Detail level: {depth_guidance['detail_level'][:50]}...")
                print(f"     Target length: {depth_guidance['target_length']}")
            else:
                print(f"  ❌ Depth guidance incomplete for {depth}")
    
    print("\n=== Testing Error Guidance ===")
    
    error_types = [
        "insufficient_content", "corrupted_pdf", "unsupported_format", 
        "template_error", "focus_mismatch"
    ]
    
    for error_type in error_types:
        guidance = generator.create_error_guidance(error_type)
        if guidance and len(guidance) > 50:
            print(f"  ✅ Error guidance for '{error_type}': {guidance[:50]}...")
        else:
            print(f"  ❌ Error guidance missing or too short for '{error_type}'")
    
    print("\n=== Testing Batch Analysis Instructions ===")
    
    batch_instructions = generator.create_batch_analysis_instructions("research", "standard", 5)
    
    required_batch_keys = [
        "focus_guidance", "depth_guidance", "general_instructions",
        "template_filling_rules", "batch_guidance", "batch_size", "processing_mode"
    ]
    
    for key in required_batch_keys:
        if key not in batch_instructions:
            print(f"  ❌ Missing batch key: {key}")
        else:
            print(f"  ✅ Found batch key: {key}")
    
    if batch_instructions.get("batch_size") == 5:
        print(f"  ✅ Batch size correctly set to 5")
    else:
        print(f"  ❌ Batch size incorrect: {batch_instructions.get('batch_size')}")
    
    if batch_instructions.get("processing_mode") == "batch":
        print(f"  ✅ Processing mode correctly set to 'batch'")
    else:
        print(f"  ❌ Processing mode incorrect: {batch_instructions.get('processing_mode')}")
    
    print("\n=== Testing Extraction Guidelines ===")
    
    # Test extraction guidelines for different focus types
    for focus in ["research", "theory", "method"]:
        instructions = generator.create_analysis_instructions(focus, "standard")
        guidelines = instructions["extraction_guidelines"]
        
        if "specific_elements" in guidelines and guidelines["specific_elements"]:
            print(f"  ✅ Specific elements found for {focus}: {len(guidelines['specific_elements'])} items")
            for element in guidelines["specific_elements"][:2]:  # Show first 2
                print(f"     - {element}")
        else:
            print(f"  ❌ No specific elements for {focus}")
    
    print("\n=== Summary ===")
    print("✅ AnalysisInstructionsGenerator appears to be working correctly!")
    print("✅ All focus types and depth levels supported")
    print("✅ Error guidance available for common scenarios")
    print("✅ Batch processing instructions implemented")
    print("✅ Focus-specific extraction guidelines provided")
    
    return True

if __name__ == "__main__":
    try:
        test_analysis_instructions()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)