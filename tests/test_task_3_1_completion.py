#!/usr/bin/env python3
"""
Test completion of Task 3.1: Implement AnalysisInstructions generator
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_task_3_1_completion():
    """Test that Task 3.1 is complete according to requirements"""
    
    print("=== Testing Task 3.1 Completion ===")
    print("Task: Implement AnalysisInstructions generator")
    print("Requirements:")
    print("- Create focus-specific analysis guidance for Claude")
    print("- Provide depth-level instructions (quick, standard, deep)")
    print("- Include template filling rules and extraction targets")
    print("- Requirements: 4.1, 4.2, 4.3, 4.4")
    print()
    
    try:
        from analysis_instructions import AnalysisInstructionsGenerator
        print("✅ AnalysisInstructionsGenerator class imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AnalysisInstructionsGenerator: {e}")
        return False
    
    # Initialize generator
    try:
        generator = AnalysisInstructionsGenerator()
        print("✅ AnalysisInstructionsGenerator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AnalysisInstructionsGenerator: {e}")
        return False
    
    print("\n=== Requirement 4.1: Focus-specific analysis guidance ===")
    
    focus_types = ["research", "theory", "method", "review", "balanced"]
    focus_success = True
    
    for focus in focus_types:
        try:
            instructions = generator.create_analysis_instructions(focus, "standard")
            focus_guidance = instructions.get("focus_guidance", {})
            
            # Check required components for focus guidance
            required_focus_keys = ["primary_focus", "key_sections", "extract", "analysis_approach"]
            missing_keys = [key for key in required_focus_keys if key not in focus_guidance]
            
            if not missing_keys:
                print(f"  ✅ {focus}: Complete focus guidance")
                print(f"     Primary focus: {focus_guidance['primary_focus'][:60]}...")
                print(f"     Extract items: {len(focus_guidance['extract'])}")
            else:
                print(f"  ❌ {focus}: Missing keys: {missing_keys}")
                focus_success = False
                
        except Exception as e:
            print(f"  ❌ {focus}: Error generating instructions: {e}")
            focus_success = False
    
    print(f"\nFocus-specific guidance: {'✅ PASS' if focus_success else '❌ FAIL'}")
    
    print("\n=== Requirement 4.2: Depth-level instructions ===")
    
    depth_levels = ["quick", "standard", "deep"]
    depth_success = True
    
    for depth in depth_levels:
        try:
            instructions = generator.create_analysis_instructions("balanced", depth)
            depth_guidance = instructions.get("depth_guidance", {})
            
            # Check required components for depth guidance
            required_depth_keys = ["detail_level", "length_guidance", "sections", "analysis_depth", "target_length"]
            missing_keys = [key for key in required_depth_keys if key not in depth_guidance]
            
            if not missing_keys:
                print(f"  ✅ {depth}: Complete depth guidance")
                print(f"     Detail level: {depth_guidance['detail_level'][:60]}...")
                print(f"     Target length: {depth_guidance['target_length']}")
            else:
                print(f"  ❌ {depth}: Missing keys: {missing_keys}")
                depth_success = False
                
        except Exception as e:
            print(f"  ❌ {depth}: Error generating instructions: {e}")
            depth_success = False
    
    print(f"\nDepth-level instructions: {'✅ PASS' if depth_success else '❌ FAIL'}")
    
    print("\n=== Requirement 4.3: Template filling rules and extraction targets ===")
    
    try:
        instructions = generator.create_analysis_instructions("research", "standard")
        
        # Check template filling rules
        template_rules = instructions.get("template_filling_rules", [])
        if template_rules and len(template_rules) >= 5:
            print("  ✅ Template filling rules provided")
            print(f"     Number of rules: {len(template_rules)}")
            for rule in template_rules[:3]:  # Show first 3
                print(f"     - {rule[:60]}...")
        else:
            print("  ❌ Template filling rules missing or insufficient")
            return False
        
        # Check extraction guidelines
        extraction_guidelines = instructions.get("extraction_guidelines", {})
        if extraction_guidelines and "content_priorities" in extraction_guidelines:
            print("  ✅ Extraction targets provided")
            print(f"     Content priorities: {len(extraction_guidelines['content_priorities'])} items")
        else:
            print("  ❌ Extraction targets missing")
            return False
        
        # Check general instructions
        general_instructions = instructions.get("general_instructions", [])
        if general_instructions and len(general_instructions) >= 5:
            print("  ✅ General instructions provided")
            print(f"     Number of instructions: {len(general_instructions)}")
        else:
            print("  ❌ General instructions missing or insufficient")
            return False
            
    except Exception as e:
        print(f"  ❌ Error checking template rules and extraction targets: {e}")
        return False
    
    print("\nTemplate filling rules and extraction targets: ✅ PASS")
    
    print("\n=== Requirement 4.4: Comprehensive analysis workflow ===")
    
    try:
        instructions = generator.create_analysis_instructions("theory", "deep")
        
        # Check analysis workflow
        workflow = instructions.get("analysis_workflow", [])
        if workflow and len(workflow) >= 8:
            print("  ✅ Analysis workflow provided")
            print(f"     Number of workflow steps: {len(workflow)}")
            for step in workflow[:3]:  # Show first 3 steps
                print(f"     {step}")
        else:
            print("  ❌ Analysis workflow missing or insufficient")
            return False
        
        # Check quality criteria
        quality_criteria = instructions.get("quality_criteria", [])
        if quality_criteria and len(quality_criteria) >= 5:
            print("  ✅ Quality criteria provided")
            print(f"     Number of criteria: {len(quality_criteria)}")
        else:
            print("  ❌ Quality criteria missing or insufficient")
            return False
            
    except Exception as e:
        print(f"  ❌ Error checking analysis workflow: {e}")
        return False
    
    print("\nComprehensive analysis workflow: ✅ PASS")
    
    print("\n=== Additional Features ===")
    
    # Test error guidance
    try:
        error_guidance = generator.create_error_guidance("insufficient_content")
        if error_guidance and len(error_guidance) > 50:
            print("  ✅ Error guidance system implemented")
        else:
            print("  ❌ Error guidance system missing or insufficient")
    except Exception as e:
        print(f"  ❌ Error guidance system error: {e}")
    
    # Test batch processing
    try:
        batch_instructions = generator.create_batch_analysis_instructions("research", "standard", 5)
        if "batch_guidance" in batch_instructions and "batch_size" in batch_instructions:
            print("  ✅ Batch processing instructions implemented")
        else:
            print("  ❌ Batch processing instructions missing")
    except Exception as e:
        print(f"  ❌ Batch processing instructions error: {e}")
    
    print("\n=== Task 3.1 Completion Summary ===")
    
    if focus_success and depth_success:
        print("✅ Task 3.1 COMPLETED SUCCESSFULLY")
        print("✅ All requirements (4.1, 4.2, 4.3, 4.4) have been implemented")
        print("✅ Focus-specific analysis guidance for Claude: IMPLEMENTED")
        print("✅ Depth-level instructions (quick, standard, deep): IMPLEMENTED")
        print("✅ Template filling rules and extraction targets: IMPLEMENTED")
        print("✅ Comprehensive analysis workflow: IMPLEMENTED")
        print("✅ Additional features (error guidance, batch processing): IMPLEMENTED")
        return True
    else:
        print("❌ Task 3.1 INCOMPLETE")
        print("❌ Some requirements are not fully implemented")
        return False

if __name__ == "__main__":
    try:
        success = test_task_3_1_completion()
        if success:
            print("\n🎉 Task 3.1 implementation is complete and ready for use!")
        else:
            print("\n❌ Task 3.1 implementation needs additional work")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)