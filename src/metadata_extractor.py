"""
Robust metadata extraction for scientific PDFs
Combines multiple strategies to handle messy real-world PDFs
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import PyPDF2
import pdfplumber
from datetime import datetime

try:
    from .models import PaperMetadata
except ImportError:
    from models import PaperMetadata


class MetadataExtractor:
    """
    Robust metadata extractor that combines multiple strategies:
    1. PDF embedded metadata (with validation)
    2. First-page text parsing with heuristics
    3. Filename parsing as fallback
    4. Content-based year/DOI extraction
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_metadata(self, pdf_path: str, pdf_text: str) -> PaperMetadata:
        """
        Extract metadata using multiple strategies
        
        Args:
            pdf_path: Path to PDF file
            pdf_text: Extracted text content from PDF
            
        Returns:
            PaperMetadata: Extracted and validated metadata
        """
        self.logger.info(f"Extracting metadata from {pdf_path}")
        
        # Strategy 1: Try PDF embedded metadata
        embedded_metadata = self._extract_embedded_metadata(pdf_path)
        
        # Strategy 2: Parse first page text
        text_metadata = self._extract_text_metadata(pdf_text)
        
        # Strategy 3: Parse filename
        filename_metadata = self._extract_filename_metadata(pdf_path)
        
        # Strategy 4: Extract DOI and year from content
        content_metadata = self._extract_content_metadata(pdf_text)
        
        # Combine all strategies with priority
        final_metadata = self._combine_metadata_sources(
            embedded_metadata, text_metadata, filename_metadata, content_metadata, pdf_path
        )
        
        return final_metadata
    
    def _extract_embedded_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract and validate embedded PDF metadata"""
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if reader.metadata:
                    raw_title = reader.metadata.get('/Title')
                    raw_author = reader.metadata.get('/Author')
                    
                    # Validate title
                    if self._is_valid_embedded_title(raw_title):
                        metadata['embedded_title'] = raw_title.strip()
                        self.logger.debug(f"Valid embedded title: {raw_title}")
                    
                    # Validate author
                    if self._is_valid_embedded_author(raw_author):
                        metadata['embedded_author'] = raw_author.strip()
                        self.logger.debug(f"Valid embedded author: {raw_author}")
                    
                    # Other metadata
                    metadata['creator'] = reader.metadata.get('/Creator')
                    metadata['producer'] = reader.metadata.get('/Producer')
                    
        except Exception as e:
            self.logger.warning(f"Could not extract embedded metadata: {e}")
        
        return metadata
    
    def _extract_text_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from first page text using heuristics"""
        metadata = {}
        
        # Get first page (approximately first 3000 characters)
        first_page = text[:3000]
        lines = [line.strip() for line in first_page.split('\n') if line.strip()]
        
        # Extract title using multiple methods
        title = self._extract_title_from_lines(lines)
        if title:
            metadata['text_title'] = title
            self.logger.debug(f"Extracted title from text: {title}")
        
        # Extract authors
        authors = self._extract_authors_from_lines(lines)
        if authors:
            metadata['text_authors'] = authors
            metadata['text_first_author'] = authors[0]
            self.logger.debug(f"Extracted authors from text: {authors}")
        
        return metadata
    
    def _extract_filename_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from filename patterns"""
        metadata = {}
        filename = Path(pdf_path).stem
        
        # Common academic filename patterns
        patterns = [
            # "Smith et al. - 2020 - Title of Paper"
            r'^([A-Z][a-z]+\s+et\s+al\.?)\s*-\s*(\d{4})\s*-\s*(.+)$',
            # "Smith - 2020 - Title"
            r'^([A-Z][a-z]+)\s*-\s*(\d{4})\s*-\s*(.+)$',
            # "Smith_et_al_2020_Title"
            r'^([A-Z][a-z]+_et_al)_(\d{4})_(.+)$',
            # "Smith_2020_Title"
            r'^([A-Z][a-z]+)_(\d{4})_(.+)$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                author, year, title = match.groups()
                # Extract first author name from "Author et al." format
                if "et al" in author.lower():
                    first_author = author.split()[0]  # Take just the first word (surname)
                else:
                    first_author = author
                metadata['filename_author'] = author  # Keep full author info for display
                metadata['filename_first_author'] = first_author  # For citekey generation
                metadata['filename_year'] = int(year)
                metadata['filename_title'] = title.replace('_', ' ').replace('-', ' ').strip()
                self.logger.debug(f"Extracted from filename: {author}, {year}, {title}")
                break
        
        return metadata
    
    def _extract_content_metadata(self, text: str) -> Dict[str, Any]:
        """Extract DOI, year, and other metadata from full content"""
        metadata = {}
        
        # Extract DOI
        doi_patterns = [
            r'(?:doi:|DOI:)\s*(10\.\d+/[^\s]+)',
            r'\b(10\.\d+/[^\s]+)\b',
            r'https?://(?:dx\.)?doi\.org/(10\.\d+/[^\s]+)'
        ]
        
        for pattern in doi_patterns:
            match = re.search(pattern, text)
            if match:
                metadata['content_doi'] = match.group(1)
                self.logger.debug(f"Found DOI: {match.group(1)}")
                break
        
        # Extract year (look for 4-digit years in reasonable range)
        year_pattern = r'\b(19[8-9]\d|20[0-2]\d)\b'
        years = re.findall(year_pattern, text[:5000])  # Look in first 5000 chars
        if years:
            # Take the most recent reasonable year
            year_counts = {}
            for year in years:
                year_int = int(year)
                if 1980 <= year_int <= datetime.now().year + 1:
                    year_counts[year_int] = year_counts.get(year_int, 0) + 1
            
            if year_counts:
                # Most frequent year in reasonable range
                most_frequent_year = max(year_counts.items(), key=lambda x: x[1])[0]
                metadata['content_year'] = most_frequent_year
                self.logger.debug(f"Extracted year: {most_frequent_year}")
        
        return metadata
    
    def _extract_title_from_lines(self, lines: List[str]) -> Optional[str]:
        """Extract title from text lines using heuristics"""
        title_candidates = []
        
        for i, line in enumerate(lines[:15]):  # Check first 15 lines
            if not line or len(line) < 10:
                continue
            
            # Skip obvious non-title lines
            if self._is_likely_non_title(line):
                continue
            
            # Score potential titles
            score = self._score_title_candidate(line, i)
            if score > 0:
                title_candidates.append((score, line))
        
        if title_candidates:
            # Return highest scoring candidate
            title_candidates.sort(reverse=True)
            return title_candidates[0][1]
        
        return None
    
    def _extract_authors_from_lines(self, lines: List[str]) -> List[str]:
        """Extract authors from text lines"""
        authors = []
        
        # Look for author patterns in first 20 lines
        for line in lines[:20]:
            if not line:
                continue
            
            # Pattern 1: "Author1, Author2, and Author3"
            if ' and ' in line and ',' in line:
                potential_authors = self._parse_author_list(line)
                if potential_authors:
                    authors.extend(potential_authors)
                    break
            
            # Pattern 2: "FirstName LastName" (single author)
            single_author = self._extract_single_author(line)
            if single_author and len(authors) < 3:  # Limit to avoid false positives
                authors.append(single_author)
        
        # Clean and validate authors
        clean_authors = []
        for author in authors:
            if self._is_valid_author_name(author):
                clean_authors.append(author)
        
        return clean_authors[:6]  # Reasonable limit
    
    def _is_valid_embedded_title(self, title: str) -> bool:
        """Check if embedded PDF title looks valid"""
        if not title or len(title.strip()) < 5:
            return False
        
        title_lower = title.strip().lower()
        
        # Common junk titles
        junk_patterns = [
            r'^untitled',
            r'^document\\d*$',
            r'^microsoft word',
            r'^draft\\d*',
            r'^temp',
            r'^new document',
            r'^page \\d+',
            r'^\\d+$',
            r'^[a-f0-9]{8,}$',  # Hex strings
        ]
        
        return not any(re.search(pattern, title_lower) for pattern in junk_patterns)
    
    def _is_valid_embedded_author(self, author: str) -> bool:
        """Check if embedded PDF author looks valid"""
        if not author or len(author.strip()) < 2:
            return False
        
        author_lower = author.strip().lower()
        
        junk_authors = {
            'user', 'admin', 'administrator', 'owner', 'guest',
            'microsoft office user', 'default user', 'unknown'
        }
        
        return author_lower not in junk_authors and not author_lower.isdigit()
    
    def _is_likely_non_title(self, line: str) -> bool:
        """Check if line is likely NOT a title"""
        line_lower = line.lower()
        
        non_title_patterns = [
            r'^\\d+$',  # Just numbers
            r'^page \\d+',
            r'^doi\\s*:',
            r'^issn\\s*:',
            r'^abstract\\s*$',
            r'^keywords\\s*$',
            r'^introduction\\s*$',
            r'^www\\.|^http',
            r'^©|^copyright',
            r'^journal homepage',
            r'^\\d{4}-\\d{4}',  # ISSN format
            r'^received|^accepted|^published',
            r'^corresponding author',
        ]
        
        return any(re.search(pattern, line_lower) for pattern in non_title_patterns)
    
    def _score_title_candidate(self, line: str, position: int) -> int:
        """Score a line as a potential title"""
        score = 0
        
        # Length scoring
        if 20 <= len(line) <= 200:
            score += 3
        elif 10 <= len(line) <= 300:
            score += 1
        
        # Position scoring (earlier is better)
        if position < 5:
            score += 2
        elif position < 10:
            score += 1
        
        # Content scoring
        if line[0].isupper():
            score += 2
        
        # Title case scoring
        words = line.split()
        if len(words) >= 3:
            score += 1
            
        capitalized_words = sum(1 for word in words if word and word[0].isupper())
        if 0.3 <= capitalized_words / len(words) <= 0.8:  # Reasonable title case
            score += 2
        
        # Doesn't end with period (titles usually don't)
        if not line.endswith('.'):
            score += 1
        
        return score
    
    def _parse_author_list(self, line: str) -> List[str]:
        """Parse a line containing multiple authors"""
        # Handle "Author1, Author2, and Author3" format
        if ' and ' in line:
            parts = line.split(' and ')
            if len(parts) == 2:
                # "A, B, and C" -> ["A, B", "C"]
                first_part = parts[0]
                last_author = parts[1].strip()
                
                authors = [author.strip() for author in first_part.split(',')]
                authors.append(last_author)
                
                return [author for author in authors if author and len(author) > 2]
        
        return []
    
    def _extract_single_author(self, line: str) -> Optional[str]:
        """Extract single author from line"""
        # Look for "FirstName LastName" pattern
        name_pattern = r'\\b([A-Z][a-z]{2,15}\\s+[A-Z][a-z]{2,20})\\b'
        match = re.search(name_pattern, line)
        
        if match:
            name = match.group(1)
            if self._is_reasonable_name(name):
                return name
        
        return None
    
    def _is_valid_author_name(self, name: str) -> bool:
        """Validate author name"""
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        # No numbers or special characters
        if re.search(r'[0-9@#$%^&*()_+=\\[\\]{}|\\\\:";\'<>?,./]', name):
            return False
        
        return self._is_reasonable_name(name)
    
    def _is_reasonable_name(self, name: str) -> bool:
        """Check if name looks reasonable"""
        name_lower = name.lower()
        
        # Common false positives
        false_positives = {
            'united states', 'new york', 'los angeles', 'research center',
            'university press', 'corresponding author', 'email address',
            'journal homepage', 'creative commons', 'all rights'
        }
        
        return name_lower not in false_positives
    
    def _combine_metadata_sources(self, 
                                 embedded: Dict[str, Any],
                                 text: Dict[str, Any], 
                                 filename: Dict[str, Any],
                                 content: Dict[str, Any],
                                 pdf_path: str) -> PaperMetadata:
        """Combine metadata from all sources with priority"""
        
        # Title priority: text > embedded > filename > fallback
        title = (text.get('text_title') or 
                embedded.get('embedded_title') or 
                filename.get('filename_title') or 
                Path(pdf_path).stem)
        
        # Authors priority: filename > embedded > text (filename is more reliable for academic papers)
        authors = []
        first_author = "Unknown"
        
        if filename.get('filename_author'):
            # Use the first author name for citekey, full author string for display
            first_author = filename.get('filename_first_author', filename['filename_author'])
            authors = [filename['filename_author']]
        elif embedded.get('embedded_author'):
            # Try to parse embedded author
            embedded_author = embedded['embedded_author']
            if ',' in embedded_author:
                authors = [a.strip() for a in embedded_author.split(',')]
            else:
                authors = [embedded_author]
            first_author = authors[0] if authors else "Unknown"
        elif text.get('text_authors') and self._validate_text_authors(text['text_authors']):
            authors = text['text_authors']
            first_author = text['text_first_author']
        
        # Year priority: content > filename > current year
        year = (content.get('content_year') or 
               filename.get('filename_year') or 
               datetime.now().year)
        
        # DOI from content
        doi = content.get('content_doi')
        
        # Generate citekey
        citekey = self._generate_citekey(first_author, year, title)
        
        return PaperMetadata(
            title=title,
            first_author=first_author,
            authors=authors,
            year=year,
            citekey=citekey,
            doi=doi,
            page_count=0,  # Will be set by caller
            file_path=pdf_path
        )
    
    def _generate_citekey(self, first_author: str, year: int, title: str) -> str:
        """Generate citekey in authorYEARkeyword format"""
        # Clean author name
        if first_author and first_author != "Unknown":
            if ',' in first_author:
                author_part = first_author.split(',')[0].strip()
            else:
                parts = first_author.split()
                author_part = parts[-1] if parts else "unknown"
        else:
            author_part = "unknown"
        
        author_part = re.sub(r'[^a-zA-Z]', '', author_part).lower()
        
        # Year part
        year_part = str(year)
        
        # Keyword from title
        keyword_part = self._generate_keyword(title)
        
        return f"{author_part}{year_part}{keyword_part}"
    
    def _generate_keyword(self, title: str) -> str:
        """Generate keyword from title"""
        if not title:
            return "paper"
        
        # Clean and split
        clean_title = re.sub(r'[^\w\s]', '', title.lower())
        words = clean_title.split()
        
        # Remove stop words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'using', 'based', 'study', 'analysis',
            'this', 'article', 'paper', 'journal'
        }
        
        meaningful_words = [word for word in words 
                          if len(word) > 3 and word not in stop_words and word.isalpha()]
        
        if meaningful_words:
            keyword = meaningful_words[0]
            return keyword[:10].lower()  # Limit length
        
        return "paper"
    
    def _validate_text_authors(self, authors: List[str]) -> bool:
        """Validate that text-extracted authors are not scientific terms"""
        if not authors:
            return False
        
        # Common scientific terms that are often mistaken for author names
        scientific_terms = {
            'thermodynamic', 'stability', 'molecular', 'dynamics', 'simulation',
            'protein', 'folding', 'structure', 'function', 'analysis', 'study',
            'research', 'experimental', 'theoretical', 'computational', 'biophysical',
            'biochemical', 'chemical', 'physical', 'biological', 'statistical',
            'laboratory', 'institute', 'university', 'department', 'center', 'centre',
            'interactions', 'mechanisms', 'properties', 'characteristics', 'parameters'
        }
        
        for author in authors:
            if not author or len(author) < 3:
                return False
            
            # Check if author name contains scientific terms
            author_lower = author.lower()
            for term in scientific_terms:
                if term in author_lower:
                    return False
            
            # Check if it looks like an actual name (has reasonable word structure)
            words = author.split()
            if len(words) < 1 or len(words) > 4:  # Names typically 1-4 words
                return False
            
            # Each word should start with capital letter
            if not all(word[0].isupper() for word in words if word):
                return False
        
        return True