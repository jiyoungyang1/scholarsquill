"""
Zotero API client for fetching items and collections
"""

import time
from typing import List, Dict, Any, Optional
from pyzotero import zotero
from src.models import ZoteroConfig


class ZoteroAuthenticationError(Exception):
    """Raised when Zotero API authentication fails"""
    pass


class ZoteroRateLimitError(Exception):
    """Raised when Zotero API rate limit is exceeded"""
    pass


class ZoteroClient:
    """Client for interacting with Zotero API"""

    def __init__(self, config: ZoteroConfig):
        """
        Initialize Zotero client with configuration

        Args:
            config: ZoteroConfig with library_id, library_type, api_key

        Raises:
            ValueError: If library_type is not 'user' or 'group'
            ZoteroAuthenticationError: If API key is invalid
        """
        # Validate library type
        if config.library_type not in ['user', 'group']:
            raise ValueError(f"Invalid library_type: {config.library_type}. Must be 'user' or 'group'")

        self.library_id = config.library_id
        self.library_type = config.library_type
        self.api_key = config.api_key

        # Initialize pyzotero client
        try:
            self.zot = zotero.Zotero(
                library_id=config.library_id,
                library_type=config.library_type,
                api_key=config.api_key
            )
        except Exception as e:
            raise ZoteroAuthenticationError(f"Failed to initialize Zotero client: {e}")

    def validate_connection(self) -> bool:
        """
        Validate connection to Zotero API

        Returns:
            True if connection is valid

        Raises:
            ZoteroAuthenticationError: If authentication fails
        """
        try:
            # Try to fetch a single item to test connection
            self.zot.top(limit=1)
            return True
        except Exception as e:
            raise ZoteroAuthenticationError(f"Invalid API credentials: {e}")

    def get_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all items from library with automatic pagination

        Args:
            limit: Maximum number of items to fetch (None = all)

        Returns:
            List of Zotero item dictionaries
        """
        items = []
        start = 0
        batch_size = 100  # Zotero API max per request

        while True:
            batch = self._fetch_from_api(f"items/top", start=start, limit=batch_size)
            if not batch:
                break

            items.extend(batch)

            if limit and len(items) >= limit:
                return items[:limit]

            # If we got fewer items than batch_size, we've reached the end
            if len(batch) < batch_size:
                break

            start += batch_size

        return items

    def get_collection_items(self, collection_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all items from a specific collection with pagination

        Args:
            collection_id: Zotero collection ID
            limit: Maximum number of items to fetch (None = all)

        Returns:
            List of Zotero item dictionaries from the collection
        """
        items = []
        start = 0
        batch_size = 100

        while True:
            batch = self._fetch_from_api(f"collections/{collection_id}/items", start=start, limit=batch_size)
            if not batch:
                break

            items.extend(batch)

            if limit and len(items) >= limit:
                return items[:limit]

            if len(batch) < batch_size:
                break

            start += batch_size

        return items

    def _fetch_from_api(self, endpoint: str, start: int = 0, limit: int = 100, retry_count: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch data from Zotero API with retry logic and rate limiting

        Args:
            endpoint: API endpoint to fetch (e.g., "items/top", "collections/{id}/items")
            start: Starting index for pagination
            limit: Number of items to fetch
            retry_count: Current retry attempt number

        Returns:
            List of items from API

        Raises:
            ZoteroRateLimitError: If rate limit is exceeded after retries
        """
        max_retries = 3
        base_delay = 2  # seconds

        try:
            # Parse endpoint to determine method
            if endpoint == "items/top":
                return self.zot.top(start=start, limit=limit)
            elif endpoint.startswith("collections/") and endpoint.endswith("/items"):
                collection_id = endpoint.split("/")[1]
                return self.zot.collection_items(collection_id, start=start, limit=limit)
            else:
                # Fallback: use everything() for general queries
                return self.zot.everything(self.zot.items(start=start, limit=limit))

        except Exception as e:
            error_msg = str(e)

            # Handle rate limit errors (429)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                if retry_count < max_retries:
                    # Exponential backoff
                    delay = base_delay * (2 ** retry_count)
                    time.sleep(delay)
                    return self._fetch_from_api(endpoint, start, limit, retry_count + 1)
                else:
                    raise ZoteroRateLimitError(f"Rate limit exceeded after {max_retries} retries")

            # Handle other errors
            if retry_count < max_retries:
                time.sleep(base_delay)
                return self._fetch_from_api(endpoint, start, limit, retry_count + 1)
            else:
                raise

    def get_collections(self) -> List[Dict[str, Any]]:
        """
        Get all collections from library

        Returns:
            List of collection dictionaries
        """
        try:
            return self.zot.collections()
        except Exception as e:
            raise Exception(f"Failed to fetch collections: {e}")

    def get_item(self, item_key: str) -> Dict[str, Any]:
        """
        Get a single item by key

        Args:
            item_key: Zotero item key

        Returns:
            Item dictionary
        """
        try:
            return self.zot.item(item_key)
        except Exception as e:
            raise Exception(f"Failed to fetch item {item_key}: {e}")
