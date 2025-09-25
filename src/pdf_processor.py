"""
PDF processing component for ScholarSquill Kiro MCP Server
"""

import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import PyPDF2
import pdfplumber

try:
    from .interfaces import PDFProcessorInterface
    from .models import PaperMetadata
    from .exceptions import (
        FileError, ProcessingError, create_file_not_found_error, 
        create_invalid_pdf_error, ErrorCode
    )
    from .metadata_extractor import MetadataExtractor
except ImportError:
    from interfaces import PDFProcessorInterface
    from models import PaperMetadata
    from exceptions import (
        FileError, ProcessingError, create_file_not_found_error, 
        create_invalid_pdf_error, ErrorCode
    )
    from metadata_extractor import MetadataExtractor


class PDFProcessor(PDFProcessorInterface):
    """PDF processing implementation using PyPDF2 and pdfplumber"""
    
    def __init__(self, max_file_size_mb: int = 50):
        """
        Initialize PDF processor
        
        Args:
            max_file_size_mb: Maximum file size in MB to process
        """
        self.max_file_size_mb = max_file_size_mb
        self.logger = logging.getLogger(__name__)
        self.metadata_extractor = MetadataExtractor()
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate if file is a readable PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            bool: True if valid PDF, False otherwise
            
        Raises:
            FileError: If file doesn't exist or is too large
        """
        path = Path(pdf_path)
        
        # Check if file exists
        if not path.exists():
            raise create_file_not_found_error(pdf_path)
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise FileError(
                message=f"File too large: {file_size_mb:.1f}MB (max: {self.max_file_size_mb}MB)",
                error_code=ErrorCode.FILE_TOO_LARGE,
                file_path=pdf_path,
                suggestions=[
                    "Try processing a smaller file",
                    "Increase max_file_size_mb setting",
                    "Split the PDF into smaller parts"
                ]
            )
        
        # Check if it's a PDF file
        if not pdf_path.lower().endswith('.pdf'):
            raise FileError(
                message=f"File is not a PDF: {pdf_path}",
                error_code=ErrorCode.INVALID_PDF,
                file_path=pdf_path,
                suggestions=["Ensure the file has a .pdf extension"]
            )
        
        # Try to open with PyPDF2 to validate
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                # Try to access first page to validate
                if len(reader.pages) == 0:
                    return False
                _ = reader.pages[0]
                return True
        except Exception as e:
            self.logger.warning(f"PDF validation failed for {pdf_path}: {e}")
            return False
    
    def get_page_count(self, pdf_path: str) -> int:
        """
        Get number of pages in PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            int: Number of pages
            
        Raises:
            FileError: If PDF is invalid
            ProcessingError: If page count extraction fails
        """
        if not self.validate_pdf(pdf_path):
            raise create_invalid_pdf_error(pdf_path)
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            raise ProcessingError(
                message=f"Failed to get page count: {str(e)}",
                error_code=ErrorCode.PROCESSING_TIMEOUT,
                suggestions=["Check if PDF is corrupted", "Try with a different PDF"]
            )
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text content from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            str: Extracted text content
            
        Raises:
            FileError: If PDF is invalid
            ProcessingError: If text extraction fails
        """
        if not self.validate_pdf(pdf_path):
            raise create_invalid_pdf_error(pdf_path)
        
        # Try pdfplumber first (better for complex layouts)
        try:
            text = self._extract_text_with_pdfplumber(pdf_path)
            if text.strip():
                return text
        except Exception as e:
            self.logger.warning(f"pdfplumber extraction failed for {pdf_path}: {e}")
        
        # Fallback to PyPDF2
        try:
            text = self._extract_text_with_pypdf2(pdf_path)
            if text.strip():
                return text
        except Exception as e:
            self.logger.error(f"PyPDF2 extraction failed for {pdf_path}: {e}")
        
        # If both methods fail
        raise ProcessingError(
            message=f"Failed to extract text from PDF: {pdf_path}",
            error_code=ErrorCode.TEXT_EXTRACTION_FAILED,
            suggestions=[
                "Check if PDF contains extractable text",
                "Try OCR if PDF contains scanned images",
                "Ensure PDF is not password-protected"
            ]
        )
    
    def _extract_text_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber"""
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n\n'.join(text_parts)
    
    def _extract_text_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        text_parts = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n\n'.join(text_parts)
    
    def extract_metadata(self, pdf_path: str) -> PaperMetadata:
        """
        Extract metadata from PDF file using robust multi-strategy approach
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            PaperMetadata: Extracted metadata
            
        Raises:
            FileError: If PDF is invalid
            ProcessingError: If metadata extraction fails
        """
        if not self.validate_pdf(pdf_path):
            raise create_invalid_pdf_error(pdf_path)
        
        try:
            # Extract text content first
            text = self.extract_text(pdf_path)
            
            # Use robust metadata extractor
            metadata = self.metadata_extractor.extract_metadata(pdf_path, text)
            
            # Set page count
            metadata.page_count = self.get_page_count(pdf_path)
            
            self.logger.info(f"Successfully extracted metadata: title='{metadata.title}', "
                           f"author='{metadata.first_author}', year={metadata.year}, "
                           f"citekey='{metadata.citekey}'")
            
            return metadata
            
        except (FileError, ProcessingError):
            # Re-raise our custom errors
            raise
        except Exception as e:
            self.logger.error(f"Metadata extraction failed for {pdf_path}: {e}")
            raise ProcessingError(
                message=f"Failed to extract metadata: {str(e)}",
                error_code=ErrorCode.METADATA_EXTRACTION_FAILED,
                suggestions=[
                    "Check if PDF contains readable metadata",
                    "Try with a different PDF file",
                    "Ensure PDF is not corrupted"
                ]
            )
    
    def _extract_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF properties"""
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if reader.metadata:
                    metadata.update({
                        'title': reader.metadata.get('/Title', ''),
                        'author': reader.metadata.get('/Author', ''),
                        'subject': reader.metadata.get('/Subject', ''),
                        'creator': reader.metadata.get('/Creator', ''),
                        'producer': reader.metadata.get('/Producer', ''),
                        'creation_date': reader.metadata.get('/CreationDate', ''),
                        'modification_date': reader.metadata.get('/ModDate', '')
                    })
        except Exception as e:
            self.logger.warning(f"Failed to extract PDF metadata: {e}")
        
        return metadata
    
    def _extract_content_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from PDF content using regex patterns"""
        metadata = {}
        
        # Extract title (usually first large text block)
        title_match = self._extract_title_from_text(text)
        if title_match:
            metadata['content_title'] = title_match
        
        # Extract authors
        authors = self._extract_authors_from_text(text)
        if authors:
            metadata['content_authors'] = authors
        
        # Extract year
        year = self._extract_year_from_text(text)
        if year:
            metadata['content_year'] = year
        
        # Extract DOI
        doi = self._extract_doi_from_text(text)
        if doi:
            metadata['content_doi'] = doi
        
        # Extract journal information
        journal_info = self._extract_journal_info_from_text(text)
        metadata.update(journal_info)
        
        # Extract abstract
        abstract = self._extract_abstract_from_text(text)
        if abstract:
            metadata['content_abstract'] = abstract
        
        return metadata
    
    def _extract_title_from_text(self, text: str) -> Optional[str]:
        """Extract title from text content - improved approach for academic papers"""
        
        # Method 1: Look for title in the filename pattern first
        # Many academic PDFs have titles in "Author - Year - Title" format
        
        # Method 2: Extract from text content
        lines = text.split('\n')
        title_candidates = []
        
        # Look for the actual paper title (usually appears after metadata but before abstract)
        for i, line in enumerate(lines[:50]):  # Check first 50 lines
            line = line.strip()
            
            if not line or len(line) < 15:
                continue
            
            # Skip obvious metadata and headers
            skip_patterns = [
                r'^\d+$',
                r'^page\s*\d+',
                r'^doi\s*:',
                r'^issn\s*:',
                r'^journal\s+of',
                r'^contents\s+list',
                r'^www\.|^http',
                r'^\d{4}-\d{4}',  # ISSN
                r'^volume\s+\d+',
                r'^number\s+\d+',
                r'^©|^copyright',
                r'^received|^accepted|^published',
                r'^corresponding\s+author',
                r'^email\s*:',
                r'^abstract\s*$',
                r'^keywords\s*$',
                r'^introduction\s*$',
                r'^this\s+article\s+is\s+licensed',
                r'^this\s+is\s+an\s+open\s+access',
            ]
            
            if any(re.search(pattern, line.lower()) for pattern in skip_patterns):
                continue
            
            # Look for title characteristics
            score = 0
            
            # Good title length
            if 25 <= len(line) <= 150:
                score += 4
            elif 15 <= len(line) <= 200:
                score += 2
            
            # Title case characteristics
            words = line.split()
            if len(words) >= 4:  # Substantial title
                score += 2
                
                # Check for title case (most words capitalized)
                capitalized_words = sum(1 for word in words if word[0].isupper() and len(word) > 2)
                if capitalized_words >= len(words) * 0.6:  # At least 60% capitalized
                    score += 3
            
            # Doesn't end with period (academic titles usually don't)
            if not line.endswith('.'):
                score += 1
            
            # Contains academic keywords
            academic_keywords = ['analysis', 'study', 'investigation', 'research', 'approach', 
                               'method', 'model', 'system', 'effect', 'impact', 'role', 'using']
            if any(keyword in line.lower() for keyword in academic_keywords):
                score += 2
            
            # Position bonus (titles usually appear early but after initial metadata)
            if 5 <= i <= 25:
                score += 1
            
            if score >= 6:  # Higher threshold for better quality
                title_candidates.append((score, line, i))
        
        # Method 3: Look for specific academic title patterns
        # Pattern: "Title of the Paper" (standalone line with title characteristics)
        for i, line in enumerate(lines[:30]):
            line = line.strip()
            
            # Must be substantial and look like a title
            if (20 <= len(line) <= 150 and 
                not line.endswith('.') and 
                len(line.split()) >= 4 and
                line[0].isupper()):
                
                # Check if it's surrounded by shorter lines (typical title formatting)
                prev_line = lines[i-1].strip() if i > 0 else ""
                next_line = lines[i+1].strip() if i < len(lines)-1 else ""
                
                if (len(prev_line) < len(line) * 0.7 and 
                    len(next_line) < len(line) * 0.7):
                    title_candidates.append((8, line, i))  # High score for this pattern
        
        # Return best candidate
        if title_candidates:
            title_candidates.sort(key=lambda x: (-x[0], x[2]))
            best_title = title_candidates[0][1]
            
            # Clean the title
            best_title = re.sub(r'\s+', ' ', best_title).strip()
            
            # Remove common prefixes/suffixes
            prefixes_to_remove = ['title:', 'title', 'research article:', 'article:']
            for prefix in prefixes_to_remove:
                if best_title.lower().startswith(prefix):
                    best_title = best_title[len(prefix):].strip()
            
            return best_title
        
        return None
    
    def _extract_authors_from_text(self, text: str) -> List[str]:
        """Extract authors from text content - focused on academic papers"""
        authors = []
        
        # Look for authors in first 3000 characters where they typically appear
        search_text = text[:3000]
        lines = search_text.split('\n')
        
        # Method 1: Look for author lines (typically appear after title, before abstract)
        for i, line in enumerate(lines[:30]):
            line = line.strip()
            
            # Skip empty lines and obvious non-author content
            if not line or len(line) < 5:
                continue
            
            # Skip lines that are clearly not authors
            skip_patterns = [
                r'^\d+$',
                r'^abstract\s*$',
                r'^keywords\s*$',
                r'^introduction\s*$',
                r'^doi\s*:',
                r'^journal\s+of',
                r'^www\.|^http',
                r'^corresponding\s+author',
                r'^email\s*:',
                r'^\d{4}-\d{4}',  # ISSN
                r'^volume\s+\d+',
                r'^received|^accepted|^published',
            ]
            
            if any(re.search(pattern, line.lower()) for pattern in skip_patterns):
                continue
            
            # Look for author patterns in this line
            found_authors = self._extract_authors_from_line(line)
            if found_authors:
                authors.extend(found_authors)
                if len(authors) >= 6:  # Stop after finding enough authors
                    break
        
        # Method 2: Look for "et al." patterns (very reliable indicator)
        et_al_patterns = [
            r'([A-Z][a-z]{2,15}(?:\s+[A-Z][a-z]{2,15})*)\s+et\s+al\.?',
            r'([A-Z][a-z]{2,15})\s+et\s+al\.?',
        ]
        
        for pattern in et_al_patterns:
            matches = re.findall(pattern, search_text)
            for match in matches:
                if self._is_reasonable_author(match) and match not in authors:
                    authors.insert(0, match)  # Put first author at beginning
        
        # Method 3: Extract from filename pattern if we can infer it
        # Many PDFs follow "FirstAuthor et al. - Year - Title" format
        
        # Clean and deduplicate
        final_authors = []
        seen = set()
        
        for author in authors:
            author = author.strip()
            if (author and 
                len(author) > 3 and 
                self._is_reasonable_author(author) and 
                author.lower() not in seen):
                seen.add(author.lower())
                final_authors.append(author)
        
        return final_authors[:6]
    
    def _extract_authors_from_line(self, line: str) -> List[str]:
        """Extract authors from a single line of text"""
        authors = []
        
        # Pattern 1: "LastName, F.M." format
        academic_pattern = r'([A-Z][a-z]{2,15}),\s*([A-Z]\.(?:\s*[A-Z]\.)*)'
        matches = re.findall(academic_pattern, line)
        for last, first in matches:
            if self._is_valid_author_name(last, first):
                authors.append(f"{last}, {first}")
        
        # Pattern 2: "FirstName LastName" format
        if not authors:  # Only try this if academic format didn't work
            name_pattern = r'\b([A-Z][a-z]{2,12}\s+[A-Z][a-z]{2,15})\b'
            matches = re.findall(name_pattern, line)
            for name in matches:
                if self._is_likely_author_name(name):
                    authors.append(name)
        
        # Pattern 3: Multiple authors separated by commas or "and"
        if not authors and (',' in line or ' and ' in line):
            # Split by common separators
            parts = re.split(r',|\s+and\s+', line)
            for part in parts:
                part = part.strip()
                if self._looks_like_author_name(part):
                    authors.append(part)
        
        return authors
    
    def _looks_like_author_name(self, text: str) -> bool:
        """Quick check if text looks like an author name"""
        if not text or len(text) < 4 or len(text) > 40:
            return False
        
        # Should have 1-3 words
        words = text.split()
        if not (1 <= len(words) <= 3):
            return False
        
        # Each word should start with capital and be mostly letters
        for word in words:
            if not word[0].isupper() or not word.replace('.', '').isalpha():
                return False
        
        return True
    
    def _is_valid_author_name(self, last: str, first: str) -> bool:
        """Check if extracted name components look like real author names"""
        # Check length
        if len(last) < 2 or len(last) > 20:
            return False
        if len(first) < 1 or len(first) > 20:
            return False
        
        # Check for common false positives
        false_positives = {
            'journal', 'article', 'paper', 'study', 'research', 'university',
            'department', 'institute', 'center', 'laboratory', 'group',
            'society', 'association', 'foundation', 'press', 'publisher',
            'copyright', 'rights', 'license', 'terms', 'conditions'
        }
        
        if last.lower() in false_positives or first.lower() in false_positives:
            return False
        
        return True
    
    def _is_likely_author_name(self, name: str) -> bool:
        """Check if a full name looks like a real author name"""
        parts = name.split()
        if len(parts) != 2:
            return False
        
        first, last = parts
        
        # Basic validation
        if not self._is_valid_author_name(last, first):
            return False
        
        # Additional checks for full names
        common_false_positives = {
            'United States', 'New York', 'Los Angeles', 'San Francisco',
            'Research Center', 'University Press', 'Science Journal',
            'Nature Publishing', 'Academic Press', 'John Wiley',
            'Copyright Notice', 'All Rights', 'Open Access',
            'Creative Commons', 'License Agreement', 'Terms Conditions',
            'Journal Homepage', 'Online Version', 'Print Version',
            'Corresponding Author', 'Email Address', 'Phone Number'
        }
        
        if name in common_false_positives:
            return False
        
        # Check if it looks like institutional text
        institutional_words = {'university', 'institute', 'center', 'laboratory', 'department'}
        if any(word in name.lower() for word in institutional_words):
            return False
        
        return True
    
    def _is_reasonable_author(self, author: str) -> bool:
        """Final validation for author names"""
        # Skip very short or very long names
        if len(author) < 4 or len(author) > 50:
            return False
        
        # Skip names with numbers or special characters
        if re.search(r'[0-9@#$%^&*()_+=\[\]{}|\\:";\'<>?,./]', author):
            return False
        
        # Skip all caps (likely headers or institutional text)
        if author.isupper():
            return False
        
        return True
    
    def _extract_year_from_text(self, text: str) -> Optional[int]:
        """Extract publication year from text"""
        # Look for 4-digit years in reasonable range
        year_pattern = r'\b(19[8-9]\d|20[0-2]\d)\b'
        matches = re.findall(year_pattern, text[:3000])
        
        if matches:
            # Return the most recent reasonable year
            years = [int(year) for year in matches]
            return max(years)
        
        return None
    
    def _extract_doi_from_text(self, text: str) -> Optional[str]:
        """Extract DOI from text"""
        doi_pattern = r'(?:doi:|DOI:)\s*(10\.\d+/[^\s]+)'
        match = re.search(doi_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        # Alternative pattern
        doi_pattern2 = r'\b(10\.\d+/[^\s]+)\b'
        match = re.search(doi_pattern2, text)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_journal_info_from_text(self, text: str) -> Dict[str, str]:
        """Extract journal, volume, issue, pages from text"""
        info = {}
        
        # Look for journal patterns
        journal_patterns = [
            r'([A-Z][a-zA-Z\s&]+Journal[a-zA-Z\s]*)',
            r'([A-Z][a-zA-Z\s&]+Review[a-zA-Z\s]*)',
            r'([A-Z][a-zA-Z\s&]+Proceedings[a-zA-Z\s]*)',
        ]
        
        for pattern in journal_patterns:
            match = re.search(pattern, text[:2000])
            if match:
                info['journal'] = match.group(1).strip()
                break
        
        # Look for volume/issue/pages
        vol_pattern = r'Vol\.?\s*(\d+)'
        vol_match = re.search(vol_pattern, text[:3000], re.IGNORECASE)
        if vol_match:
            info['volume'] = vol_match.group(1)
        
        issue_pattern = r'(?:No\.?|Issue)\s*(\d+)'
        issue_match = re.search(issue_pattern, text[:3000], re.IGNORECASE)
        if issue_match:
            info['issue'] = issue_match.group(1)
        
        pages_pattern = r'pp\.?\s*(\d+[-–]\d+)'
        pages_match = re.search(pages_pattern, text[:3000], re.IGNORECASE)
        if pages_match:
            info['pages'] = pages_match.group(1)
        
        return info
    
    def _extract_abstract_from_text(self, text: str) -> Optional[str]:
        """Extract abstract from text"""
        # Look for abstract section
        abstract_pattern = r'(?:ABSTRACT|Abstract)\s*[:\-]?\s*\n?(.*?)(?:\n\s*\n|\n\s*(?:Keywords|KEYWORDS|Introduction|INTRODUCTION))'
        match = re.search(abstract_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            abstract = match.group(1).strip()
            # Clean up the abstract
            abstract = re.sub(r'\s+', ' ', abstract)  # Normalize whitespace
            if len(abstract) > 50 and len(abstract) < 2000:  # Reasonable length
                return abstract
        
        return None
    
    def _combine_metadata(self, pdf_metadata: Dict[str, Any], content_metadata: Dict[str, Any], 
                         file_path: str, page_count: int) -> PaperMetadata:
        """Combine metadata from different sources"""
        
        # Title: prefer content over PDF metadata
        title = (content_metadata.get('content_title') or 
                pdf_metadata.get('title') or 
                Path(file_path).stem)
        
        # Authors: prefer content extraction
        authors = content_metadata.get('content_authors', [])
        if not authors and pdf_metadata.get('author'):
            # Try to parse PDF author field
            author_text = pdf_metadata['author']
            authors = [name.strip() for name in re.split(r'[,;]', author_text) if name.strip()]
        
        first_author = authors[0] if authors else "Unknown"
        
        # Year: prefer content extraction
        year = content_metadata.get('content_year')
        
        # DOI
        doi = content_metadata.get('content_doi')
        
        # Journal info
        journal = content_metadata.get('journal', '')
        volume = content_metadata.get('volume')
        issue = content_metadata.get('issue')
        pages = content_metadata.get('pages')
        
        # Abstract
        abstract = content_metadata.get('content_abstract')
        
        return PaperMetadata(
            title=title,
            first_author=first_author,
            authors=authors,
            year=year,
            journal=journal,
            volume=volume,
            issue=issue,
            pages=pages,
            doi=doi,
            abstract=abstract,
            page_count=page_count,
            file_path=file_path
        )
    
    def generate_citekey(self, metadata: PaperMetadata) -> str:
        """
        Generate citation key from metadata following authorYEARkeyword format
        
        Args:
            metadata: Paper metadata
            
        Returns:
            str: Generated citation key in format: authorYEARkeyword
        """
        # Get first author's last name
        author_part = "unknown"
        
        if metadata.first_author and metadata.first_author != "Unknown":
            # Handle different author formats
            if ',' in metadata.first_author:
                # "Smith, John" or "Smith, J." format
                author_last = metadata.first_author.split(',')[0].strip()
            else:
                # "John Smith" format - take last word
                parts = metadata.first_author.strip().split()
                author_last = parts[-1] if parts else "unknown"
            
            # Clean and normalize author name
            author_part = re.sub(r'[^a-zA-Z]', '', author_last).lower()
            
            # Ensure reasonable length
            if len(author_part) < 2:
                author_part = "unknown"
            elif len(author_part) > 15:
                author_part = author_part[:15]
        
        # Get year
        year_part = str(metadata.year) if metadata.year else "2023"  # Default to current-ish year
        
        # Generate keyword from title
        keyword_part = self._generate_keyword_from_title(metadata.title)
        
        # Ensure all parts are reasonable
        if not author_part or author_part == "unknown":
            author_part = "paper"
        
        citekey = f"{author_part}{year_part}{keyword_part}"
        
        # Ensure citekey is reasonable length
        if len(citekey) > 50:
            citekey = f"{author_part}{year_part}{keyword_part[:10]}"
        
        return citekey
    
    def _generate_keyword_from_title(self, title: str) -> str:
        """Generate keyword from paper title - more robust approach"""
        if not title or len(title) < 3:
            return "paper"
        
        # Clean title and split into words
        title_clean = re.sub(r'[^\w\s]', '', title.lower())
        words = title_clean.split()
        
        # Remove common stop words and short words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'using', 'based', 'study', 'analysis',
            'this', 'article', 'paper', 'journal', 'issn', 'print', 'online',
            'homepage', 'www', 'com', 'under', 'license', 'which', 'permits'
        }
        
        # Find meaningful words (length > 3, not stop words, not numbers)
        meaningful_words = []
        for word in words:
            if (len(word) > 3 and 
                word not in stop_words and 
                not word.isdigit() and 
                word.isalpha()):
                meaningful_words.append(word)
        
        if meaningful_words:
            # Take first meaningful word
            keyword = meaningful_words[0]
            # Ensure reasonable length
            if len(keyword) > 12:
                keyword = keyword[:12]
            return keyword.lower()
        else:
            # Fallback: take first non-stop word regardless of length
            for word in words:
                if word not in stop_words and word.isalpha() and len(word) > 2:
                    return word.lower()[:8]
            
            return "paper"