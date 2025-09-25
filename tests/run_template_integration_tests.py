"""
Test runner for comprehensive template integration testing
Executes all template integration tests and provides detailed reporting
"""

import pytest
import sys
import os
from pathlib import Path
import subprocess
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_test_suite():
    """Run the complete template integration test suite"""
    
    print("=" * 80)
    print("SCHOLARSQUILL KIRO - TEMPLATE INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test configuration
    test_files = [
        "test_template_integration_unit.py",
        "test_template_integration_workflow.py", 
        "test_template_integration_e2e.py"
    ]
    
    test_results = {}
    overall_success = True
    
    for test_file in test_files:
        print(f"Running {test_file}...")
        print("-" * 60)
        
        # Run pytest with detailed output
        cmd = [
            sys.executable, "-m", "pytest", 
            test_file,
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--durations=10",  # Show 10 slowest tests
            "--junit-xml=junit_results.xml",  # Generate JUnit XML
            "--cov=src",  # Coverage for src directory
            "--cov-report=term-missing"  # Show missing lines
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=Path(__file__).parent,
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout per test file
            )
            
            test_results[test_file] = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            if result.returncode == 0:
                print(f"✅ {test_file} PASSED")
            else:
                print(f"❌ {test_file} FAILED")
                overall_success = False
                print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                print("STDERR:", result.stderr[-500:])
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} TIMED OUT")
            test_results[test_file] = {
                "returncode": -1,
                "stdout": "",
                "stderr": "Test timed out after 5 minutes",
                "success": False
            }
            overall_success = False
        
        except Exception as e:
            print(f"💥 {test_file} ERROR: {e}")
            test_results[test_file] = {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
            overall_success = False
        
        print()
    
    # Generate summary report
    print("=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(1 for result in test_results.values() if result["success"])
    total_tests = len(test_results)
    
    print(f"Overall Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    print(f"Test Files: {passed_tests}/{total_tests} passed")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detailed results
    print("\nDetailed Results:")
    for test_file, result in test_results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"  {test_file}: {status}")
        if not result["success"]:
            print(f"    Error: {result['stderr'][:100]}...")
    
    # Save detailed results to file
    results_file = Path(__file__).parent / "template_integration_test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "overall_success": overall_success,
            "total_files": total_tests,
            "passed_files": passed_tests,
            "results": test_results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return overall_success


def validate_test_coverage():
    """Validate that tests cover all required functionality"""
    
    print("\n" + "=" * 80)
    print("TEMPLATE INTEGRATION TEST COVERAGE VALIDATION")
    print("=" * 80)
    
    required_test_areas = {
        "Content Extraction Methods": [
            "_extract_research_question",
            "_extract_methodology", 
            "_extract_key_findings",
            "_extract_theory_specific_data",
            "_extract_research_specific_data",
            "_extract_method_specific_data",
            "_extract_review_specific_data"
        ],
        "Text Processing Utilities": [
            "_clean_extracted_text",
            "_summarize_text",
            "_extract_findings_from_text",
            "_extract_research_questions_by_pattern",
            "_extract_objectives_by_pattern",
            "_segment_text_by_content_type",
            "_extract_numerical_results"
        ],
        "Template Workflow": [
            "complete_workflow_research_focus",
            "complete_workflow_theory_focus", 
            "template_selection_logic",
            "depth_filtering",
            "error_handling_template_not_found",
            "error_handling_template_rendering_failure",
            "fallback_mechanism"
        ],
        "End-to-End Integration": [
            "complete_pipeline_research_paper",
            "template_output_quality_validation",
            "theory_paper_specialized_content",
            "review_paper_synthesis_content",
            "error_resilience_with_poor_content"
        ]
    }
    
    # Check test files exist
    test_files = [
        "test_template_integration_unit.py",
        "test_template_integration_workflow.py",
        "test_template_integration_e2e.py"
    ]
    
    coverage_report = {}
    overall_coverage = True
    
    for area, required_tests in required_test_areas.items():
        print(f"\n{area}:")
        area_coverage = True
        covered_tests = []
        missing_tests = []
        
        for test_name in required_tests:
            found = False
            for test_file in test_files:
                test_path = Path(__file__).parent / test_file
                if test_path.exists():
                    content = test_path.read_text()
                    if test_name in content:
                        found = True
                        covered_tests.append(test_name)
                        break
            
            if not found:
                missing_tests.append(test_name)
                area_coverage = False
                overall_coverage = False
        
        coverage_report[area] = {
            "covered": covered_tests,
            "missing": missing_tests,
            "coverage_percent": len(covered_tests) / len(required_tests) * 100
        }
        
        print(f"  Coverage: {len(covered_tests)}/{len(required_tests)} ({coverage_report[area]['coverage_percent']:.1f}%)")
        
        if missing_tests:
            print(f"  Missing tests: {', '.join(missing_tests)}")
        else:
            print("  ✅ All required tests present")
    
    print(f"\nOverall Coverage: {'✅ COMPLETE' if overall_coverage else '⚠️ INCOMPLETE'}")
    
    return overall_coverage, coverage_report


def generate_test_documentation():
    """Generate documentation for the test suite"""
    
    doc_content = """# Template Integration Test Suite Documentation

## Overview
This test suite provides comprehensive testing for the ScholarSquill Kiro template integration system.
It validates the fix for the MCP template bypass issue and ensures proper Jinja2 template usage.

## Test Structure

### 1. Unit Tests (`test_template_integration_unit.py`)
Tests individual content extraction methods with various input formats:

- **Research Question Extraction**: Tests pattern matching for research questions in abstracts and introductions
- **Methodology Extraction**: Validates methodology extraction from different section structures  
- **Key Findings Extraction**: Tests findings extraction from results, discussion, and conclusion sections
- **Focus-Specific Data Extraction**: Tests theory, research, method, and review-specific data extraction
- **Text Processing Utilities**: Tests enhanced text cleaning, summarization, and pattern matching

### 2. Workflow Integration Tests (`test_template_integration_workflow.py`)
Tests complete template workflow from content to rendered output:

- **Complete Workflow**: End-to-end template generation for all focus types
- **Template Selection Logic**: Tests template selection based on focus type and paper classification
- **Depth Filtering**: Validates content filtering based on quick/standard/deep depth settings
- **Error Handling**: Tests error handling for missing templates and rendering failures
- **Fallback Mechanisms**: Tests fallback behavior when template processing fails

### 3. End-to-End Tests (`test_template_integration_e2e.py`)
Tests with realistic content and complete pipeline:

- **Real Content Processing**: Tests with sample research, theory, and review paper content
- **Output Quality Validation**: Validates template output meets quality standards
- **Performance Testing**: Tests performance with large content documents
- **Error Resilience**: Tests system behavior with poor quality or minimal content

## Running Tests

### Individual Test Files
```bash
pytest test_template_integration_unit.py -v
pytest test_template_integration_workflow.py -v  
pytest test_template_integration_e2e.py -v
```

### Complete Test Suite
```bash
python run_template_integration_tests.py
```

### With Coverage Report
```bash
pytest --cov=src --cov-report=html
```

## Test Requirements Coverage

The test suite covers all requirements from Task 8:

- ✅ **8.1**: Unit tests for content extraction methods
  - Research question extraction with various formats
  - Methodology extraction from different section structures
  - Key findings extraction from multiple sections
  - All focus-specific data extraction methods

- ✅ **8.2**: Integration tests for template workflow  
  - Complete workflow from PDF content to rendered output
  - Template selection logic for different focus types
  - Error handling and fallback mechanisms
  - Template output quality validation

## Quality Standards

### Test Coverage Targets
- **Function Coverage**: >90% of template-related functions
- **Branch Coverage**: >85% of conditional logic paths
- **Integration Coverage**: All focus types and depth levels tested

### Quality Validation
- Template variables properly populated (no undefined values)
- Proper markdown formatting maintained
- Content relevance and accuracy preserved
- Performance within acceptable limits (<30s for large documents)

## Continuous Integration

The test suite is designed for CI/CD integration:
- JUnit XML output for CI systems
- Coverage reports for quality tracking
- Timeout handling for reliability
- Detailed error reporting for debugging

## Troubleshooting

### Common Issues
1. **Template Not Found**: Ensure templates directory exists and contains required templates
2. **Import Errors**: Verify src directory is in Python path
3. **Timeout Errors**: Large content may require timeout adjustment
4. **Mock Failures**: Check that mock objects match actual interface signatures

### Performance Optimization
- Use realistic but smaller test content for unit tests
- Implement test data caching for repeated runs
- Parallel test execution where possible
- Resource cleanup in test fixtures
"""
    
    doc_file = Path(__file__).parent / "TEST_DOCUMENTATION.md"
    doc_file.write_text(doc_content)
    print(f"Test documentation generated: {doc_file}")


if __name__ == "__main__":
    print("Starting Template Integration Test Suite...")
    
    # Run coverage validation first
    coverage_ok, coverage_report = validate_test_coverage()
    
    if not coverage_ok:
        print("\n⚠️ Warning: Test coverage is incomplete")
        print("Proceeding with available tests...")
    
    # Run the test suite
    success = run_test_suite()
    
    # Generate documentation
    generate_test_documentation()
    
    # Exit with appropriate code
    exit_code = 0 if success else 1
    print(f"\nExiting with code: {exit_code}")
    sys.exit(exit_code)