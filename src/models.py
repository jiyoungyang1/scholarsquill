"""
Core data models for ScholarSquill MCP Server
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class FocusType(Enum):
    """Focus types for note generation"""
    RESEARCH = "research"
    THEORY = "theory"
    REVIEW = "review"
    METHOD = "method"
    BALANCED = "balanced"


class DepthType(Enum):
    """Depth levels for analysis"""
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class FormatType(Enum):
    """Output format types"""
    MARKDOWN = "markdown"


class CodelangFocusType(Enum):
    """Focus types for discourse analysis"""
    DISCOURSE = "discourse"
    ARCHITECTURE = "architecture"
    TERMINOLOGY = "terminology"
    RHETORIC = "rhetoric"
    SECTIONS = "sections"
    FUNCTIONS = "functions"
    SUMMARY = "summary"


class SectionFilterType(Enum):
    """Section filter types for analysis"""
    ALL = "all"
    INTRODUCTION = "introduction"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"


@dataclass
class PaperMetadata:
    """Metadata extracted from PDF papers"""
    title: str
    first_author: str
    authors: List[str]
    year: Optional[int] = None
    citekey: str = ""
    item_type: str = "journalArticle"
    journal: str = ""
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    page_count: int = 0
    file_path: str = ""


@dataclass
class ProcessingOptions:
    """Options for processing papers"""
    focus: FocusType = FocusType.BALANCED
    depth: DepthType = DepthType.STANDARD
    format: FormatType = FormatType.MARKDOWN
    batch: bool = False
    minireview: bool = False
    topic: Optional[str] = None
    output_dir: Optional[str] = None


@dataclass
class NoteContent:
    """Generated note content structure"""
    title: str
    citation: str
    sections: Dict[str, str]
    metadata: PaperMetadata
    generated_at: datetime
    processing_options: ProcessingOptions


@dataclass
class AnalysisResult:
    """Result of content analysis"""
    paper_type: str
    confidence: float
    sections: Dict[str, str]
    key_concepts: List[str]
    equations: List[str] = field(default_factory=list)
    methodologies: List[str] = field(default_factory=list)


@dataclass
class CommandArgs:
    """Parsed command arguments"""
    target: str
    focus: FocusType = FocusType.BALANCED
    depth: DepthType = DepthType.STANDARD
    format: FormatType = FormatType.MARKDOWN
    batch: bool = False
    minireview: bool = False
    topic: Optional[str] = None
    output_dir: Optional[str] = None


@dataclass
class NoteTemplate:
    """Template structure for note generation"""
    name: str
    description: str
    sections: List['TemplateSection']
    focus_areas: List[FocusType]


@dataclass
class TemplateSection:
    """Individual section within a template"""
    title: str
    description: str
    required: bool = True
    content_type: str = "text"  # text, list, equation, citation


@dataclass
class CodelangArgs:
    """Parsed arguments for codelang discourse analysis"""
    target: str
    field: str = "auto-detect"
    focus: CodelangFocusType = CodelangFocusType.DISCOURSE
    section_filter: SectionFilterType = SectionFilterType.ALL
    depth: DepthType = DepthType.STANDARD
    batch: bool = False
    keyword: Optional[str] = None
    output_dir: Optional[str] = None


@dataclass
class DiscoursePattern:
    """Represents a discovered discourse pattern"""
    expression: str
    function: str
    context: str
    frequency: int = 1
    section: Optional[str] = None
    pattern_type: Optional[str] = None


@dataclass
class LinguisticFunction:
    """Represents a discovered linguistic function"""
    function_name: str
    expressions: List[str]
    description: str
    frequency: int = 0


@dataclass
class CodelangAnalysis:
    """Results of discourse pattern analysis"""
    paper_metadata: PaperMetadata
    focus: CodelangFocusType
    field: str
    discourse_patterns: List[DiscoursePattern] = field(default_factory=list)
    linguistic_functions: List[LinguisticFunction] = field(default_factory=list)
    argument_structure: Optional[str] = None
    primary_strategy: Optional[str] = None
    field_conventions: Optional[str] = None
    writing_insights: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class BatchCodelangAnalysis:
    """Results of batch discourse pattern analysis"""
    papers: List[PaperMetadata]
    focus: CodelangFocusType
    field: str
    keyword: Optional[str] = None
    combined_patterns: List[DiscoursePattern] = field(default_factory=list)
    cross_paper_functions: List[LinguisticFunction] = field(default_factory=list)
    comparative_analysis: Optional[str] = None
    pattern_frequency: Dict[str, int] = field(default_factory=dict)
    field_variations: Dict[str, str] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CitationContext:
    """Context and details for a single citation"""
    id: int
    citation: str  # The actual citation text (e.g., "Smith 2020", "[1]")
    context: str  # Full context sentence or paragraph
    sentence: str  # Specific sentence containing the citation
    purpose: str  # Purpose of citation (supporting_evidence, contrasting_view, etc.)
    section: str  # Section of paper where citation appears
    position: int  # Character position in text
    surrounding_context: str  # Extended context around citation


@dataclass
class ReferenceNetwork:
    """Network representation of references and their relationships"""
    nodes: List[Dict[str, any]] = field(default_factory=list)  # Reference nodes
    edges: List[Dict[str, any]] = field(default_factory=list)  # Citation relationships
    clusters: Dict[str, List[str]] = field(default_factory=dict)  # Purpose-based clusters