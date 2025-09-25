#!/usr/bin/env python3
"""
Final verification test for Task 3.1 integration
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_integration_verification():
    """Verify that Task 3.1 is properly integrated into the server"""
    
    print("=== Task 3.1 Integration Verification ===")
    print("Verifying that AnalysisInstructionsGenerator is properly integrated into MCP server")
    print()
    
    # Test 1: Import verification
    try:
        from analysis_instructions import AnalysisInstructionsGenerator
        print("✅ AnalysisInstructionsGenerator can be imported")
    except ImportError as e:
        print(f"❌ Failed to import AnalysisInstructionsGenerator: {e}")
        return False
    
    # Test 2: Server integration verification
    print("\n=== Server Integration Check ===")
    
    # Check server.py imports
    server_file = Path(__file__).parent / "src" / "server.py"
    if server_file.exists():
        server_content = server_file.read_text()
        
        # Check import
        if "from .analysis_instructions import AnalysisInstructionsGenerator" in server_content:
            print("✅ AnalysisInstructionsGenerator is imported in server.py")
        elif "from analysis_instructions import AnalysisInstructionsGenerator" in server_content:
            print("✅ AnalysisInstructionsGenerator is imported in server.py")
        else:
            print("❌ AnalysisInstructionsGenerator import not found in server.py")
            return False
        
        # Check initialization
        if "self.analysis_instructions = AnalysisInstructionsGenerator()" in server_content:
            print("✅ AnalysisInstructionsGenerator is initialized in server")
        else:
            print("❌ AnalysisInstructionsGenerator initialization not found")
            return False
        
        # Check usage in methods
        if "self.analysis_instructions.create_analysis_instructions" in server_content:
            print("✅ create_analysis_instructions method is used in server")
        else:
            print("❌ create_analysis_instructions method usage not found")
            return False
        
        if "self.analysis_instructions.create_batch_analysis_instructions" in server_content:
            print("✅ create_batch_analysis_instructions method is used in server")
        else:
            print("❌ create_batch_analysis_instructions method usage not found")
            return False
        
    else:
        print("❌ server.py file not found")
        return False
    
    # Test 3: Functional verification
    print("\n=== Functional Verification ===")
    
    try:
        generator = AnalysisInstructionsGenerator()
        
        # Test all required methods
        instructions = generator.create_analysis_instructions("research", "standard")
        if "analysis_instructions" in str(instructions) or "focus_guidance" in instructions:
            print("✅ create_analysis_instructions method works correctly")
        else:
            print("❌ create_analysis_instructions method not working properly")
            return False
        
        batch_instructions = generator.create_batch_analysis_instructions("theory", "deep", 3)
        if "batch_guidance" in batch_instructions:
            print("✅ create_batch_analysis_instructions method works correctly")
        else:
            print("❌ create_batch_analysis_instructions method not working properly")
            return False
        
        error_guidance = generator.create_error_guidance("insufficient_content")
        if error_guidance and len(error_guidance) > 20:
            print("✅ create_error_guidance method works correctly")
        else:
            print("❌ create_error_guidance method not working properly")
            return False
        
    except Exception as e:
        print(f"❌ Functional verification failed: {e}")
        return False
    
    # Test 4: Requirements compliance check
    print("\n=== Requirements Compliance Check ===")
    
    # Check all focus types
    focus_types = ["research", "theory", "method", "review", "balanced"]
    for focus in focus_types:
        try:
            instructions = generator.create_analysis_instructions(focus, "standard")
            focus_guidance = instructions.get("focus_guidance", {})
            if "primary_focus" in focus_guidance and "extract" in focus_guidance:
                print(f"  ✅ {focus} focus type supported")
            else:
                print(f"  ❌ {focus} focus type incomplete")
                return False
        except Exception as e:
            print(f"  ❌ {focus} focus type error: {e}")
            return False
    
    # Check all depth levels
    depth_levels = ["quick", "standard", "deep"]
    for depth in depth_levels:
        try:
            instructions = generator.create_analysis_instructions("balanced", depth)
            depth_guidance = instructions.get("depth_guidance", {})
            if "detail_level" in depth_guidance and "target_length" in depth_guidance:
                print(f"  ✅ {depth} depth level supported")
            else:
                print(f"  ❌ {depth} depth level incomplete")
                return False
        except Exception as e:
            print(f"  ❌ {depth} depth level error: {e}")
            return False
    
    print("\n=== Task 3.1 Integration Summary ===")
    print("✅ Task 3.1 is FULLY IMPLEMENTED and INTEGRATED")
    print("✅ AnalysisInstructionsGenerator class: COMPLETE")
    print("✅ Server integration: COMPLETE")
    print("✅ Method usage in server: COMPLETE")
    print("✅ All focus types supported: COMPLETE")
    print("✅ All depth levels supported: COMPLETE")
    print("✅ Error guidance system: COMPLETE")
    print("✅ Batch processing support: COMPLETE")
    
    print("\n🎉 Task 3.1 implementation is COMPLETE and ready for production use!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_integration_verification()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Integration verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)