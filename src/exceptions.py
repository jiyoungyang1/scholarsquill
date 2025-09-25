"""
Exception classes and error handling for ScholarSquill Kiro MCP Server
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ErrorType(Enum):
    """Types of errors that can occur"""
    FILE_ERROR = "file_error"
    PROCESSING_ERROR = "processing_error"
    TEMPLATE_ERROR = "template_error"
    MCP_ERROR = "mcp_error"
    VALIDATION_ERROR = "validation_error"
    CONFIGURATION_ERROR = "configuration_error"


class ErrorCode(Enum):
    """Specific error codes"""
    # File errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_UNREADABLE = "FILE_UNREADABLE"
    FILE_CORRUPTED = "FILE_CORRUPTED"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_PDF = "INVALID_PDF"
    FILE_EXISTS = "FILE_EXISTS"
    FILE_ERROR = "FILE_ERROR"
    
    # Processing errors
    TEXT_EXTRACTION_FAILED = "TEXT_EXTRACTION_FAILED"
    METADATA_EXTRACTION_FAILED = "METADATA_EXTRACTION_FAILED"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"
    CONTENT_TOO_LARGE = "CONTENT_TOO_LARGE"
    PROCESSING_TIMEOUT = "PROCESSING_TIMEOUT"
    
    # Template errors
    TEMPLATE_NOT_FOUND = "TEMPLATE_NOT_FOUND"
    TEMPLATE_INVALID = "TEMPLATE_INVALID"
    TEMPLATE_RENDER_FAILED = "TEMPLATE_RENDER_FAILED"
    
    # MCP errors
    INVALID_TOOL_CALL = "INVALID_TOOL_CALL"
    INVALID_ARGUMENTS = "INVALID_ARGUMENTS"
    TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED"
    
    # Validation errors
    INVALID_FOCUS = "INVALID_FOCUS"
    INVALID_DEPTH = "INVALID_DEPTH"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_PATH = "INVALID_PATH"
    
    # Configuration errors
    INVALID_CONFIG = "INVALID_CONFIG"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"


@dataclass
class ErrorResponse:
    """Structured error response"""
    error_type: ErrorType
    error_message: str
    error_code: ErrorCode
    success: bool = False
    suggestions: List[str] = field(default_factory=list)
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response"""
        return {
            "success": self.success,
            "error": {
                "type": self.error_type.value,
                "message": self.error_message,
                "code": self.error_code.value,
                "suggestions": self.suggestions,
                "details": self.details or {}
            }
        }


class ScholarSquillError(Exception):
    """Base exception for ScholarSquill errors"""
    
    def __init__(self, message: str, error_type: ErrorType, error_code: ErrorCode, 
                 suggestions: Optional[List[str]] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.error_code = error_code
        self.suggestions = suggestions or []
        self.details = details or {}
    
    def to_error_response(self) -> ErrorResponse:
        """Convert to ErrorResponse"""
        return ErrorResponse(
            error_type=self.error_type,
            error_message=self.message,
            error_code=self.error_code,
            suggestions=self.suggestions,
            details=self.details
        )


class FileError(ScholarSquillError):
    """File-related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, file_path: Optional[str] = None,
                 suggestions: Optional[List[str]] = None):
        details = {"file_path": file_path} if file_path else None
        super().__init__(message, ErrorType.FILE_ERROR, error_code, suggestions, details)


class ProcessingError(ScholarSquillError):
    """Processing-related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, 
                 suggestions: Optional[List[str]] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorType.PROCESSING_ERROR, error_code, suggestions, details)


class TemplateError(ScholarSquillError):
    """Template-related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, template_name: Optional[str] = None,
                 suggestions: Optional[List[str]] = None):
        details = {"template_name": template_name} if template_name else None
        super().__init__(message, ErrorType.TEMPLATE_ERROR, error_code, suggestions, details)


class MCPError(ScholarSquillError):
    """MCP protocol-related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, tool_name: Optional[str] = None,
                 suggestions: Optional[List[str]] = None):
        details = {"tool_name": tool_name} if tool_name else None
        super().__init__(message, ErrorType.MCP_ERROR, error_code, suggestions, details)


class ValidationError(ScholarSquillError):
    """Validation-related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, field_name: Optional[str] = None,
                 suggestions: Optional[List[str]] = None):
        details = {"field_name": field_name} if field_name else None
        super().__init__(message, ErrorType.VALIDATION_ERROR, error_code, suggestions, details)


class ConfigurationError(ScholarSquillError):
    """Configuration-related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, config_key: Optional[str] = None,
                 suggestions: Optional[List[str]] = None):
        details = {"config_key": config_key} if config_key else None
        super().__init__(message, ErrorType.CONFIGURATION_ERROR, error_code, suggestions, details)


class NoteGenerationError(ScholarSquillError):
    """Note generation-related errors"""
    
    def __init__(self, message: str, error_code: Optional[ErrorCode] = None, 
                 suggestions: Optional[List[str]] = None, details: Optional[Dict[str, Any]] = None):
        error_code = error_code or ErrorCode.PROCESSING_TIMEOUT
        super().__init__(message, ErrorType.PROCESSING_ERROR, error_code, suggestions, details)


def create_file_not_found_error(file_path: str) -> FileError:
    """Create a file not found error with helpful suggestions"""
    return FileError(
        message=f"PDF file not found: {file_path}",
        error_code=ErrorCode.FILE_NOT_FOUND,
        file_path=file_path,
        suggestions=[
            "Check if the file path is correct",
            "Ensure the file exists and is accessible",
            "Try using an absolute path instead of relative path"
        ]
    )


def create_invalid_pdf_error(file_path: str) -> FileError:
    """Create an invalid PDF error with helpful suggestions"""
    return FileError(
        message=f"Invalid or corrupted PDF file: {file_path}",
        error_code=ErrorCode.INVALID_PDF,
        file_path=file_path,
        suggestions=[
            "Ensure the file is a valid PDF",
            "Try opening the PDF in a PDF viewer to verify it's not corrupted",
            "Check if the file is password-protected"
        ]
    )


def create_processing_timeout_error(timeout_seconds: int) -> ProcessingError:
    """Create a processing timeout error"""
    return ProcessingError(
        message=f"Processing timed out after {timeout_seconds} seconds",
        error_code=ErrorCode.PROCESSING_TIMEOUT,
        suggestions=[
            "Try processing a smaller file",
            "Increase the timeout setting",
            "Use quick depth for faster processing"
        ]
    )


def create_template_not_found_error(template_name: str) -> TemplateError:
    """Create a template not found error"""
    return TemplateError(
        message=f"Template not found: {template_name}",
        error_code=ErrorCode.TEMPLATE_NOT_FOUND,
        template_name=template_name,
        suggestions=[
            "Check available templates",
            "Ensure template files are in the templates directory",
            "Use a different focus type"
        ]
    )


# Additional exception classes for compatibility
class PDFProcessingError(ProcessingError):
    """PDF processing specific errors"""
    pass


class ContentAnalysisError(ProcessingError):
    """Content analysis specific errors"""
    pass


class CommandParsingError(ValidationError):
    """Command parsing specific errors"""
    pass


class BatchProcessingError(ProcessingError):
    """Batch processing specific errors"""
    pass