"""
Caching system for Zotero items to reduce API calls
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional


class ZoteroCache:
    """File-based cache for Zotero items with TTL expiration"""

    def __init__(self, cache_dir: str = ".zotero_cache", ttl: int = 86400):
        """
        Initialize cache

        Args:
            cache_dir: Directory to store cache files
            ttl: Time-to-live in seconds (default 24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.cache_dir.mkdir(exist_ok=True)

    def store(self, key: str, item: Dict[str, Any]) -> None:
        """
        Store item in cache with timestamp

        Args:
            key: Cache key (typically Zotero item key)
            item: Item data to cache
        """
        cache_entry = {
            'data': item,
            'timestamp': time.time()
        }

        cache_file = self._get_cache_file(key)
        with open(cache_file, 'w') as f:
            json.dump(cache_entry, f, indent=2)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve item from cache if not expired

        Args:
            key: Cache key

        Returns:
            Cached item data or None if expired/not found
        """
        cache_file = self._get_cache_file(key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                cache_entry = json.load(f)

            # Check if expired
            timestamp = cache_entry.get('timestamp', 0)
            if time.time() - timestamp > self.ttl:
                # Expired - remove file
                cache_file.unlink()
                return None

            return cache_entry.get('data')

        except Exception:
            return None

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache (not expired)

        Args:
            key: Cache key

        Returns:
            True if key exists and not expired
        """
        return self.get(key) is not None

    def invalidate(self, key: str) -> None:
        """
        Remove item from cache

        Args:
            key: Cache key to invalidate
        """
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            cache_file.unlink()

    def clear_all(self) -> None:
        """Remove all items from cache"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

    def size(self) -> int:
        """
        Get number of items in cache

        Returns:
            Number of cached items
        """
        return len(list(self.cache_dir.glob("*.json")))

    def _get_cache_file(self, key: str) -> Path:
        """
        Get cache file path for key

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Sanitize key for filename
        safe_key = key.replace('/', '_').replace('\\', '_')
        return self.cache_dir / f"{safe_key}.json"
