"""
Unit tests for Zotero client connection and item fetching
Tests MUST fail until implementation is complete (TDD)
"""

import pytest
from unittest.mock import Mock, patch
from src.zotero.client import ZoteroClient
from src.models import ZoteroConfig


class TestZoteroClientConnection:
    """Test Zotero client initialization and connection"""

    def test_init_with_valid_credentials(self):
        """Test ZoteroClient.__init__() with valid credentials"""
        config = ZoteroConfig(
            library_id="12345",
            library_type="user",
            api_key="test_api_key_abc123"
        )

        # This will fail until ZoteroClient is implemented
        client = ZoteroClient(config)

        assert client is not None
        assert client.library_id == "12345"
        assert client.library_type == "user"

    def test_init_with_invalid_api_key(self):
        """Test connection failure with invalid API key"""
        config = ZoteroConfig(
            library_id="12345",
            library_type="user",
            api_key="invalid_key"
        )

        # Should raise authentication error
        with pytest.raises(Exception):  # Will be ZoteroAuthenticationError
            client = ZoteroClient(config)
            client.validate_connection()

    def test_library_type_validation(self):
        """Test library type validation (user vs group)"""
        # Valid user library
        config_user = ZoteroConfig(
            library_id="12345",
            library_type="user",
            api_key="test_key"
        )
        client = ZoteroClient(config_user)
        assert client.library_type == "user"

        # Valid group library
        config_group = ZoteroConfig(
            library_id="67890",
            library_type="group",
            api_key="test_key"
        )
        client = ZoteroClient(config_group)
        assert client.library_type == "group"

        # Invalid library type
        config_invalid = ZoteroConfig(
            library_id="12345",
            library_type="invalid",
            api_key="test_key"
        )
        with pytest.raises(ValueError):
            ZoteroClient(config_invalid)


class TestZoteroItemFetching:
    """Test fetching items from Zotero"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Zotero client for testing"""
        config = ZoteroConfig(
            library_id="12345",
            library_type="user",
            api_key="test_key"
        )
        return ZoteroClient(config)

    def test_get_items_returns_list(self, mock_client):
        """Test get_items() returns list of items"""
        # Mock Zotero API response
        with patch.object(mock_client, '_fetch_from_api') as mock_fetch:
            mock_fetch.return_value = [
                {'key': 'ABC123', 'data': {'title': 'Test Paper'}},
                {'key': 'DEF456', 'data': {'title': 'Another Paper'}}
            ]

            items = mock_client.get_items()

            assert isinstance(items, list)
            assert len(items) == 2
            assert items[0]['key'] == 'ABC123'

    def test_get_collection_items(self, mock_client):
        """Test get_collection_items() with collection ID"""
        collection_id = "COLL123"

        with patch.object(mock_client, '_fetch_from_api') as mock_fetch:
            mock_fetch.return_value = [
                {'key': 'ABC123', 'data': {'title': 'Paper in Collection'}}
            ]

            items = mock_client.get_collection_items(collection_id)

            assert isinstance(items, list)
            assert len(items) == 1
            mock_fetch.assert_called_once_with(f"collections/{collection_id}/items")

    def test_pagination_handling_large_collection(self, mock_client):
        """Test pagination handling for >100 items"""
        # Zotero API returns max 100 items per request
        with patch.object(mock_client, '_fetch_from_api') as mock_fetch:
            # Simulate paginated responses
            mock_fetch.side_effect = [
                [{'key': f'ITEM{i}'} for i in range(100)],  # First page
                [{'key': f'ITEM{i}'} for i in range(100, 150)]  # Second page
            ]

            items = mock_client.get_items()

            assert len(items) == 150
            assert mock_fetch.call_count == 2

    def test_rate_limit_retry_logic(self, mock_client):
        """Test rate limit handling with exponential backoff"""
        with patch.object(mock_client, '_fetch_from_api') as mock_fetch:
            # Simulate rate limit error, then success
            mock_fetch.side_effect = [
                Exception("429 Too Many Requests"),
                [{'key': 'ABC123'}]
            ]

            items = mock_client.get_items()

            # Should retry and succeed
            assert len(items) == 1
            assert mock_fetch.call_count == 2
