"""
File I/O and output handling for ScholarSquill Kiro MCP Server
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

try:
    from .interfaces import FileWriterInterface
    from .models import PaperMetadata, FormatType
    from .exceptions import FileError, ErrorCode
    from .utils import sanitize_filename, extract_first_author_lastname, ensure_directory
except ImportError:
    from interfaces import FileWriterInterface
    from models import PaperMetadata, FormatType
    from exceptions import FileError, ErrorCode
    from utils import sanitize_filename, extract_first_author_lastname, ensure_directory


class FileWriter(FileWriterInterface):
    """File writer for handling output file operations"""
    
    def __init__(self, default_output_dir: Optional[str] = None, 
                 overwrite_mode: str = "prompt", logger: Optional[logging.Logger] = None):
        """
        Initialize file writer
        
        Args:
            default_output_dir: Default directory for output files
            overwrite_mode: How to handle existing files ("overwrite", "rename", "prompt", "skip")
            logger: Optional logger for file operations
        """
        self.default_output_dir = default_output_dir or "literature-notes"
        self.overwrite_mode = overwrite_mode
        self.logger = logger or logging.getLogger(__name__)
        
        # Validate overwrite mode
        valid_modes = ["overwrite", "rename", "prompt", "skip"]
        if overwrite_mode not in valid_modes:
            self.overwrite_mode = "prompt"
            self.logger.warning(f"Invalid overwrite mode '{overwrite_mode}', using 'prompt'")
    
    def write_note(self, content: str, output_path: str) -> str:
        """
        Write note content to file
        
        Args:
            content: Note content to write
            output_path: Path where to write the file
            
        Returns:
            str: Actual path where file was written
            
        Raises:
            FileError: If file cannot be written
        """
        try:
            output_file = Path(output_path)
            
            # Ensure output directory exists
            self.ensure_output_directory(str(output_file.parent))
            
            # Handle file conflicts
            final_path = self._resolve_file_conflict(output_file)
            
            # Write the content
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Successfully wrote note to: {final_path}")
            return str(final_path)
            
        except PermissionError:
            raise FileError(
                f"Permission denied writing to: {output_path}",
                ErrorCode.FILE_UNREADABLE,
                file_path=output_path,
                suggestions=[
                    "Check write permissions for the output directory",
                    "Run with appropriate user privileges",
                    "Choose a different output directory"
                ]
            )
        except OSError as e:
            raise FileError(
                f"Error writing file {output_path}: {e}",
                ErrorCode.FILE_ERROR,
                file_path=output_path,
                suggestions=[
                    "Check available disk space",
                    "Ensure the path is valid",
                    "Check filesystem permissions"
                ]
            )
        except Exception as e:
            raise FileError(
                f"Unexpected error writing file {output_path}: {e}",
                ErrorCode.FILE_ERROR,
                file_path=output_path,
                suggestions=[
                    "Check file path validity",
                    "Ensure content is valid UTF-8",
                    "Try a different output location"
                ]
            )
    
    def generate_filename(self, metadata: PaperMetadata, format_type: str) -> str:
        """
        Generate safe filename from metadata
        
        Args:
            metadata: Paper metadata
            format_type: Output format type
            
        Returns:
            str: Generated filename
        """
        # Get file extension based on format
        extension = self._get_file_extension(format_type)
        
        # Generate base filename using different strategies
        filename = self._generate_base_filename(metadata)
        
        # Sanitize and add extension
        safe_filename = sanitize_filename(filename, max_length=200)
        return f"{safe_filename}{extension}"
    
    def generate_citekey_filename(self, metadata: PaperMetadata, format_type: str = "markdown") -> str:
        """
        Generate filename using citekey format: authorYEARkeyword.ext
        
        Args:
            metadata: Paper metadata
            format_type: Output format type
            
        Returns:
            str: Generated filename in citekey format
        """
        from .utils import generate_citekey
        
        # Get file extension based on format
        extension = self._get_file_extension(format_type)
        
        # Generate citekey
        if metadata.authors and metadata.title:
            first_author = metadata.authors[0]
            citekey = generate_citekey(first_author, metadata.year, metadata.title)
        else:
            # Fallback to basic filename generation
            citekey = self._generate_base_filename(metadata)
        
        # Sanitize and add extension
        safe_filename = sanitize_filename(citekey, max_length=200)
        return f"{safe_filename}{extension}"
    
    def ensure_output_directory(self, directory_path: str) -> bool:
        """
        Ensure output directory exists
        
        Args:
            directory_path: Path to directory
            
        Returns:
            bool: True if directory exists or was created successfully
            
        Raises:
            FileError: If directory cannot be created
        """
        try:
            path = Path(directory_path)
            
            # If path exists and is a file, that's an error
            if path.exists() and not path.is_dir():
                raise FileError(
                    f"Output path exists but is not a directory: {directory_path}",
                    ErrorCode.INVALID_PATH,
                    file_path=directory_path,
                    suggestions=[
                        "Choose a different output directory",
                        "Remove the existing file",
                        "Use a subdirectory name"
                    ]
                )
            
            # Create directory if it doesn't exist
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created output directory: {directory_path}")
            
            return True
            
        except PermissionError:
            raise FileError(
                f"Permission denied creating directory: {directory_path}",
                ErrorCode.FILE_UNREADABLE,
                file_path=directory_path,
                suggestions=[
                    "Check write permissions for the parent directory",
                    "Run with appropriate user privileges",
                    "Choose a directory you have write access to"
                ]
            )
        except OSError as e:
            raise FileError(
                f"Error creating directory {directory_path}: {e}",
                ErrorCode.FILE_ERROR,
                file_path=directory_path,
                suggestions=[
                    "Check available disk space",
                    "Ensure the path is valid",
                    "Check parent directory permissions"
                ]
            )
    
    def get_output_path(self, metadata: PaperMetadata, format_type: str, 
                       output_dir: Optional[str] = None) -> str:
        """
        Get full output path for a note file
        
        Args:
            metadata: Paper metadata
            format_type: Output format type
            output_dir: Optional output directory override
            
        Returns:
            str: Full output path
        """
        # Determine output directory
        target_dir = output_dir or self.default_output_dir
        
        # Generate filename
        filename = self.generate_filename(metadata, format_type)
        
        # Combine path
        return str(Path(target_dir) / filename)
    
    def backup_existing_file(self, file_path: str) -> str:
        """
        Create backup of existing file
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            str: Path to backup file
            
        Raises:
            FileError: If backup cannot be created
        """
        try:
            original_path = Path(file_path)
            
            if not original_path.exists():
                return file_path
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = original_path.with_name(
                f"{original_path.stem}_backup_{timestamp}{original_path.suffix}"
            )
            
            # Copy file to backup location
            shutil.copy2(original_path, backup_path)
            
            self.logger.info(f"Created backup: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            raise FileError(
                f"Error creating backup for {file_path}: {e}",
                ErrorCode.FILE_ERROR,
                file_path=file_path,
                suggestions=[
                    "Check write permissions",
                    "Ensure sufficient disk space",
                    "Try a different backup location"
                ]
            )
    
    def _resolve_file_conflict(self, output_path: Path) -> Path:
        """
        Resolve file conflict based on overwrite mode
        
        Args:
            output_path: Intended output path
            
        Returns:
            Path: Resolved output path
        """
        if not output_path.exists():
            return output_path
        
        if self.overwrite_mode == "overwrite":
            # Create backup before overwriting
            self.backup_existing_file(str(output_path))
            return output_path
        
        elif self.overwrite_mode == "rename":
            return self._generate_unique_filename(output_path)
        
        elif self.overwrite_mode == "skip":
            raise FileError(
                f"File already exists and overwrite mode is 'skip': {output_path}",
                ErrorCode.FILE_EXISTS,
                file_path=str(output_path),
                suggestions=[
                    "Change overwrite mode to 'overwrite' or 'rename'",
                    "Remove the existing file",
                    "Choose a different output location"
                ]
            )
        
        else:  # prompt mode - for now, default to rename
            self.logger.warning(f"File exists: {output_path}, auto-renaming")
            return self._generate_unique_filename(output_path)
    
    def _generate_unique_filename(self, original_path: Path) -> Path:
        """
        Generate unique filename by appending counter
        
        Args:
            original_path: Original intended path
            
        Returns:
            Path: Unique path that doesn't exist
        """
        counter = 1
        base_path = original_path.parent
        stem = original_path.stem
        suffix = original_path.suffix
        
        while True:
            new_path = base_path / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
            
            # Safety limit to prevent infinite loop
            if counter > 1000:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return base_path / f"{stem}_{timestamp}{suffix}"
    
    def _generate_base_filename(self, metadata: PaperMetadata) -> str:
        """
        Generate base filename from metadata using citekey format
        
        Args:
            metadata: Paper metadata
            
        Returns:
            str: Base filename without extension (citekey format: authorYEARkeyword)
        """
        # Strategy 1: Use citekey if available
        if metadata.citekey:
            return metadata.citekey
        
        # Strategy 2: Generate citekey from metadata
        if metadata.authors and metadata.title:
            from .utils import generate_citekey
            first_author = metadata.authors[0]
            return generate_citekey(first_author, metadata.year, metadata.title)
        
        # Strategy 3: Fallback using available components
        components = []
        
        # Add first author's last name
        if metadata.authors:
            author_lastname = extract_first_author_lastname(metadata.authors)
            components.append(author_lastname.lower())
        
        # Add year
        if metadata.year:
            components.append(str(metadata.year))
        else:
            components.append("unknown")
        
        # Add first meaningful word from title
        if metadata.title:
            title_words = metadata.title.split()
            meaningful_words = [word for word in title_words if len(word) > 3]
            if meaningful_words:
                components.append(meaningful_words[0].lower())
            else:
                components.append("paper")
        else:
            components.append("untitled")
        
        # Join components or use fallback
        if components:
            return "".join(components)  # No underscores for citekey format
        else:
            # Fallback to timestamp-based name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"paper_{timestamp}"
    
    def _get_file_extension(self, format_type: str) -> str:
        """
        Get file extension for format type
        
        Args:
            format_type: Output format type
            
        Returns:
            str: File extension including dot
        """
        format_extensions = {
            FormatType.MARKDOWN.value: ".md",
            "markdown": ".md",
            "md": ".md",
        }
        
        return format_extensions.get(format_type.lower(), ".md")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dict with file information
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {"exists": False}
            
            stat = path.stat()
            
            return {
                "exists": True,
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
                "size_bytes": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "created_time": datetime.fromtimestamp(stat.st_ctime),
                "readable": os.access(path, os.R_OK),
                "writable": os.access(path, os.W_OK),
            }
            
        except Exception as e:
            return {
                "exists": False,
                "error": str(e)
            }
    
    def cleanup_temp_files(self, temp_dir: str) -> None:
        """
        Clean up temporary files and directories
        
        Args:
            temp_dir: Path to temporary directory to clean up
        """
        try:
            temp_path = Path(temp_dir)
            if temp_path.exists() and temp_path.is_dir():
                shutil.rmtree(temp_path)
                self.logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp directory {temp_dir}: {e}")


# Additional error class for file operations
class FileExistsError(FileError):
    """Error when file already exists and cannot be overwritten"""
    
    def __init__(self, file_path: str, suggestions: Optional[list] = None):
        super().__init__(
            f"File already exists: {file_path}",
            ErrorCode.FILE_ERROR,
            file_path=file_path,
            suggestions=suggestions or [
                "Use overwrite mode to replace existing file",
                "Use rename mode to create new file with different name",
                "Delete the existing file manually"
            ]
        )


def create_file_writer(config: Optional[Dict[str, Any]] = None) -> FileWriter:
    """
    Factory function to create FileWriter with configuration
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        FileWriter: Configured file writer instance
    """
    config = config or {}
    
    return FileWriter(
        default_output_dir=config.get("default_output_dir", "literature-notes"),
        overwrite_mode=config.get("overwrite_mode", "prompt"),
        logger=config.get("logger")
    )