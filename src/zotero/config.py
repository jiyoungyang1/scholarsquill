"""
Configuration management for Zotero integration with environment variable support.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from src.models import ZoteroConfig, ObsidianConfig, BatchConfig


class ZoteroConfigManager:
    """
    Manages Zotero integration configuration from environment variables and YAML files.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Optional path to YAML configuration file
        """
        self.config_path = config_path
        self._config_data = {}

        if config_path and config_path.exists():
            self._load_yaml_config()

    def _load_yaml_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self._config_data = yaml.safe_load(f) or {}
        except Exception as e:
            raise ValueError(f"Failed to load config from {self.config_path}: {e}")

    def get_zotero_config(self) -> ZoteroConfig:
        """
        Get Zotero API configuration from environment variables or YAML.

        Environment variables take precedence over YAML config.

        Returns:
            ZoteroConfig with API credentials

        Raises:
            ValueError: If required credentials are missing
        """
        # Try environment variables first
        library_id = os.getenv('ZOTERO_LIBRARY_ID')
        library_type = os.getenv('ZOTERO_LIBRARY_TYPE')
        api_key = os.getenv('ZOTERO_API_KEY')

        # Fall back to YAML config
        yaml_zotero = self._config_data.get('zotero', {})

        library_id = library_id or yaml_zotero.get('library_id')
        library_type = library_type or yaml_zotero.get('library_type')
        api_key = api_key or yaml_zotero.get('api_key')

        # Validate required fields
        if not library_id:
            raise ValueError(
                "Missing ZOTERO_LIBRARY_ID. Set environment variable or add to config YAML."
            )
        if not library_type:
            raise ValueError(
                "Missing ZOTERO_LIBRARY_TYPE. Set environment variable or add to config YAML. "
                "Valid values: 'user' or 'group'"
            )
        if not api_key:
            raise ValueError(
                "Missing ZOTERO_API_KEY. Set environment variable or add to config YAML. "
                "Generate at https://www.zotero.org/settings/keys/new"
            )

        # Validate library type
        if library_type not in ['user', 'group']:
            raise ValueError(
                f"Invalid ZOTERO_LIBRARY_TYPE: {library_type}. Must be 'user' or 'group'"
            )

        # Get optional cache TTL
        cache_ttl = yaml_zotero.get('cache_ttl', 86400)

        return ZoteroConfig(
            library_id=library_id,
            library_type=library_type,
            api_key=api_key,
            cache_ttl=cache_ttl
        )

    def get_obsidian_config(self) -> ObsidianConfig:
        """
        Get Obsidian output configuration.

        Returns:
            ObsidianConfig with vault settings
        """
        yaml_obsidian = self._config_data.get('obsidian', {})

        # Default vault path from environment or YAML or current directory
        vault_path = os.getenv('OBSIDIAN_VAULT_PATH') or \
                     yaml_obsidian.get('vault_path', './obsidian_vault')

        return ObsidianConfig(
            vault_path=vault_path,
            use_rest_api=yaml_obsidian.get('use_rest_api', False),
            rest_api_port=yaml_obsidian.get('rest_api_port', 27123),
            create_folders=yaml_obsidian.get('create_folders', True)
        )

    def get_batch_config(self) -> BatchConfig:
        """
        Get batch processing configuration.

        Returns:
            BatchConfig with batch processing settings
        """
        yaml_batch = self._config_data.get('batch', {})

        return BatchConfig(
            batch_size=yaml_batch.get('batch_size', 50),
            checkpoint_interval=yaml_batch.get('checkpoint_interval', 10),
            cache_ttl=yaml_batch.get('cache_ttl', 86400),
            max_retries=yaml_batch.get('max_retries', 3),
            retry_delay=yaml_batch.get('retry_delay', 5)
        )

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate environment setup and return diagnostic information.

        Returns:
            Dictionary with validation results and diagnostics
        """
        diagnostics = {
            'zotero_config': {'status': 'unknown', 'details': {}},
            'obsidian_config': {'status': 'unknown', 'details': {}},
            'dependencies': {'status': 'unknown', 'details': {}}
        }

        # Check Zotero configuration
        try:
            zotero_config = self.get_zotero_config()
            diagnostics['zotero_config']['status'] = 'valid'
            diagnostics['zotero_config']['details'] = {
                'library_id': zotero_config.library_id,
                'library_type': zotero_config.library_type,
                'api_key_set': bool(zotero_config.api_key),
                'cache_ttl': zotero_config.cache_ttl
            }
        except ValueError as e:
            diagnostics['zotero_config']['status'] = 'invalid'
            diagnostics['zotero_config']['error'] = str(e)

        # Check Obsidian configuration
        try:
            obsidian_config = self.get_obsidian_config()
            vault_exists = Path(obsidian_config.vault_path).exists()
            diagnostics['obsidian_config']['status'] = 'valid'
            diagnostics['obsidian_config']['details'] = {
                'vault_path': obsidian_config.vault_path,
                'vault_exists': vault_exists,
                'use_rest_api': obsidian_config.use_rest_api,
                'create_folders': obsidian_config.create_folders
            }
            if not vault_exists:
                diagnostics['obsidian_config']['warning'] = 'Vault directory does not exist (will be created)'
        except Exception as e:
            diagnostics['obsidian_config']['status'] = 'invalid'
            diagnostics['obsidian_config']['error'] = str(e)

        # Check dependencies
        try:
            import pyzotero
            diagnostics['dependencies']['status'] = 'valid'
            diagnostics['dependencies']['details'] = {
                'pyzotero': True,
                'version': getattr(pyzotero, '__version__', 'unknown')
            }
        except ImportError:
            diagnostics['dependencies']['status'] = 'invalid'
            diagnostics['dependencies']['error'] = 'pyzotero not installed. Run: pip install pyzotero>=1.5.0'

        return diagnostics

    def create_sample_config(self, output_path: Path) -> None:
        """
        Create a sample YAML configuration file.

        Args:
            output_path: Path where to save the sample config
        """
        sample_config = {
            'zotero': {
                'library_id': 'YOUR_LIBRARY_ID',
                'library_type': 'user',  # or 'group'
                'api_key': 'YOUR_API_KEY',
                'cache_ttl': 86400
            },
            'obsidian': {
                'vault_path': '~/Documents/Obsidian/Vault',
                'create_folders': True,
                'use_rest_api': False,
                'rest_api_port': 27123
            },
            'batch': {
                'batch_size': 50,
                'checkpoint_interval': 10,
                'cache_ttl': 86400,
                'max_retries': 3,
                'retry_delay': 5
            }
        }

        with open(output_path, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)


def get_default_config_manager() -> ZoteroConfigManager:
    """
    Get default configuration manager checking standard config locations.

    Returns:
        ZoteroConfigManager instance
    """
    # Check for config file in standard locations
    config_paths = [
        Path.cwd() / 'zotero_config.yml',
        Path.cwd() / 'config' / 'zotero.yml',
        Path.home() / '.scholarsquill' / 'zotero_config.yml'
    ]

    for path in config_paths:
        if path.exists():
            return ZoteroConfigManager(config_path=path)

    # No config file found, use environment variables only
    return ZoteroConfigManager()
