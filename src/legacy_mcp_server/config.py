"""
Configuration classes for ScholarsQuill MCP Server
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ServerConfig:
    """Main server configuration"""
    default_output_dir: str = "literature-notes"
    default_codelang_output_dir: str = "codelang-analysis"
    default_templates_dir: str = "templates"
    max_file_size_mb: int = 50
    batch_size_limit: int = 100
    enable_caching: bool = True
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Create configuration from environment variables"""
        return cls(
            default_output_dir=os.getenv('SQ_OUTPUT_DIR', cls.default_output_dir),
            default_codelang_output_dir=os.getenv('SQ_CODELANG_OUTPUT_DIR', cls.default_codelang_output_dir),
            default_templates_dir=os.getenv('SQ_TEMPLATES_DIR', cls.default_templates_dir),
            max_file_size_mb=int(os.getenv('SQ_MAX_FILE_SIZE_MB', str(cls.max_file_size_mb))),
            batch_size_limit=int(os.getenv('SQ_BATCH_SIZE_LIMIT', str(cls.batch_size_limit))),
            enable_caching=os.getenv('SQ_ENABLE_CACHING', 'true').lower() == 'true',
            log_level=os.getenv('SQ_LOG_LEVEL', cls.log_level)
        )
    
    def validate(self) -> bool:
        """Validate configuration values"""
        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")
        if self.batch_size_limit <= 0:
            raise ValueError("batch_size_limit must be positive")
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError("Invalid log_level")
        return True


@dataclass
class ProcessingConfig:
    """Configuration for PDF processing"""
    pdf_timeout_seconds: int = 30
    max_text_length: int = 1000000  # 1MB of text
    enable_ocr: bool = False
    ocr_language: str = "eng"
    
    @classmethod
    def from_env(cls) -> 'ProcessingConfig':
        """Create processing configuration from environment variables"""
        return cls(
            pdf_timeout_seconds=int(os.getenv('SQ_PDF_TIMEOUT', str(cls.pdf_timeout_seconds))),
            max_text_length=int(os.getenv('SQ_MAX_TEXT_LENGTH', str(cls.max_text_length))),
            enable_ocr=os.getenv('SQ_ENABLE_OCR', 'false').lower() == 'true',
            ocr_language=os.getenv('SQ_OCR_LANGUAGE', cls.ocr_language)
        )


@dataclass
class TemplateConfig:
    """Configuration for template processing"""
    template_cache_size: int = 50
    custom_templates_dir: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'TemplateConfig':
        """Create template configuration from environment variables"""
        return cls(
            template_cache_size=int(os.getenv('SQ_TEMPLATE_CACHE_SIZE', str(cls.template_cache_size))),
            custom_templates_dir=os.getenv('SQ_CUSTOM_TEMPLATES_DIR')
        )


class ConfigManager:
    """Manages all configuration aspects"""
    
    def __init__(self):
        self.server = ServerConfig.from_env()
        self.processing = ProcessingConfig.from_env()
        self.template = TemplateConfig.from_env()
        
        # Validate all configurations
        self.server.validate()
    
    def get_templates_dir(self) -> Path:
        """Get the templates directory path"""
        if self.template.custom_templates_dir:
            return Path(self.template.custom_templates_dir)
        return Path(__file__).parent.parent / self.server.default_templates_dir
    
    def get_output_dir(self, custom_dir: Optional[str] = None) -> Path:
        """Get the output directory path"""
        if custom_dir:
            return Path(custom_dir)
        return Path(self.server.default_output_dir)
    
    def is_file_size_valid(self, file_path: str) -> bool:
        """Check if file size is within limits"""
        try:
            file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            return file_size_mb <= self.server.max_file_size_mb
        except (OSError, FileNotFoundError):
            return False