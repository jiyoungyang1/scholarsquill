"""
Command parsing for ScholarsQuill MCP Server
"""

import re
import shlex
from typing import Dict, List, Optional, Union
from pathlib import Path

from .interfaces import CommandParserInterface
from .models import CommandArgs, FocusType, DepthType, FormatType
from .exceptions import ValidationError, ErrorCode


class CommandParser(CommandParserInterface):
    """Command parser for /sq:note commands"""
    
    def __init__(self):
        """Initialize command parser"""
        self._focus_aliases = {
            'r': FocusType.RESEARCH,
            'research': FocusType.RESEARCH,
            't': FocusType.THEORY,
            'theory': FocusType.THEORY,
            'rev': FocusType.REVIEW,
            'review': FocusType.REVIEW,
            'm': FocusType.METHOD,
            'method': FocusType.METHOD,
            'methodology': FocusType.METHOD,
            'b': FocusType.BALANCED,
            'balanced': FocusType.BALANCED,
        }
        
        self._depth_aliases = {
            'q': DepthType.QUICK,
            'quick': DepthType.QUICK,
            'fast': DepthType.QUICK,
            's': DepthType.STANDARD,
            'standard': DepthType.STANDARD,
            'normal': DepthType.STANDARD,
            'd': DepthType.DEEP,
            'deep': DepthType.DEEP,
            'detailed': DepthType.DEEP,
            'comprehensive': DepthType.DEEP,
        }
        
        self._format_aliases = {
            'md': FormatType.MARKDOWN,
            'markdown': FormatType.MARKDOWN,
        }
    
    def parse_command(self, command: str) -> CommandArgs:
        """
        Parse command string into CommandArgs
        
        Expected format: /sq:note [target] [--focus type] [--depth level] [--format type] [--batch] [--output-dir path]
        
        Args:
            command: Command string to parse
            
        Returns:
            CommandArgs: Parsed command arguments
            
        Raises:
            ValidationError: If command format is invalid
        """
        # Remove the command prefix if present
        if command.startswith('/sq:note'):
            command = command[8:].strip()
        elif command.startswith('sq:note'):
            command = command[7:].strip()
        
        if not command:
            raise ValidationError(
                "Target file or directory is required",
                ErrorCode.INVALID_ARGUMENTS,
                field_name="target",
                suggestions=[
                    "Provide a PDF file path or directory path",
                    "Example: /sq:note paper.pdf --focus research",
                    "Example: /sq:note ./papers/ --batch"
                ]
            )
        
        try:
            # Use shlex to properly handle quoted arguments
            tokens = shlex.split(command)
        except ValueError as e:
            raise ValidationError(
                f"Invalid command syntax: {e}",
                ErrorCode.INVALID_ARGUMENTS,
                suggestions=[
                    "Check for unmatched quotes",
                    "Use proper shell escaping for special characters"
                ]
            )
        
        if not tokens:
            raise ValidationError(
                "Target file or directory is required",
                ErrorCode.INVALID_ARGUMENTS,
                field_name="target"
            )
        
        # First token is always the target
        target = tokens[0]
        
        # Parse options
        args = CommandArgs(target=target)
        i = 1
        
        while i < len(tokens):
            token = tokens[i]
            
            if token.startswith('--'):
                option = token[2:]
                
                if option == 'focus':
                    i += 1
                    if i >= len(tokens):
                        raise ValidationError(
                            "--focus requires a value",
                            ErrorCode.INVALID_ARGUMENTS,
                            field_name="focus",
                            suggestions=list(self._focus_aliases.keys())
                        )
                    args.focus = self._parse_focus(tokens[i])
                
                elif option == 'depth':
                    i += 1
                    if i >= len(tokens):
                        raise ValidationError(
                            "--depth requires a value",
                            ErrorCode.INVALID_ARGUMENTS,
                            field_name="depth",
                            suggestions=list(self._depth_aliases.keys())
                        )
                    args.depth = self._parse_depth(tokens[i])
                
                elif option == 'format':
                    i += 1
                    if i >= len(tokens):
                        raise ValidationError(
                            "--format requires a value",
                            ErrorCode.INVALID_ARGUMENTS,
                            field_name="format",
                            suggestions=list(self._format_aliases.keys())
                        )
                    args.format = self._parse_format(tokens[i])
                
                elif option == 'batch':
                    args.batch = True
                
                elif option == 'minireview':
                    args.minireview = True
                
                elif option == 'topic':
                    i += 1
                    if i >= len(tokens):
                        raise ValidationError(
                            "--topic requires a topic description",
                            ErrorCode.INVALID_ARGUMENTS,
                            field_name="topic",
                            suggestions=[
                                "Provide a topic description",
                                "Example: --topic \"Kirkwood-Buff finite size correction\"",
                                "Example: --topic \"protein folding mechanisms\""
                            ]
                        )
                    args.topic = tokens[i]
                
                elif option in ['output-dir', 'output']:
                    i += 1
                    if i >= len(tokens):
                        raise ValidationError(
                            "--output-dir requires a path",
                            ErrorCode.INVALID_ARGUMENTS,
                            field_name="output_dir",
                            suggestions=[
                                "Provide a directory path",
                                "Example: --output-dir ./notes/"
                            ]
                        )
                    args.output_dir = tokens[i]
                
                else:
                    raise ValidationError(
                        f"Unknown option: --{option}",
                        ErrorCode.INVALID_ARGUMENTS,
                        field_name=option,
                        suggestions=[
                            "Valid options: --focus, --depth, --format, --batch, --minireview, --topic, --output-dir",
                            "Use --help for more information"
                        ]
                    )
            
            elif token.startswith('-') and len(token) > 1:
                # Handle short options
                for char in token[1:]:
                    if char == 'b':
                        args.batch = True
                    else:
                        raise ValidationError(
                            f"Unknown short option: -{char}",
                            ErrorCode.INVALID_ARGUMENTS,
                            suggestions=[
                                "Valid short options: -b (batch)",
                                "Use long options for clarity"
                            ]
                        )
            
            else:
                raise ValidationError(
                    f"Unexpected argument: {token}",
                    ErrorCode.INVALID_ARGUMENTS,
                    suggestions=[
                        "Options must start with -- or -",
                        "Check command syntax"
                    ]
                )
            
            i += 1
        
        return args
    
    def validate_arguments(self, args: CommandArgs) -> bool:
        """
        Validate parsed arguments
        
        Args:
            args: CommandArgs to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            ValidationError: If arguments are invalid
        """
        # Check for conflicting modes
        if args.batch and args.minireview:
            raise ValidationError(
                "Cannot use both --batch and --minireview options together",
                ErrorCode.INVALID_ARGUMENTS,
                suggestions=[
                    "Use --batch for individual notes from multiple papers",
                    "Use --minireview for one comprehensive review of multiple papers",
                    "Choose one processing mode"
                ]
            )
        
        # Validate minireview mode requirements
        if args.minireview and not args.topic:
            raise ValidationError(
                "--minireview requires a --topic to focus the analysis",
                ErrorCode.INVALID_ARGUMENTS,
                field_name="topic",
                suggestions=[
                    "Provide a topic with --topic \"your topic here\"",
                    "Example: --topic \"Kirkwood-Buff finite size correction\"",
                    "Example: --topic \"protein folding mechanisms\""
                ]
            )
        
        # Validate target (can be path or citekey)
        resolved_target = self._resolve_target(args.target, args.batch or args.minireview)
        args.target = resolved_target  # Update target with resolved path
        
        target_path = Path(resolved_target)
        
        if args.batch or args.minireview:
            # For batch processing and minireview, target should be a directory
            mode_name = "minireview" if args.minireview else "batch processing"
            if not target_path.exists():
                raise ValidationError(
                    f"Directory not found: {args.target}",
                    ErrorCode.INVALID_PATH,
                    field_name="target",
                    suggestions=[
                        "Ensure the directory exists",
                        "Use absolute path if needed",
                        "Check directory permissions"
                    ]
                )
            
            if not target_path.is_dir():
                flag_name = "--minireview" if args.minireview else "--batch"
                raise ValidationError(
                    f"{mode_name.title()} requires a directory, not a file: {args.target}",
                    ErrorCode.INVALID_PATH,
                    field_name="target",
                    suggestions=[
                        f"Remove {flag_name} flag to process single file",
                        f"Provide a directory path for {mode_name}"
                    ]
                )
        
        else:
            # For single file processing, target should be a PDF file
            if not target_path.exists():
                raise ValidationError(
                    f"File not found: {args.target}",
                    ErrorCode.INVALID_PATH,
                    field_name="target",
                    suggestions=[
                        "Check if the file path is correct",
                        "Ensure the file exists and is accessible",
                        "Use absolute path if needed"
                    ]
                )
            
            if not target_path.is_file():
                raise ValidationError(
                    f"Target must be a file, not a directory: {args.target}",
                    ErrorCode.INVALID_PATH,
                    field_name="target",
                    suggestions=[
                        "Add --batch flag to process directory",
                        "Specify a PDF file path"
                    ]
                )
            
            # Check if it's a PDF file
            if target_path.suffix.lower() != '.pdf':
                raise ValidationError(
                    f"Target must be a PDF file: {args.target}",
                    ErrorCode.INVALID_PATH,
                    field_name="target",
                    suggestions=[
                        "Ensure the file has .pdf extension",
                        "Convert the file to PDF format if needed"
                    ]
                )
        
        # Validate output directory if specified
        if args.output_dir:
            output_path = Path(args.output_dir)
            if output_path.exists() and not output_path.is_dir():
                raise ValidationError(
                    f"Output path must be a directory: {args.output_dir}",
                    ErrorCode.INVALID_PATH,
                    field_name="output_dir",
                    suggestions=[
                        "Specify a directory path",
                        "Remove existing file at that path"
                    ]
                )
        
        return True
    
    def _resolve_target(self, target: str, is_batch_mode: bool = False) -> str:
        """
        Resolve target which can be:
        1. File path (e.g., paper.pdf)
        2. Directory path (e.g., ./papers/)
        3. Single citekey (e.g., yang2024multi)
        4. Comma-separated citekeys (e.g., yang2024multi,smith2023data)
        
        Args:
            target: Target string to resolve
            is_batch_mode: Whether this is for batch/minireview mode
            
        Returns:
            str: Resolved path to file or directory
            
        Raises:
            ValidationError: If target cannot be resolved
        """
        target_path = Path(target)
        
        # If it's already a valid path, return as-is
        if target_path.exists():
            return target
        
        # Check if target looks like citekey(s)
        if self._looks_like_citekey(target):
            return self._resolve_citekey_target(target, is_batch_mode)
        
        # If not a valid path and not a citekey, return original (will fail in validation)
        return target
    
    def _looks_like_citekey(self, target: str) -> bool:
        """
        Check if target looks like citekey(s) rather than a file path
        
        Args:
            target: Target string to check
            
        Returns:
            bool: True if target appears to be citekey(s)
        """
        # Remove any commas and check each component
        parts = [part.strip() for part in target.split(',')]
        
        for part in parts:
            # Citekey pattern: usually author + year + keyword (no spaces, no file extensions)
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]{2,}$', part):
                return False
            
            # Should not have file extensions
            if part.lower().endswith(('.pdf', '.txt', '.md')):
                return False
            
            # Should not have path separators
            if '/' in part or '\\' in part:
                return False
        
        return True
    
    def _resolve_citekey_target(self, citekeys: str, is_batch_mode: bool) -> str:
        """
        Resolve citekey(s) to actual file path(s)
        
        Args:
            citekeys: Comma-separated citekeys to resolve
            is_batch_mode: Whether this is for batch/minireview mode
            
        Returns:
            str: Resolved path
            
        Raises:
            ValidationError: If citekeys cannot be resolved
        """
        import os
        
        # Get citekey list
        citekey_list = [ck.strip() for ck in citekeys.split(',')]
        
        # Search in common directories for PDF files
        search_dirs = [
            Path.cwd(),  # Current directory
            Path.cwd() / "papers",
            Path.cwd() / "pdfs", 
            Path.cwd() / "literature",
            Path.cwd() / "docs",
            Path.cwd() / "tests" / "examples" / "papers",  # Test directory
        ]
        
        found_files = []
        
        for citekey in citekey_list:
            # Extract components from citekey (e.g., yang2024multi -> yang, 2024, multi)
            components = self._extract_citekey_components(citekey)
            
            # Find matching PDF files
            matching_files = self._find_matching_pdfs(components, search_dirs)
            
            if not matching_files:
                raise ValidationError(
                    f"No PDF files found matching citekey: {citekey}",
                    ErrorCode.INVALID_PATH,
                    field_name="target",
                    suggestions=[
                        f"Check if PDF file exists with components: {', '.join(components)}",
                        "Ensure PDF filename contains author, year, and keywords",
                        "Use direct file path instead of citekey",
                        f"Example: author_year_keyword.pdf for citekey {citekey}"
                    ]
                )
            
            # If multiple matches, pick the most likely one
            if len(matching_files) > 1:
                # Sort by match score (number of components matched)
                best_match = max(matching_files, key=lambda x: x[1])
                found_files.append(best_match[0])
            else:
                found_files.append(matching_files[0][0])
        
        # Return result based on mode
        if is_batch_mode:
            if len(found_files) == 1:
                # Single file for batch - return its parent directory
                return str(found_files[0].parent)
            else:
                # Multiple files for batch - create temporary directory or return common parent
                common_parent = self._find_common_parent(found_files)
                if common_parent:
                    return str(common_parent)
                else:
                    raise ValidationError(
                        "Multiple citekeys found in different directories - cannot determine target directory for batch mode",
                        ErrorCode.INVALID_PATH,
                        field_name="target",
                        suggestions=[
                            "Use a directory path instead",
                            "Ensure all papers are in the same directory for batch processing"
                        ]
                    )
        else:
            # Single file mode
            if len(found_files) > 1:
                raise ValidationError(
                    f"Multiple citekeys provided but not in batch mode: {citekeys}",
                    ErrorCode.INVALID_ARGUMENTS,
                    field_name="target", 
                    suggestions=[
                        "Use --batch flag for multiple papers",
                        "Provide only one citekey for single file processing"
                    ]
                )
            return str(found_files[0])
    
    def _extract_citekey_components(self, citekey: str) -> List[str]:
        """
        Extract searchable components from citekey
        Expected format: lastname + year + firstwordoftitle
        
        Args:
            citekey: Citekey like 'fukuda2014thermodynamic' or 'yang2024multi'
            
        Returns:
            List[str]: Components like ['fukuda', '2014', 'thermodynamic']
        """
        components = []
        
        # Extract year (4-digit number)
        year_match = re.search(r'(19|20)\d{2}', citekey)
        if year_match:
            year = year_match.group()
            components.append(year)
            
            # Split citekey into parts before and after year
            before_year = citekey[:year_match.start()].lower()
            after_year = citekey[year_match.end():].lower()
            
            # Before year should be lastname
            if before_year:
                # Clean and add lastname
                lastname = re.sub(r'[^a-zA-Z]', '', before_year)
                if len(lastname) >= 2:
                    components.insert(0, lastname)  # Insert at beginning
            
            # After year should be first word of title
            if after_year:
                # Clean and add first word of title
                title_word = re.sub(r'[^a-zA-Z]', '', after_year)
                if len(title_word) >= 2:
                    components.append(title_word)
        
        else:
            # Fallback: try to parse without clear year
            # Use regex to split on transitions between letters and numbers
            parts = re.findall(r'[a-zA-Z]+|\d+', citekey)
            
            for part in parts:
                if len(part) >= 2:  # Only include meaningful components
                    components.append(part.lower())
        
        return components
    
    def _find_matching_pdfs(self, components: List[str], search_dirs: List[Path]) -> List[tuple]:
        """
        Find PDF files matching the citekey components
        
        Args:
            components: List of components to match
            search_dirs: Directories to search in
            
        Returns:
            List[tuple]: List of (Path, match_score) tuples
        """
        matches = []
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            # Find all PDF files in directory
            for pdf_file in search_dir.rglob("*.pdf"):
                filename_lower = pdf_file.name.lower()
                
                # Count how many components match
                match_score = 0
                for component in components:
                    if component in filename_lower:
                        match_score += 1
                
                # Require at least 2 components to match for a valid match
                if match_score >= min(2, len(components)):
                    matches.append((pdf_file, match_score))
        
        return matches
    
    def _find_common_parent(self, files: List[Path]) -> Optional[Path]:
        """
        Find common parent directory of multiple files
        
        Args:
            files: List of file paths
            
        Returns:
            Optional[Path]: Common parent directory or None
        """
        if not files:
            return None
        
        # Get all parent directories
        parents = [f.parent for f in files]
        
        # Find common parent
        common = parents[0]
        for parent in parents[1:]:
            # Find common path
            try:
                import os
                common = Path(os.path.commonpath([common, parent]))
            except ValueError:
                return None
        
        return common
    
    def _parse_focus(self, focus_str: str) -> FocusType:
        """Parse focus string to FocusType"""
        focus_lower = focus_str.lower()
        if focus_lower in self._focus_aliases:
            return self._focus_aliases[focus_lower]
        
        raise ValidationError(
            f"Invalid focus type: {focus_str}",
            ErrorCode.INVALID_FOCUS,
            field_name="focus",
            suggestions=[
                f"Valid focus types: {', '.join(self._focus_aliases.keys())}",
                "Use 'balanced' for general analysis",
                "Use 'research' for practical applications",
                "Use 'theory' for mathematical models",
                "Use 'review' for literature reviews",
                "Use 'method' for methodologies"
            ]
        )
    
    def _parse_depth(self, depth_str: str) -> DepthType:
        """Parse depth string to DepthType"""
        depth_lower = depth_str.lower()
        if depth_lower in self._depth_aliases:
            return self._depth_aliases[depth_lower]
        
        raise ValidationError(
            f"Invalid depth level: {depth_str}",
            ErrorCode.INVALID_DEPTH,
            field_name="depth",
            suggestions=[
                f"Valid depth levels: {', '.join(self._depth_aliases.keys())}",
                "Use 'quick' for fast analysis",
                "Use 'standard' for balanced analysis",
                "Use 'deep' for comprehensive analysis"
            ]
        )
    
    def _parse_format(self, format_str: str) -> FormatType:
        """Parse format string to FormatType"""
        format_lower = format_str.lower()
        if format_lower in self._format_aliases:
            return self._format_aliases[format_lower]
        
        raise ValidationError(
            f"Invalid format type: {format_str}",
            ErrorCode.INVALID_FORMAT,
            field_name="format",
            suggestions=[
                f"Valid format types: {', '.join(self._format_aliases.keys())}",
                "Currently only markdown format is supported"
            ]
        )
    
    def get_help_text(self) -> str:
        """Get help text for the command"""
        return """
/sq:note - Process PDF papers into structured markdown notes

Usage:
    /sq:note <target> [options]

Arguments:
    target                  PDF file path or directory path (for batch processing)

Options:
    --focus <type>         Focus area for analysis
                          Valid types: research, theory, review, method, balanced
                          Aliases: r, t, rev, m, b
                          Default: balanced

    --depth <level>        Analysis depth level
                          Valid levels: quick, standard, deep
                          Aliases: q, s, d
                          Default: standard

    --format <type>        Output format
                          Valid types: markdown
                          Aliases: md
                          Default: markdown

    --batch                Enable batch processing for directories
    -b                     Short form of --batch

    --minireview           Create comprehensive topic-focused mini-review across multiple papers
                          Requires --topic and a directory of PDFs
                          Creates ONE comprehensive mini-review note

    --topic <description>  Topic focus for mini-review mode
                          Used with --minireview for topic-focused analysis
                          Example: "Kirkwood-Buff finite size correction"

    --output-dir <path>    Output directory for generated notes
                          Default: current directory

Examples:
    /sq:note paper.pdf
    /sq:note paper.pdf --focus research --depth deep
    /sq:note ./papers/ --batch --output-dir ./notes/
    /sq:note research.pdf --focus theory -b
    /sq:note ./papers/ --minireview --topic "Kirkwood-Buff finite size correction" --focus theoretical
    /sq:note ./papers/ --minireview --topic "protein folding mechanisms" --depth deep
"""


def create_command_validation_error(field: str, value: str, valid_options: List[str]) -> ValidationError:
    """Create a standardized validation error for command parsing"""
    return ValidationError(
        f"Invalid {field}: {value}",
        ErrorCode.INVALID_ARGUMENTS,
        field_name=field,
        suggestions=[
            f"Valid {field} options: {', '.join(valid_options)}",
            "Use /sq:note --help for more information"
        ]
    )