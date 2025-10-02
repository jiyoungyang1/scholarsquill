"""
Content extraction engine for scientific papers - provides basic structure detection for AI analysis
"""

import re
from typing import Dict, List, Tuple

try:
    from .interfaces import ContentAnalyzerInterface
    from .models import AnalysisResult, FocusType
except ImportError:
    from interfaces import ContentAnalyzerInterface
    from models import AnalysisResult, FocusType


class ContentAnalyzer(ContentAnalyzerInterface):
    """
    Basic content analyzer for backward compatibility
    
    This class provides minimal analysis functionality while delegating 
    intelligent analysis to Claude AI.
    """
    
    def __init__(self):
        """Initialize the content extractor for basic structure detection"""
        # Basic section patterns for structure detection only
        self._section_patterns = {
            'abstract': [r'\babstract\b', r'\bsummary\b'],
            'introduction': [r'\bintroduction\b', r'\bbackground\b'],
            'methods': [r'\bmethods?\b', r'\bmethodology\b'],
            'results': [r'\bresults?\b', r'\bfindings\b'],
            'discussion': [r'\bdiscussion\b'],
            'conclusion': [r'\bconclusions?\b'],
            'references': [r'\breferences?\b', r'\bbibliography\b']
        }

    def analyze_content(self, text: str, focus: str) -> AnalysisResult:
        """
        Extract basic content structure for AI analysis
        
        Args:
            text: Full text content of the paper
            focus: Focus type (unused in basic extraction)
            
        Returns:
            AnalysisResult with basic structure detection only
        """
        # Basic structure extraction only - no intelligent analysis
        sections = self.extract_sections(text)
        
        return AnalysisResult(
            paper_type='unknown',  # No classification - let Claude decide
            confidence=0.0,  # No confidence - not analyzing
            sections=sections,
            key_concepts=[],  # No concept extraction - let Claude analyze
            equations=[],  # No equation extraction - let Claude identify
            methodologies=[]  # No methodology extraction - let Claude analyze
        )

    def classify_paper_type(self, text: str) -> Tuple[str, float]:
        """
        No classification - delegate to AI analysis
        
        Args:
            text: Full text content of the paper
            
        Returns:
            Tuple of ('unknown', 0.0) - classification removed
        """
        # No intelligent classification - let Claude analyze the content
        return 'unknown', 0.0

    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Basic section detection for structure identification
        
        Args:
            text: Full text content of the paper
            
        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}
        lines = text.split('\n')
        
        # Simple section header detection
        section_positions = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            for section_name, patterns in self._section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line_lower):
                        section_positions.append((i, section_name, line.strip()))
                        break
        
        # Sort by position
        section_positions.sort(key=lambda x: x[0])
        
        # Extract content between sections
        for i, (pos, section_name, header) in enumerate(section_positions):
            start_line = pos + 1
            
            # Find end position (next section or end of text)
            if i + 1 < len(section_positions):
                end_line = section_positions[i + 1][0]
            else:
                end_line = len(lines)
            
            # Extract section content
            section_content = '\n'.join(lines[start_line:end_line]).strip()
            
            # Add section if it has content
            if len(section_content) > 10:
                sections[section_name] = section_content
        
        return sections

    def extract_key_concepts(self, text: str, focus: str) -> List[str]:
        """
        No concept extraction - delegate to AI analysis
        
        Args:
            text: Full text content of the paper
            focus: Focus type (ignored)
            
        Returns:
            Empty list - concept extraction removed
        """
        # No intelligent concept extraction - let Claude analyze the content
        return []

    def _extract_equations(self, text: str) -> List[str]:
        """
        No equation extraction - delegate to AI analysis
        
        Args:
            text: Full text content
            
        Returns:
            Empty list - equation extraction removed
        """
        # No intelligent equation extraction - let Claude identify equations
        return []

    def _extract_methodologies(self, text: str) -> List[str]:
        """
        No methodology extraction - delegate to AI analysis
        
        Args:
            text: Full text content
            
        Returns:
            Empty list - methodology extraction removed
        """
        # No intelligent methodology extraction - let Claude analyze methods
        return []