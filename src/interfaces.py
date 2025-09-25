"""
Core interfaces for ScholarSquill Kiro MCP Server components
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    from .models import (
        PaperMetadata, ProcessingOptions, NoteContent, AnalysisResult, 
        CommandArgs, NoteTemplate
    )
except ImportError:
    from models import (
        PaperMetadata, ProcessingOptions, NoteContent, AnalysisResult, 
        CommandArgs, NoteTemplate
    )


class PDFProcessorInterface(ABC):
    """Interface for PDF processing components"""
    
    @abstractmethod
    def extract_text(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        pass
    
    @abstractmethod
    def extract_metadata(self, pdf_path: str) -> PaperMetadata:
        """Extract metadata from PDF file"""
        pass
    
    @abstractmethod
    def get_page_count(self, pdf_path: str) -> int:
        """Get number of pages in PDF"""
        pass
    
    @abstractmethod
    def validate_pdf(self, pdf_path: str) -> bool:
        """Validate if file is a readable PDF"""
        pass
    
    @abstractmethod
    def generate_citekey(self, metadata: PaperMetadata) -> str:
        """Generate citation key from metadata"""
        pass


class ContentAnalyzerInterface(ABC):
    """Interface for content analysis components"""
    
    @abstractmethod
    def analyze_content(self, text: str, focus: str) -> AnalysisResult:
        """Analyze paper content based on focus"""
        pass
    
    @abstractmethod
    def classify_paper_type(self, text: str) -> Tuple[str, float]:
        """Classify paper type with confidence score"""
        pass
    
    @abstractmethod
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract paper sections"""
        pass
    
    @abstractmethod
    def extract_key_concepts(self, text: str, focus: str) -> List[str]:
        """Extract key concepts based on focus"""
        pass


class NoteGeneratorInterface(ABC):
    """Interface for note generation components"""
    
    @abstractmethod
    def generate_note(self, content: str, metadata: PaperMetadata, 
                     focus: str, depth: str) -> str:
        """Generate structured note from content"""
        pass
    
    @abstractmethod
    def apply_template(self, template_name: str, content: Dict) -> str:
        """Apply template to content"""
        pass
    
    @abstractmethod
    def format_citations(self, metadata: PaperMetadata) -> str:
        """Format citation information"""
        pass


class TemplateProcessorInterface(ABC):
    """Interface for template processing components"""
    
    @abstractmethod
    def load_template(self, template_name: str) -> NoteTemplate:
        """Load template by name"""
        pass
    
    @abstractmethod
    def render_template(self, template: NoteTemplate, data: Dict) -> str:
        """Render template with data"""
        pass
    
    @abstractmethod
    def list_available_templates(self) -> List[str]:
        """List all available template names"""
        pass
    
    @abstractmethod
    def select_template(self, focus_type, paper_classification=None, analysis_result=None) -> str:
        """Select appropriate template based on focus and classification"""
        pass
    
    @abstractmethod
    def render_template_with_dynamic_content(self, template, data, depth_type=None, analysis_result=None) -> str:
        """Render template with dynamic content inclusion"""
        pass


class CommandParserInterface(ABC):
    """Interface for command parsing components"""
    
    @abstractmethod
    def parse_command(self, command: str) -> CommandArgs:
        """Parse command string into arguments"""
        pass
    
    @abstractmethod
    def validate_arguments(self, args: CommandArgs) -> bool:
        """Validate parsed arguments"""
        pass


class BatchProcessorInterface(ABC):
    """Interface for batch processing components"""
    
    @abstractmethod
    def process_directory(self, directory_path: str, options: ProcessingOptions) -> List[Dict]:
        """Process all PDFs in directory"""
        pass
    
    @abstractmethod
    def get_pdf_files(self, directory_path: str) -> List[Path]:
        """Get list of PDF files in directory"""
        pass


class FileWriterInterface(ABC):
    """Interface for file writing components"""
    
    @abstractmethod
    def write_note(self, content: str, output_path: str) -> str:
        """Write note content to file"""
        pass
    
    @abstractmethod
    def generate_filename(self, metadata: PaperMetadata, format_type: str) -> str:
        """Generate safe filename from metadata"""
        pass
    
    @abstractmethod
    def ensure_output_directory(self, directory_path: str) -> bool:
        """Ensure output directory exists"""
        pass


class CacheInterface(ABC):
    """Interface for caching components"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Dict]:
        """Get cached data by key"""
        pass
    
    @abstractmethod
    def set(self, key: str, data: Dict, ttl_seconds: Optional[int] = None) -> None:
        """Set cached data with optional TTL"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached data"""
        pass
    
    @abstractmethod
    def generate_cache_key(self, file_path: str, options: ProcessingOptions) -> str:
        """Generate cache key for file and options"""
        pass


class LoggerInterface(ABC):
    """Interface for logging components"""
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        pass