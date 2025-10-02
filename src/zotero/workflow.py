"""
Complete Zotero to Obsidian workflow integration
Connects all components: client, mapper, batch processor, cache, formatter, writer
"""

from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from src.models import ZoteroConfig, ObsidianConfig, BatchConfig, PaperMetadata
from src.zotero.client import ZoteroClient
from src.zotero.mapper import ZoteroMetadataMapper
from src.zotero.batch_processor import ZoteroBatchProcessor
from src.zotero.cache import ZoteroCache
from src.obsidian.formatter import ObsidianFormatter
from src.obsidian.writer import ObsidianWriter


class ZoteroObsidianWorkflow:
    """Complete workflow for Zotero → ScholarsQuill → Obsidian"""

    def __init__(
        self,
        zotero_config: ZoteroConfig,
        obsidian_config: ObsidianConfig,
        batch_config: Optional[BatchConfig] = None
    ):
        """
        Initialize workflow with all components

        Args:
            zotero_config: Zotero API configuration
            obsidian_config: Obsidian vault configuration
            batch_config: Optional batch processing configuration
        """
        # Initialize components
        self.zotero_client = ZoteroClient(zotero_config)
        self.mapper = ZoteroMetadataMapper()
        self.formatter = ObsidianFormatter()
        self.writer = ObsidianWriter(obsidian_config)
        
        # Initialize batch processor if config provided
        self.batch_config = batch_config or BatchConfig()
        self.batch_processor = ZoteroBatchProcessor(self.batch_config)
        
        # Initialize cache
        self.cache = ZoteroCache(ttl=batch_config.cache_ttl if batch_config else 86400)
        
        # Track existing citekeys to avoid collisions
        self.existing_citekeys: List[str] = []

    def process_single_item(self, zotero_item: Dict[str, Any], template_content: str = "") -> str:
        """
        Process a single Zotero item to Obsidian note

        Args:
            zotero_item: Zotero item dictionary
            template_content: Optional template for note content

        Returns:
            Path to created note file
        """
        # Check cache first
        item_key = zotero_item.get('key')
        cached_metadata = self.cache.get(item_key) if item_key else None
        
        if cached_metadata:
            metadata = cached_metadata
        else:
            # Map Zotero item to metadata
            metadata = self.mapper.map_zotero_item(zotero_item)
            
            # Generate unique citekey
            metadata.citekey = self.mapper.generate_citekey(
                zotero_item,
                self.existing_citekeys
            )
            self.existing_citekeys.append(metadata.citekey)
            
            # Cache metadata
            if item_key:
                self.cache.store(item_key, metadata)
        
        # Format for Obsidian
        frontmatter = self.formatter.format_yaml_frontmatter(metadata)
        
        # Build full note content
        if template_content:
            note_content = f"{frontmatter}\n{template_content}"
        else:
            note_content = self._generate_default_content(metadata, frontmatter)
        
        # Write to Obsidian vault
        file_path = self.writer.write_note(metadata, note_content)
        
        return file_path

    def process_collection(
        self,
        collection_id: str,
        template_content: str = "",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Process entire Zotero collection

        Args:
            collection_id: Zotero collection ID
            template_content: Optional template for notes
            progress_callback: Optional progress callback(current, total, item_key)

        Returns:
            Summary report with results
        """
        # Fetch items from collection
        items = self.zotero_client.get_collection_items(collection_id)
        
        # Process batch
        results = []
        total = len(items)
        
        for idx, item in enumerate(items, 1):
            item_key = item.get('key', f'UNKNOWN_{idx}')
            
            try:
                file_path = self.process_single_item(item, template_content)
                results.append({
                    'item_key': item_key,
                    'file_path': file_path,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'item_key': item_key,
                    'status': 'failed',
                    'error': str(e)
                })
            
            # Progress callback
            if progress_callback:
                progress_callback(idx, total, item_key)
            
            # Checkpoint at intervals
            if idx % self.batch_config.checkpoint_interval == 0:
                self.batch_processor._save_checkpoint(
                    f'collection_{collection_id}_{idx}',
                    {
                        'processed_count': idx,
                        'collection_id': collection_id,
                        'results': results
                    }
                )
        
        # Generate summary
        return self.batch_processor.generate_summary_report(results)

    def process_library(
        self,
        limit: Optional[int] = None,
        template_content: str = "",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Process entire Zotero library

        Args:
            limit: Optional limit on number of items
            template_content: Optional template for notes
            progress_callback: Optional progress callback

        Returns:
            Summary report with results
        """
        # Fetch all items from library
        items = self.zotero_client.get_items(limit=limit)
        
        # Process batch (similar to process_collection)
        results = []
        total = len(items)
        
        for idx, item in enumerate(items, 1):
            item_key = item.get('key', f'UNKNOWN_{idx}')
            
            try:
                file_path = self.process_single_item(item, template_content)
                results.append({
                    'item_key': item_key,
                    'file_path': file_path,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'item_key': item_key,
                    'status': 'failed',
                    'error': str(e)
                })
            
            if progress_callback:
                progress_callback(idx, total, item_key)
            
            if idx % self.batch_config.checkpoint_interval == 0:
                self.batch_processor._save_checkpoint(
                    f'library_{idx}',
                    {
                        'processed_count': idx,
                        'results': results
                    }
                )
        
        return self.batch_processor.generate_summary_report(results)

    def _generate_default_content(self, metadata: PaperMetadata, frontmatter: str) -> str:
        """
        Generate default note content if no template provided

        Args:
            metadata: Paper metadata
            frontmatter: YAML frontmatter

        Returns:
            Complete note content
        """
        content_parts = [frontmatter]
        
        # Title
        content_parts.append(f"# {metadata.title}\n")
        
        # Citation
        authors_str = metadata.first_author
        if len(metadata.authors) > 1:
            authors_str += " et al."
        content_parts.append(f"**Citation**: {authors_str} ({metadata.year})\n")
        
        # Zotero link
        if metadata.zotero_url:
            content_parts.append(f"**Zotero**: [{metadata.zotero_key}]({metadata.zotero_url})\n")
        
        # Abstract
        if metadata.abstract:
            content_parts.append(f"## Abstract\n\n{metadata.abstract}\n")
        
        # Sections
        content_parts.append("## Summary\n\n<!-- Add your summary here -->\n")
        content_parts.append("## Key Points\n\n- \n\n")
        content_parts.append("## Notes\n\n<!-- Your notes -->\n")
        
        # Related papers section
        content_parts.append("## Related Papers\n\n")
        
        return "\n".join(content_parts)
