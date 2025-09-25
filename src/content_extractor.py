"""
Content extractor for AI analysis - extracts PDF content without attempting analysis
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

try:
    from .pdf_processor import PDFProcessor
    from .metadata_extractor import MetadataExtractor
    from .models import PaperMetadata
    from .exceptions import PDFProcessingError, ErrorCode
except ImportError:
    from pdf_processor import PDFProcessor
    from metadata_extractor import MetadataExtractor
    from models import PaperMetadata
    from exceptions import PDFProcessingError, ErrorCode


class ContentExtractor:
    """Extract and structure PDF content for AI analysis without attempting intelligent analysis"""
    
    def __init__(self):
        """Initialize content extractor"""
        self.pdf_processor = PDFProcessor()
        self.metadata_extractor = MetadataExtractor()
        self.logger = logging.getLogger(__name__)
    
    async def extract_for_analysis(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract PDF content structured for AI analysis
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict containing raw content, structured content, metadata, and stats
        """
        try:
            # Extract raw content
            self.logger.info(f"Extracting content from: {pdf_path}")
            raw_content = self.pdf_processor.extract_text(pdf_path)
            
            if not raw_content or len(raw_content.strip()) < 100:
                raise PDFProcessingError(
                    "Extracted text is too short or empty", 
                    error_code=ErrorCode.TEXT_EXTRACTION_FAILED
                )
            
            # Extract metadata
            metadata = self.pdf_processor.extract_metadata(pdf_path)
            
            # Basic structure extraction (no analysis)
            structured_content = self._structure_content(raw_content)
            
            # Calculate content statistics
            content_stats = self._calculate_content_stats(raw_content)
            
            return {
                "raw_content": raw_content,
                "structured_content": structured_content,
                "metadata": metadata.to_dict() if hasattr(metadata, 'to_dict') else self._metadata_to_dict(metadata),
                "content_stats": content_stats,
                "source_path": pdf_path
            }
            
        except Exception as e:
            self.logger.error(f"Content extraction failed for {pdf_path}: {str(e)}")
            raise PDFProcessingError(
                f"Failed to extract content: {str(e)}", 
                error_code=ErrorCode.TEXT_EXTRACTION_FAILED
            )
    
    def _structure_content(self, content: str) -> Dict[str, Any]:
        """
        Basic content structuring without analysis
        
        Args:
            content: Raw PDF text content
            
        Returns:
            Dict with basic structure detection
        """
        # Simple section detection (no intelligent analysis)
        sections = self._detect_basic_sections(content)
        
        # Extract potential equations/figures (basic detection)
        equations = self._detect_equations(content)
        figures = self._detect_figures(content)
        tables = self._detect_tables(content)
        references = self._detect_references(content)
        
        return {
            "sections": sections,
            "equations": equations,
            "figures": figures,
            "tables": tables,
            "references": references,
            "paragraphs": self._split_paragraphs(content)
        }
    
    def _detect_basic_sections(self, content: str) -> Dict[str, str]:
        """
        Basic section detection using common patterns
        
        Args:
            content: Raw text content
            
        Returns:
            Dict mapping section names to content
        """
        sections = {}
        
        # Common section headers (case-insensitive)
        section_patterns = {
            'abstract': [r'\n\s*abstract\s*\n', r'\n\s*summary\s*\n'],
            'introduction': [r'\n\s*(?:1\.?\s*)?introduction\s*\n'],
            'methods': [r'\n\s*(?:\d+\.?\s*)?(?:methods?|methodology|experimental)\s*\n'],
            'results': [r'\n\s*(?:\d+\.?\s*)?results\s*\n'],
            'discussion': [r'\n\s*(?:\d+\.?\s*)?discussion\s*\n'],
            'conclusion': [r'\n\s*(?:\d+\.?\s*)?conclusions?\s*\n'],
            'references': [r'\n\s*(?:references|bibliography)\s*\n']
        }
        
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    start_pos = match.end()
                    # Find next section or end of document
                    next_section_pos = len(content)
                    for other_patterns in section_patterns.values():
                        for other_pattern in other_patterns:
                            next_match = re.search(other_pattern, content[start_pos:], re.IGNORECASE)
                            if next_match:
                                next_section_pos = min(next_section_pos, start_pos + next_match.start())
                    
                    section_content = content[start_pos:next_section_pos].strip()
                    if section_content:
                        sections[section_name] = section_content
                    break
        
        return sections
    
    def _detect_equations(self, content: str) -> List[str]:
        """
        Detect potential equations in text
        
        Args:
            content: Raw text content
            
        Returns:
            List of potential equation strings
        """
        equations = []
        
        # Look for mathematical expressions
        equation_patterns = [
            r'\$[^$]+\$',  # LaTeX inline math
            r'\$\$[^$]+\$\$',  # LaTeX display math
            r'\\begin\{equation\}.*?\\end\{equation\}',  # LaTeX equation environment
            r'\\begin\{align\}.*?\\end\{align\}',  # LaTeX align environment
            r'\([^)]*[=<>±∑∫∂∇][^)]*\)',  # Parenthetical expressions with math symbols
            r'[A-Za-z]\s*[=<>]\s*[^.!?]*[0-9]'  # Simple variable assignments
        ]
        
        for pattern in equation_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            equations.extend(matches)
        
        # Remove duplicates and filter out very short matches
        equations = list(set([eq.strip() for eq in equations if len(eq.strip()) > 3]))
        
        return equations[:20]  # Limit to first 20 equations
    
    def _detect_figures(self, content: str) -> List[str]:
        """
        Detect figure references
        
        Args:
            content: Raw text content
            
        Returns:
            List of figure references
        """
        figure_patterns = [
            r'Figure\s+\d+[^.]*\.?',
            r'Fig\.\s*\d+[^.]*\.?',
            r'figure\s+\d+[^.]*\.?'
        ]
        
        figures = []
        for pattern in figure_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            figures.extend(matches)
        
        # Remove duplicates
        figures = list(set([fig.strip() for fig in figures]))
        
        return figures[:10]  # Limit to first 10 figures
    
    def _detect_tables(self, content: str) -> List[str]:
        """
        Detect table references
        
        Args:
            content: Raw text content
            
        Returns:
            List of table references
        """
        table_patterns = [
            r'Table\s+\d+[^.]*\.?',
            r'table\s+\d+[^.]*\.?'
        ]
        
        tables = []
        for pattern in table_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            tables.extend(matches)
        
        # Remove duplicates
        tables = list(set([table.strip() for table in tables]))
        
        return tables[:10]  # Limit to first 10 tables
    
    def _detect_references(self, content: str) -> List[str]:
        """
        Detect reference section
        
        Args:
            content: Raw text content
            
        Returns:
            List of reference entries (first few)
        """
        # Look for references section
        ref_pattern = r'\n\s*(?:references|bibliography)\s*\n(.*?)(?:\n\s*(?:appendix|acknowledgments?)\s*\n|$)'
        match = re.search(ref_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            ref_section = match.group(1)
            # Split into individual references (basic approach)
            ref_lines = [line.strip() for line in ref_section.split('\n') if line.strip()]
            # Filter lines that look like references (contain years, authors, etc.)
            references = []
            for line in ref_lines[:20]:  # Limit to first 20 lines
                if re.search(r'\b(19|20)\d{2}\b', line) and len(line) > 20:
                    references.append(line)
            
            return references[:10]  # Limit to first 10 references
        
        return []
    
    def _split_paragraphs(self, content: str) -> List[str]:
        """
        Split content into paragraphs
        
        Args:
            content: Raw text content
            
        Returns:
            List of paragraph strings
        """
        # Split by double newlines and filter out short paragraphs
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', content) if len(p.strip()) > 50]
        
        return paragraphs[:50]  # Limit to first 50 paragraphs
    
    def _calculate_content_stats(self, content: str) -> Dict[str, Any]:
        """
        Calculate basic content statistics
        
        Args:
            content: Raw text content
            
        Returns:
            Dict with content statistics
        """
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        return {
            "total_length": len(content),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len(re.split(r'\n\s*\n', content)),
            "estimated_pages": max(1, len(content) // 3000),  # Rough estimate
            "avg_words_per_sentence": len(words) / max(1, len([s for s in sentences if s.strip()])),
            "reading_time_minutes": max(1, len(words) // 200)  # Rough estimate at 200 WPM
        }
    
    def _metadata_to_dict(self, metadata: PaperMetadata) -> Dict[str, Any]:
        """
        Convert metadata object to dictionary
        
        Args:
            metadata: PaperMetadata object
            
        Returns:
            Dict representation of metadata
        """
        return {
            "title": getattr(metadata, 'title', ''),
            "first_author": getattr(metadata, 'first_author', ''),
            "authors": getattr(metadata, 'authors', []),
            "year": getattr(metadata, 'year', None),
            "journal": getattr(metadata, 'journal', ''),
            "doi": getattr(metadata, 'doi', ''),
            "citekey": getattr(metadata, 'citekey', ''),
            "page_count": getattr(metadata, 'page_count', 0),
            "abstract": getattr(metadata, 'abstract', ''),
            "keywords": getattr(metadata, 'keywords', [])
        }