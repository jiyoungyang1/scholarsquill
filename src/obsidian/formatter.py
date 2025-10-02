"""
Obsidian-specific formatting for markdown notes
"""

from typing import List, Optional
from src.models import PaperMetadata


class ObsidianFormatter:
    """Formats metadata and content for Obsidian compatibility"""

    def format_yaml_frontmatter(self, metadata: PaperMetadata) -> str:
        """
        Format YAML frontmatter with Zotero metadata

        Args:
            metadata: PaperMetadata with Zotero fields

        Returns:
            YAML frontmatter string with --- delimiters
        """
        lines = ["---"]

        # Basic metadata
        lines.append(f"title: {metadata.title}")
        lines.append(f"citekey: {metadata.citekey}")

        # Authors
        lines.append("authors:")
        for author in metadata.authors:
            lines.append(f"  - {author}")

        # Year and publication info
        if metadata.year:
            lines.append(f"year: {metadata.year}")
        if metadata.journal:
            lines.append(f"journal: {metadata.journal}")
        if metadata.volume:
            lines.append(f"volume: {metadata.volume}")
        if metadata.issue:
            lines.append(f"issue: {metadata.issue}")
        if metadata.pages:
            lines.append(f"pages: {metadata.pages}")
        if metadata.doi:
            lines.append(f"doi: {metadata.doi}")

        # Item type
        lines.append(f"item_type: {metadata.item_type}")

        # Zotero fields
        if metadata.zotero_key:
            lines.append(f"zotero_key: {metadata.zotero_key}")
        if metadata.zotero_url:
            lines.append(f"zotero_url: {metadata.zotero_url}")

        # Tags (Obsidian format)
        if metadata.zotero_tags:
            lines.append("tags:")
            for tag in metadata.zotero_tags:
                lines.append(f"  - {tag}")

        # Collections
        if metadata.zotero_collections:
            lines.append("collections:")
            for collection in metadata.zotero_collections:
                lines.append(f"  - {collection}")

        # Dates
        if metadata.date_added:
            lines.append(f"date_added: {metadata.date_added}")
        if metadata.date_modified:
            lines.append(f"date_modified: {metadata.date_modified}")

        lines.append("---")
        lines.append("")  # Blank line after frontmatter

        return "\n".join(lines)

    def generate_wikilink(self, citekey: str, display_text: Optional[str] = None) -> str:
        """
        Generate Obsidian wikilink

        Args:
            citekey: Target note citekey
            display_text: Optional display text

        Returns:
            Wikilink string [[citekey]] or [[citekey|display]]
        """
        if display_text:
            return f"[[{citekey}|{display_text}]]"
        return f"[[{citekey}]]"

    def format_zotero_url(self, zotero_key: str, library_type: str = "library", library_id: Optional[str] = None) -> str:
        """
        Format Zotero URL for opening items

        Args:
            zotero_key: Zotero item key
            library_type: 'library' or 'group'
            library_id: Library ID (optional)

        Returns:
            Zotero URL string
        """
        return f"zotero://select/{library_type}/items/{zotero_key}"

    def format_tags(self, tags: List[str]) -> str:
        """
        Format tags for Obsidian

        Args:
            tags: List of tag strings

        Returns:
            Formatted tags string
        """
        # Return as comma-separated list (YAML array handled in frontmatter)
        return ", ".join(tags)

    def generate_collection_path(self, collections: List[str]) -> str:
        """
        Generate folder path from Zotero collections

        Args:
            collections: List of collection names/paths

        Returns:
            File system path for note
        """
        if not collections:
            return ""

        # Use the deepest (most specific) collection
        deepest = max(collections, key=lambda c: c.count('/'))

        # Replace spaces with underscores for file system compatibility
        path = deepest.replace(' ', '_')

        return path
