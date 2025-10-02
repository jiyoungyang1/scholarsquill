"""
Obsidian markdown file writer
"""

from pathlib import Path
from typing import Optional
from src.models import PaperMetadata, ObsidianConfig


class ObsidianWriteError(Exception):
    """Raised when writing to Obsidian vault fails"""
    pass


class ObsidianWriter:
    """Writes markdown notes to Obsidian vault"""

    def __init__(self, config: ObsidianConfig):
        """
        Initialize writer

        Args:
            config: ObsidianConfig with vault_path and settings
        """
        self.config = config
        self.vault_path = Path(config.vault_path)

        # Create vault directory if it doesn't exist
        if config.create_folders:
            self.vault_path.mkdir(parents=True, exist_ok=True)

    def write_note(self, metadata: PaperMetadata, content: str) -> str:
        """
        Write note to Obsidian vault

        Args:
            metadata: PaperMetadata with citekey and collection info
            content: Full markdown content including frontmatter

        Returns:
            Path to written file

        Raises:
            ObsidianWriteError: If write operation fails
        """
        try:
            # Determine file location based on collections
            file_path = self._get_file_path(metadata)

            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Handle filename conflicts
            file_path = self._resolve_conflict(file_path)

            # Write content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return str(file_path)

        except PermissionError as e:
            raise ObsidianWriteError(f"Permission denied writing to {file_path}: {e}")
        except Exception as e:
            raise ObsidianWriteError(f"Failed to write note: {e}")

    def _get_file_path(self, metadata: PaperMetadata) -> Path:
        """
        Determine file path based on metadata

        Args:
            metadata: PaperMetadata

        Returns:
            Path object for the note file
        """
        # Start with vault path
        base_path = self.vault_path

        # Add collection folder structure if available
        if metadata.zotero_collections and self.config.create_folders:
            # Use the deepest collection
            deepest_collection = max(
                metadata.zotero_collections,
                key=lambda c: c.count('/')
            )
            # Replace spaces and slashes for file system
            folder_path = deepest_collection.replace(' ', '_').replace('/', '_')
            base_path = base_path / folder_path

        # Filename is citekey.md
        filename = f"{metadata.citekey}.md"
        return base_path / filename

    def _resolve_conflict(self, file_path: Path) -> Path:
        """
        Resolve filename conflicts by appending suffix

        Args:
            file_path: Original file path

        Returns:
            Available file path (may have -2, -3 suffix)
        """
        if not file_path.exists():
            return file_path

        # Extract base name and extension
        base_name = file_path.stem
        extension = file_path.suffix
        parent = file_path.parent

        # Find next available suffix
        suffix = 2
        while True:
            new_name = f"{base_name}-{suffix}{extension}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            suffix += 1
