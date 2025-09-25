"""
Utility functions for ScholarSquill Kiro MCP Server
"""

import re
import hashlib
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    from .models import PaperMetadata, ProcessingOptions
except ImportError:
    from models import PaperMetadata, ProcessingOptions


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename by removing invalid characters and limiting length
    
    Args:
        filename: Original filename
        max_length: Maximum length for filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()
    
    # Ensure not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def generate_citekey(first_author: str, year: Optional[int], title: str) -> str:
    """
    Generate citation key in format: authorYEARkeyword
    
    Args:
        first_author: First author's name (can be "LastName, FirstName" or "FirstName LastName")
        year: Publication year
        title: Paper title
        
    Returns:
        Generated citation key
    """
    # Extract last name from first author
    # Handle "LastName, FirstName" format
    if ',' in first_author:
        last_name = first_author.split(',')[0].strip()
    else:
        # Handle "FirstName LastName" format
        author_parts = first_author.split()
        last_name = author_parts[-1] if author_parts else "unknown"
    
    # Clean author name (remove non-alphabetic characters)
    author_clean = re.sub(r'[^a-zA-Z]', '', last_name).lower()
    
    # Get year string
    year_str = str(year) if year else "unknown"
    
    # Extract first meaningful word from title (3+ characters)
    title_words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
    keyword = title_words[0] if title_words else "paper"
    
    return f"{author_clean}{year_str}{keyword}"


def extract_first_author_lastname(authors: List[str]) -> str:
    """
    Extract last name from first author
    
    Args:
        authors: List of author names
        
    Returns:
        Last name of first author
    """
    if not authors:
        return "Unknown"
    
    first_author = authors[0]
    
    # Handle "LastName, FirstName" format
    if ',' in first_author:
        return first_author.split(',')[0].strip()
    
    # Handle "FirstName LastName" format
    parts = first_author.split()
    return parts[-1] if parts else "Unknown"


def create_cache_key(file_path: str, options: ProcessingOptions) -> str:
    """
    Create cache key from file path and processing options
    
    Args:
        file_path: Path to PDF file
        options: Processing options
        
    Returns:
        MD5 hash as cache key
    """
    # Get file modification time for cache invalidation
    try:
        mtime = Path(file_path).stat().st_mtime
    except (OSError, FileNotFoundError):
        mtime = 0
    
    # Create key from file path, options, and modification time
    key_data = f"{file_path}:{options.focus.value}:{options.depth.value}:{mtime}"
    
    return hashlib.md5(key_data.encode()).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_pdf_path(file_path: str) -> bool:
    """
    Validate if path points to a PDF file
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if valid PDF path
    """
    path = Path(file_path)
    
    # Check if file exists
    if not path.exists():
        return False
    
    # Check if it's a file (not directory)
    if not path.is_file():
        return False
    
    # Check file extension
    if path.suffix.lower() != '.pdf':
        return False
    
    return True


def get_pdf_files_in_directory(directory_path: str) -> List[Path]:
    """
    Get all PDF files in directory
    
    Args:
        directory_path: Directory to search
        
    Returns:
        List of PDF file paths
    """
    directory = Path(directory_path)
    
    if not directory.exists() or not directory.is_dir():
        return []
    
    pdf_files = []
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == '.pdf':
            pdf_files.append(file_path)
    
    return sorted(pdf_files)


def format_metadata_for_citation(metadata: PaperMetadata) -> str:
    """
    Format metadata for citation display
    
    Args:
        metadata: Paper metadata
        
    Returns:
        Formatted citation string
    """
    citation_parts = []
    
    # Authors
    if metadata.authors:
        if len(metadata.authors) == 1:
            citation_parts.append(metadata.authors[0])
        elif len(metadata.authors) == 2:
            citation_parts.append(f"{metadata.authors[0]} and {metadata.authors[1]}")
        else:
            citation_parts.append(f"{metadata.authors[0]} et al.")
    
    # Year
    if metadata.year:
        citation_parts.append(f"({metadata.year})")
    
    # Title
    if metadata.title:
        citation_parts.append(f'"{metadata.title}"')
    
    # Journal
    if metadata.journal:
        journal_info = metadata.journal
        if metadata.volume:
            journal_info += f", {metadata.volume}"
        if metadata.issue:
            journal_info += f"({metadata.issue})"
        if metadata.pages:
            journal_info += f", {metadata.pages}"
        citation_parts.append(journal_info)
    
    return ". ".join(citation_parts)


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        ISO formatted timestamp
    """
    return datetime.now().isoformat()


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def ensure_directory(directory_path: str) -> None:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory_path: Path to directory
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)