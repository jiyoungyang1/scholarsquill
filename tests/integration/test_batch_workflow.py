"""
Integration tests for batch processing workflow
Tests MUST fail until implementation is complete (TDD)

Tests batch processing with multiple items using real test data
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.zotero.batch_processor import ZoteroBatchProcessor
from src.zotero.client import ZoteroClient
from src.zotero.mapper import ZoteroMetadataMapper
from src.obsidian.writer import ObsidianWriter
from src.models import BatchConfig, ZoteroConfig, ObsidianConfig


@pytest.fixture
def batch_items_50():
    """Create 50 mock Zotero items for batch testing"""
    items = []
    for i in range(50):
        items.append({
            'key': f'ITEM{i:03d}',
            'data': {
                'itemType': 'journalArticle',
                'title': f'Paper {i}: Machine Learning Applications',
                'creators': [
                    {'creatorType': 'author', 'lastName': f'Author{i}'}
                ],
                'date': str(2020 + (i % 5)),  # 2020-2024
                'DOI': f'10.1234/paper{i}',
                'tags': [
                    {'tag': 'machine-learning'},
                    {'tag': f'topic-{i % 10}'}
                ],
                'collections': [f'Collection {i // 10}']
            }
        })
    return items


@pytest.fixture
def batch_config():
    """Create batch configuration"""
    return BatchConfig(
        batch_size=50,
        checkpoint_interval=10,
        cache_ttl=86400
    )


class TestBatchProcessingWorkflow:
    """Test end-to-end batch processing"""

    def test_process_collection_with_50_items(self, batch_items_50, batch_config, tmp_path):
        """Test: Process collection with 50 items"""
        processor = ZoteroBatchProcessor(batch_config)
        mapper = ZoteroMetadataMapper()

        obsidian_config = ObsidianConfig(vault_path=str(tmp_path / "vault"))
        writer = ObsidianWriter(obsidian_config)

        # Process all items
        results = []
        for item in batch_items_50:
            metadata = mapper.map_zotero_item(item)
            content = f"# {metadata.title}\n\nGenerated from batch processing."
            file_path = writer.write_note(metadata, content)
            results.append({
                'item_key': item['key'],
                'file_path': file_path,
                'status': 'success'
            })

        # Verify all 50 notes created
        assert len(results) == 50
        assert all(r['status'] == 'success' for r in results)

        # Verify files exist
        vault_path = Path(tmp_path / "vault")
        created_files = list(vault_path.rglob("*.md"))
        assert len(created_files) == 50

    def test_progress_tracking_works(self, batch_items_50, batch_config):
        """Verify progress tracking during batch processing"""
        processor = ZoteroBatchProcessor(batch_config)

        progress_updates = []

        def track_progress(current, total, item_key):
            progress_updates.append({
                'current': current,
                'total': total,
                'key': item_key,
                'percentage': (current / total) * 100
            })

        processor.process_batch(
            batch_items_50,
            progress_callback=track_progress
        )

        # Verify progress tracking
        assert len(progress_updates) == 50
        assert progress_updates[0]['current'] == 1
        assert progress_updates[-1]['current'] == 50
        assert progress_updates[-1]['percentage'] == 100.0

    def test_summary_report_accuracy(self, batch_items_50, batch_config):
        """Verify summary report after batch completion"""
        processor = ZoteroBatchProcessor(batch_config)

        results = processor.process_batch(batch_items_50)
        report = processor.generate_summary_report(results)

        assert report['total_items'] == 50
        assert report['successful'] == 50
        assert report['failed'] == 0
        assert 'processing_time' in report
        assert 'items_per_second' in report


class TestCheckpointingAndRecovery:
    """Test checkpoint creation and recovery from interruptions"""

    def test_checkpoint_every_10_items(self, batch_items_50, batch_config, tmp_path):
        """Test checkpoint creation at configured intervals"""
        processor = ZoteroBatchProcessor(batch_config)
        processor.checkpoint_dir = str(tmp_path / "checkpoints")

        # Process with checkpointing
        with patch.object(processor, '_save_checkpoint') as mock_checkpoint:
            processor.process_batch(batch_items_50)

            # Should save checkpoints at items 10, 20, 30, 40, 50
            assert mock_checkpoint.call_count >= 5

    def test_resume_after_interruption_at_item_25(self, batch_items_50, batch_config, tmp_path):
        """Test resuming batch after interruption at item 25"""
        processor = ZoteroBatchProcessor(batch_config)

        # Simulate checkpoint at item 25
        checkpoint = {
            'processed_count': 25,
            'completed_keys': [f'ITEM{i:03d}' for i in range(25)],
            'timestamp': '2024-10-02T10:00:00Z'
        }

        with patch.object(processor, '_load_checkpoint', return_value=checkpoint):
            results = processor.resume_batch(batch_items_50)

            # Should process remaining 25 items
            assert len(results) == 50
            # First 25 from checkpoint, last 25 newly processed

    def test_checkpoint_data_integrity(self, batch_config, tmp_path):
        """Verify checkpoint data can be saved and loaded correctly"""
        processor = ZoteroBatchProcessor(batch_config)
        processor.checkpoint_dir = str(tmp_path / "checkpoints")

        checkpoint_data = {
            'batch_id': 'test_batch_001',
            'processed_count': 30,
            'completed_keys': [f'ITEM{i:03d}' for i in range(30)],
            'errors': [],
            'timestamp': '2024-10-02T12:00:00Z'
        }

        # Save checkpoint
        checkpoint_path = processor._save_checkpoint('test_batch_001', checkpoint_data)
        assert Path(checkpoint_path).exists()

        # Load checkpoint
        loaded = processor._load_checkpoint('test_batch_001')
        assert loaded['processed_count'] == 30
        assert len(loaded['completed_keys']) == 30


class TestErrorHandlingAndRetry:
    """Test error handling and retry logic during batch processing"""

    def test_handle_failed_items(self, batch_config):
        """Test handling of failed items during batch"""
        processor = ZoteroBatchProcessor(batch_config)

        # Create items where some will fail
        items = [
            {'key': 'GOOD1', 'data': {'itemType': 'journalArticle', 'title': 'Good', 'creators': [{'lastName': 'A'}], 'date': '2023'}},
            {'key': 'BAD1', 'data': {}},  # Missing required fields
            {'key': 'GOOD2', 'data': {'itemType': 'journalArticle', 'title': 'Good', 'creators': [{'lastName': 'B'}], 'date': '2023'}},
            {'key': 'BAD2', 'data': None},  # Invalid data
            {'key': 'GOOD3', 'data': {'itemType': 'journalArticle', 'title': 'Good', 'creators': [{'lastName': 'C'}], 'date': '2023'}},
        ]

        results = processor.process_batch(items, continue_on_error=True)

        # Should process all items but mark failures
        assert len(results) == 5
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'failed']

        assert len(successful) == 3
        assert len(failed) == 2

    def test_retry_on_transient_failures(self, batch_config):
        """Test retry logic for transient failures"""
        processor = ZoteroBatchProcessor(batch_config)

        item = {
            'key': 'RETRY1',
            'data': {
                'itemType': 'journalArticle',
                'title': 'Test',
                'creators': [{'lastName': 'Test'}],
                'date': '2023'
            }
        }

        attempt_count = [0]

        def mock_process(item):
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise Exception("Transient error")
            return {'status': 'success'}

        with patch.object(processor, '_process_single_item', side_effect=mock_process):
            result = processor.process_with_retry(item, max_retries=3)

            # Should succeed after 3 attempts
            assert result['status'] == 'success'
            assert attempt_count[0] == 3


class TestPerformanceMetrics:
    """Test performance tracking and metrics"""

    def test_processing_time_under_2_minutes_for_100_items(self, batch_config):
        """Test processing 100 items completes within 2 minutes"""
        items = [
            {
                'key': f'PERF{i:03d}',
                'data': {
                    'itemType': 'journalArticle',
                    'title': f'Paper {i}',
                    'creators': [{'lastName': f'Author{i}'}],
                    'date': '2023'
                }
            }
            for i in range(100)
        ]

        processor = ZoteroBatchProcessor(batch_config)

        import time
        start_time = time.time()
        results = processor.process_batch(items)
        elapsed_time = time.time() - start_time

        # Should complete in < 120 seconds (requirement from spec)
        assert elapsed_time < 120
        assert len(results) == 100

    def test_items_per_second_metric(self, batch_items_50, batch_config):
        """Test items per second calculation"""
        processor = ZoteroBatchProcessor(batch_config)

        results = processor.process_batch(batch_items_50)
        report = processor.generate_summary_report(results)

        assert 'items_per_second' in report
        assert report['items_per_second'] > 0
        # Should process at reasonable rate (e.g., > 5 items/sec)
        assert report['items_per_second'] >= 5
