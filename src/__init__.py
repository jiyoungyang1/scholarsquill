"""
ScholarSquill Kiro MCP Server

A Model Context Protocol server for processing scientific PDF papers
into structured markdown literature notes.
"""

__version__ = "0.1.0"
__author__ = "ScholarSquill Team"
__email__ = "team@scholarsquill.com"
__license__ = "MIT"

# Main components
from .server import ScholarsQuillKiroServer
from .config import ServerConfig, ProcessingConfig, TemplateConfig
from .models import (
    PaperMetadata,
    ProcessingOptions,
    NoteContent,
    FocusType,
    DepthType,
    FormatType,
)

__all__ = [
    "ScholarsQuillKiroServer",
    "ServerConfig",
    "ProcessingConfig", 
    "TemplateConfig",
    "PaperMetadata",
    "ProcessingOptions",
    "NoteContent",
    "FocusType",
    "DepthType",
    "FormatType",
]