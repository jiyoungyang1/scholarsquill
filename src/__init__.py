"""
ScholarsQuill MCP Server

A Model Context Protocol server for processing scientific PDF papers
into structured markdown literature notes.
"""

__version__ = "0.1.0"
__author__ = "ScholarsQuill Team"
__email__ = "team@scholarsquill.com"
__license__ = "MIT"

# Main components
from .legacy_mcp_server.server import ScholarsQuillServer
from .legacy_mcp_server.config import ServerConfig, ProcessingConfig, TemplateConfig
from .models import (
    PaperMetadata,
    ProcessingOptions,
    NoteContent,
    FocusType,
    DepthType,
    FormatType,
)

__all__ = [
    "ScholarsQuillServer",
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