"""
Batch processor for processing multiple Zotero items with checkpointing
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from src.models import BatchConfig


class ZoteroBatchProcessor:
    """Processes multiple Zotero items with progress tracking and checkpointing"""

    def __init__(self, config: BatchConfig):
        """
        Initialize batch processor

        Args:
            config: BatchConfig with batch_size, checkpoint_interval, etc.
        """
        self.config = config
        self.checkpoint_dir = "checkpoints"

    def process_batch(
        self,
        items: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        continue_on_error: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of Zotero items

        Args:
            items: List of Zotero items to process
            progress_callback: Optional callback function(current, total, item_key)
            continue_on_error: Continue processing if individual items fail

        Returns:
            List of processing results with status for each item
        """
        results = []
        total = len(items)

        for idx, item in enumerate(items, 1):
            item_key = item.get('key', f'UNKNOWN_{idx}')

            try:
                # Process single item (to be implemented by caller)
                result = {
                    'item_key': item_key,
                    'status': 'success',
                    'index': idx
                }
                results.append(result)

                # Progress callback
                if progress_callback:
                    progress_callback(idx, total, item_key)

                # Checkpoint at intervals
                if idx % self.config.checkpoint_interval == 0:
                    self._save_checkpoint(f'batch_{int(time.time())}', {
                        'processed_count': idx,
                        'completed_keys': [r['item_key'] for r in results],
                        'timestamp': time.time()
                    })

            except Exception as e:
                if continue_on_error:
                    results.append({
                        'item_key': item_key,
                        'status': 'failed',
                        'error': str(e),
                        'index': idx
                    })
                else:
                    raise

        return results

    def resume_batch(self, items: List[Dict[str, Any]], checkpoint_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Resume batch processing from checkpoint

        Args:
            items: Full list of items to process
            checkpoint_id: Checkpoint ID to resume from

        Returns:
            Complete list of results (checkpoint + newly processed)
        """
        # Load checkpoint
        checkpoint = self._load_checkpoint(checkpoint_id) if checkpoint_id else None

        if not checkpoint:
            return self.process_batch(items)

        processed_count = checkpoint.get('processed_count', 0)
        completed_keys = set(checkpoint.get('completed_keys', []))

        # Filter out already processed items
        remaining_items = [
            item for item in items
            if item.get('key') not in completed_keys
        ]

        # Process remaining items
        new_results = self.process_batch(remaining_items)

        # Combine with checkpoint results
        checkpoint_results = [
            {'item_key': key, 'status': 'success', 'from_checkpoint': True}
            for key in completed_keys
        ]

        return checkpoint_results + new_results

    def generate_summary_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary report from batch results

        Args:
            results: List of processing results

        Returns:
            Summary dictionary with statistics
        """
        total = len(results)
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = total - successful

        # Calculate processing time if available
        processing_time = 0
        if results:
            processing_time = time.time()  # Placeholder

        items_per_second = total / processing_time if processing_time > 0 else 0

        return {
            'total_items': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'processing_time': processing_time,
            'items_per_second': items_per_second
        }

    def process_with_retry(self, item: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Process single item with retry logic

        Args:
            item: Zotero item to process
            max_retries: Maximum retry attempts

        Returns:
            Processing result
        """
        for attempt in range(max_retries):
            try:
                result = self._process_single_item(item)
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(self.config.retry_delay * (attempt + 1))

        return {'status': 'failed'}

    def _process_single_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single item (placeholder for actual implementation)

        Args:
            item: Zotero item

        Returns:
            Processing result
        """
        # This is implemented by caller or subclass
        return {'status': 'success'}

    def _save_checkpoint(self, checkpoint_id: str, data: Dict[str, Any]) -> str:
        """
        Save checkpoint to disk

        Args:
            checkpoint_id: Unique checkpoint identifier
            data: Checkpoint data to save

        Returns:
            Path to saved checkpoint file
        """
        checkpoint_dir = Path(self.checkpoint_dir)
        checkpoint_dir.mkdir(exist_ok=True)

        checkpoint_file = checkpoint_dir / f"{checkpoint_id}.json"

        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)

        return str(checkpoint_file)

    def _load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint from disk

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Checkpoint data or None if not found
        """
        checkpoint_file = Path(self.checkpoint_dir) / f"{checkpoint_id}.json"

        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file, 'r') as f:
            return json.load(f)
