"""
Custom exceptions for Zotero integration.
"""


class ZoteroError(Exception):
    """Base exception for all Zotero-related errors."""
    pass


class ZoteroAuthenticationError(ZoteroError):
    """Raised when Zotero API authentication fails."""

    def __init__(self, message="Invalid Zotero API credentials"):
        self.message = message
        super().__init__(self.message)


class ZoteroRateLimitError(ZoteroError):
    """Raised when Zotero API rate limit is exceeded."""

    def __init__(self, retry_after=None):
        self.retry_after = retry_after
        msg = "Zotero API rate limit exceeded"
        if retry_after:
            msg += f". Retry after {retry_after} seconds"
        super().__init__(msg)


class ZoteroItemNotFoundError(ZoteroError):
    """Raised when requested Zotero item is not found."""

    def __init__(self, item_key):
        self.item_key = item_key
        super().__init__(f"Zotero item not found: {item_key}")


class ZoteroCollectionNotFoundError(ZoteroError):
    """Raised when requested Zotero collection is not found."""

    def __init__(self, collection_id):
        self.collection_id = collection_id
        super().__init__(f"Zotero collection not found: {collection_id}")


class ZoteroNetworkError(ZoteroError):
    """Raised when network connection to Zotero API fails."""

    def __init__(self, original_error=None):
        self.original_error = original_error
        msg = "Network error connecting to Zotero API"
        if original_error:
            msg += f": {str(original_error)}"
        super().__init__(msg)


class ZoteroInvalidLibraryTypeError(ZoteroError):
    """Raised when library type is invalid (must be 'user' or 'group')."""

    def __init__(self, library_type):
        self.library_type = library_type
        super().__init__(
            f"Invalid library type: {library_type}. Must be 'user' or 'group'"
        )


class ObsidianError(Exception):
    """Base exception for Obsidian-related errors."""
    pass


class ObsidianVaultNotFoundError(ObsidianError):
    """Raised when Obsidian vault directory does not exist."""

    def __init__(self, vault_path):
        self.vault_path = vault_path
        super().__init__(f"Obsidian vault not found: {vault_path}")


class ObsidianWriteError(ObsidianError):
    """Raised when writing to Obsidian vault fails."""

    def __init__(self, file_path, original_error=None):
        self.file_path = file_path
        self.original_error = original_error
        msg = f"Failed to write Obsidian note: {file_path}"
        if original_error:
            msg += f" - {str(original_error)}"
        super().__init__(msg)


class CitekeyCollisionError(Exception):
    """Raised when citekey collision cannot be resolved."""

    def __init__(self, citekey, attempts):
        self.citekey = citekey
        self.attempts = attempts
        super().__init__(
            f"Citekey collision unresolved after {attempts} attempts: {citekey}"
        )


class BatchProcessingError(Exception):
    """Base exception for batch processing errors."""
    pass


class CheckpointError(BatchProcessingError):
    """Raised when checkpoint save/load fails."""

    def __init__(self, checkpoint_path, operation, original_error=None):
        self.checkpoint_path = checkpoint_path
        self.operation = operation
        self.original_error = original_error
        msg = f"Checkpoint {operation} failed: {checkpoint_path}"
        if original_error:
            msg += f" - {str(original_error)}"
        super().__init__(msg)


class CacheError(Exception):
    """Base exception for cache-related errors."""
    pass


class CacheReadError(CacheError):
    """Raised when reading from cache fails."""

    def __init__(self, cache_key, original_error=None):
        self.cache_key = cache_key
        self.original_error = original_error
        msg = f"Failed to read cache for key: {cache_key}"
        if original_error:
            msg += f" - {str(original_error)}"
        super().__init__(msg)


class CacheWriteError(CacheError):
    """Raised when writing to cache fails."""

    def __init__(self, cache_key, original_error=None):
        self.cache_key = cache_key
        self.original_error = original_error
        msg = f"Failed to write cache for key: {cache_key}"
        if original_error:
            msg += f" - {str(original_error)}"
        super().__init__(msg)


class ConfigurationError(Exception):
    """Base exception for configuration errors."""
    pass


class MissingConfigError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(self, config_key, suggestion=None):
        self.config_key = config_key
        self.suggestion = suggestion
        msg = f"Missing required configuration: {config_key}"
        if suggestion:
            msg += f"\n{suggestion}"
        super().__init__(msg)


class InvalidConfigError(ConfigurationError):
    """Raised when configuration value is invalid."""

    def __init__(self, config_key, value, reason):
        self.config_key = config_key
        self.value = value
        self.reason = reason
        super().__init__(
            f"Invalid configuration for {config_key}='{value}': {reason}"
        )


class TemplateError(Exception):
    """Base exception for template rendering errors."""
    pass


class TemplateNotFoundError(TemplateError):
    """Raised when requested template is not found."""

    def __init__(self, template_name):
        self.template_name = template_name
        super().__init__(f"Template not found: {template_name}")


class TemplateRenderError(TemplateError):
    """Raised when template rendering fails."""

    def __init__(self, template_name, original_error=None):
        self.template_name = template_name
        self.original_error = original_error
        msg = f"Template rendering failed: {template_name}"
        if original_error:
            msg += f" - {str(original_error)}"
        super().__init__(msg)
