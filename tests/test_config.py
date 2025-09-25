"""
Tests for configuration classes
"""

import pytest
import os
from unittest.mock import patch
from src.config import ServerConfig, ProcessingConfig, TemplateConfig, ConfigManager


class TestServerConfig:
    """Test ServerConfig class"""
    
    def test_server_config_defaults(self):
        """Test ServerConfig with default values"""
        config = ServerConfig()
        
        assert config.default_output_dir == "literature-notes"
        assert config.default_templates_dir == "templates"
        assert config.max_file_size_mb == 50
        assert config.batch_size_limit == 100
        assert config.enable_caching is True
        assert config.log_level == "INFO"
    
    def test_server_config_validation(self):
        """Test ServerConfig validation"""
        config = ServerConfig()
        assert config.validate() is True
        
        # Test invalid values
        config.max_file_size_mb = -1
        with pytest.raises(ValueError, match="max_file_size_mb must be positive"):
            config.validate()
        
        config.max_file_size_mb = 50
        config.batch_size_limit = 0
        with pytest.raises(ValueError, match="batch_size_limit must be positive"):
            config.validate()
        
        config.batch_size_limit = 100
        config.log_level = "INVALID"
        with pytest.raises(ValueError, match="Invalid log_level"):
            config.validate()
    
    @patch.dict(os.environ, {
        'SQ_OUTPUT_DIR': 'custom-output',
        'SQ_MAX_FILE_SIZE_MB': '100',
        'SQ_ENABLE_CACHING': 'false',
        'SQ_LOG_LEVEL': 'DEBUG'
    })
    def test_server_config_from_env(self):
        """Test ServerConfig creation from environment variables"""
        config = ServerConfig.from_env()
        
        assert config.default_output_dir == "custom-output"
        assert config.max_file_size_mb == 100
        assert config.enable_caching is False
        assert config.log_level == "DEBUG"


class TestProcessingConfig:
    """Test ProcessingConfig class"""
    
    def test_processing_config_defaults(self):
        """Test ProcessingConfig with default values"""
        config = ProcessingConfig()
        
        assert config.pdf_timeout_seconds == 30
        assert config.max_text_length == 1000000
        assert config.enable_ocr is False
        assert config.ocr_language == "eng"
    
    @patch.dict(os.environ, {
        'SQ_PDF_TIMEOUT': '60',
        'SQ_ENABLE_OCR': 'true',
        'SQ_OCR_LANGUAGE': 'fra'
    })
    def test_processing_config_from_env(self):
        """Test ProcessingConfig creation from environment variables"""
        config = ProcessingConfig.from_env()
        
        assert config.pdf_timeout_seconds == 60
        assert config.enable_ocr is True
        assert config.ocr_language == "fra"


class TestTemplateConfig:
    """Test TemplateConfig class"""
    
    def test_template_config_defaults(self):
        """Test TemplateConfig with default values"""
        config = TemplateConfig()
        
        assert config.template_cache_size == 50
        assert config.custom_templates_dir is None
    
    @patch.dict(os.environ, {
        'SQ_TEMPLATE_CACHE_SIZE': '100',
        'SQ_CUSTOM_TEMPLATES_DIR': '/custom/templates'
    })
    def test_template_config_from_env(self):
        """Test TemplateConfig creation from environment variables"""
        config = TemplateConfig.from_env()
        
        assert config.template_cache_size == 100
        assert config.custom_templates_dir == "/custom/templates"


class TestConfigManager:
    """Test ConfigManager class"""
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization"""
        manager = ConfigManager()
        
        assert isinstance(manager.server, ServerConfig)
        assert isinstance(manager.processing, ProcessingConfig)
        assert isinstance(manager.template, TemplateConfig)
    
    def test_get_templates_dir(self):
        """Test get_templates_dir method"""
        manager = ConfigManager()
        
        # Test default templates directory
        templates_dir = manager.get_templates_dir()
        assert templates_dir.name == "templates"
        
        # Test custom templates directory
        manager.template.custom_templates_dir = "/custom/templates"
        custom_dir = manager.get_templates_dir()
        assert str(custom_dir) == "/custom/templates"
    
    def test_get_output_dir(self):
        """Test get_output_dir method"""
        manager = ConfigManager()
        
        # Test default output directory
        output_dir = manager.get_output_dir()
        assert str(output_dir) == "literature-notes"
        
        # Test custom output directory
        custom_dir = manager.get_output_dir("/custom/output")
        assert str(custom_dir) == "/custom/output"
    
    def test_is_file_size_valid(self):
        """Test is_file_size_valid method"""
        manager = ConfigManager()
        
        # Test with non-existent file
        assert manager.is_file_size_valid("nonexistent.pdf") is False