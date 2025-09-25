#!/usr/bin/env python3
"""
Test MCP integration with AnalysisInstructionsGenerator
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from server import ScholarsQuillKiroServer
from config import ServerConfig

async def test_mcp_integration():
    """Test MCP server integration with AnalysisInstructionsGenerator"""
    
    print("Testing MCP Server Integration with AnalysisInstructionsGenerator...")
    
    # Initialize server
    config = ServerConfig()
    server = ScholarsQuillKiroServer(config)
    
    print("✅ Server initialized successfully")
    
    # Test that analysis_instructions is properly initialized
    if hasattr(server, 'analysis_instructions'):
        print("✅ AnalysisInstructionsGenerator is properly initialized")
    else:
        print("❌ AnalysisInstructionsGenerator not found in server")
        return False
    
    # Test analysis instructions generation
    print("\n=== Testing Analysis Instructions Generation ===")
    
    try:
        instructions = server.analysis_instructions.create_analysis_instructions("research", "standard")
        
        required_keys = [
            "focus_guidance", "depth_guidance", "general_instructions",
            "template_filling_rules", "extraction_guidelines", 
            "quality_criteria", "analysis_workflow"
        ]
        
        for key in required_keys:
            if key in instructions:
                print(f"  ✅ {key}: Available")
            else:
                print(f"  ❌ {key}: Missing")
                return False
        
        print("✅ Analysis instructions generation working correctly")
        
    except Exception as e:
        print(f"❌ Error generating analysis instructions: {str(e)}")
        return False
    
    # Test error guidance
    print("\n=== Testing Error Guidance ===")
    
    try:
        error_guidance = server.analysis_instructions.create_error_guidance("insufficient_content")
        if error_guidance and len(error_guidance) > 50:
            print("✅ Error guidance generation working correctly")
        else:
            print("❌ Error guidance too short or missing")
            return False
            
    except Exception as e:
        print(f"❌ Error generating error guidance: {str(e)}")
        return False
    
    # Test batch instructions
    print("\n=== Testing Batch Instructions ===")
    
    try:
        batch_instructions = server.analysis_instructions.create_batch_analysis_instructions("theory", "deep", 3)
        
        if "batch_guidance" in batch_instructions and "batch_size" in batch_instructions:
            print("✅ Batch instructions generation working correctly")
            print(f"  Batch size: {batch_instructions['batch_size']}")
            print(f"  Processing mode: {batch_instructions.get('processing_mode', 'unknown')}")
        else:
            print("❌ Batch instructions missing required keys")
            return False
            
    except Exception as e:
        print(f"❌ Error generating batch instructions: {str(e)}")
        return False
    
    # Test server method that uses analysis instructions
    print("\n=== Testing Server Methods Using Analysis Instructions ===")
    
    # Test the _create_error_response method
    try:
        error_response = server._create_error_response(
            ValueError("Test error"), 
            "test_context", 
            "test_target"
        )
        
        if "claude_guidance" in error_response:
            print("✅ Error response includes Claude guidance")
        else:
            print("❌ Error response missing Claude guidance")
            return False
            
    except Exception as e:
        print(f"❌ Error testing error response: {str(e)}")
        return False
    
    print("\n=== Integration Test Summary ===")
    print("✅ AnalysisInstructionsGenerator properly integrated into MCP server")
    print("✅ All analysis instruction methods working correctly")
    print("✅ Error guidance properly integrated")
    print("✅ Batch processing instructions available")
    print("✅ Server methods using analysis instructions working")
    
    return True

async def test_focus_depth_combinations():
    """Test all focus and depth combinations"""
    
    print("\n=== Testing All Focus/Depth Combinations ===")
    
    config = ServerConfig()
    server = ScholarsQuillKiroServer(config)
    
    focus_types = ["research", "theory", "method", "review", "balanced"]
    depth_levels = ["quick", "standard", "deep"]
    
    success_count = 0
    total_count = len(focus_types) * len(depth_levels)
    
    for focus in focus_types:
        for depth in depth_levels:
            try:
                instructions = server.analysis_instructions.create_analysis_instructions(focus, depth)
                
                # Verify essential components
                if (instructions.get("focus_guidance") and 
                    instructions.get("depth_guidance") and 
                    instructions.get("general_instructions")):
                    success_count += 1
                    print(f"  ✅ {focus}/{depth}")
                else:
                    print(f"  ❌ {focus}/{depth} - Missing components")
                    
            except Exception as e:
                print(f"  ❌ {focus}/{depth} - Error: {str(e)}")
    
    print(f"\nCombination Test Results: {success_count}/{total_count} successful")
    
    if success_count == total_count:
        print("✅ All focus/depth combinations working correctly")
        return True
    else:
        print("❌ Some focus/depth combinations failed")
        return False

if __name__ == "__main__":
    async def run_tests():
        try:
            # Test basic integration
            integration_success = await test_mcp_integration()
            
            # Test all combinations
            combinations_success = await test_focus_depth_combinations()
            
            if integration_success and combinations_success:
                print("\n🎉 All MCP integration tests passed!")
                print("✅ Task 3.1 - AnalysisInstructionsGenerator implementation is complete and working!")
                return True
            else:
                print("\n❌ Some tests failed")
                return False
                
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)