"""Tests for configuration system"""

import pytest
import json
from config import SystemConfig, BiometricConfig, get_config, reset_config


class TestSystemConfig:
    """Test system configuration"""

    def test_default_config(self):
        """Test default configuration creation"""
        config = SystemConfig()

        assert config.version == '2.0.0'
        assert config.environment in ['development', 'testing', 'production']
        assert isinstance(config.biometric, BiometricConfig)

    def test_config_validation(self):
        """Test configuration validation"""
        config = SystemConfig()

        is_valid, errors = config.validate()

        assert is_valid is True
        assert len(errors) == 0

    def test_invalid_config(self):
        """Test invalid configuration detection"""
        config = SystemConfig()

        # Set invalid values
        config.biometric.similarity_threshold = 1.5  # Should be 0-1
        config.logging.level = 'INVALID'

        is_valid, errors = config.validate()

        assert is_valid is False
        assert len(errors) > 0

    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        config = SystemConfig()

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert 'biometric' in config_dict
        assert 'logging' in config_dict
        assert 'version' in config_dict

    def test_config_to_json(self, temp_dir):
        """Test exporting configuration to JSON"""
        import os

        config = SystemConfig()
        json_path = os.path.join(temp_dir, 'config.json')

        config.to_json(json_path)

        assert os.path.exists(json_path)

        # Load and verify
        with open(json_path, 'r') as f:
            loaded_data = json.load(f)

        assert loaded_data['version'] == config.version

    def test_config_from_json(self, temp_dir):
        """Test loading configuration from JSON"""
        import os

        # Create config file
        config_data = {
            'version': '2.0.0',
            'environment': 'testing',
            'biometric': {
                'model_name': 'Facenet',
                'similarity_threshold': 0.7
            },
            'logging': {
                'level': 'DEBUG'
            }
        }

        json_path = os.path.join(temp_dir, 'config.json')
        with open(json_path, 'w') as f:
            json.dump(config_data, f)

        # Load config
        config = SystemConfig.from_json(json_path)

        assert config.version == '2.0.0'
        assert config.environment == 'testing'
        assert config.biometric.similarity_threshold == 0.7

    def test_environment_variables(self, monkeypatch):
        """Test loading from environment variables"""
        monkeypatch.setenv('BIOMETRIC_MODEL', 'VGG-Face')
        monkeypatch.setenv('BIOMETRIC_THRESHOLD', '0.8')
        monkeypatch.setenv('LOG_LEVEL', 'ERROR')

        config = SystemConfig()

        assert config.biometric.model_name == 'VGG-Face'
        assert config.biometric.similarity_threshold == 0.8
        assert config.logging.level == 'ERROR'

    def test_directory_creation(self, temp_dir, monkeypatch):
        """Test that required directories are created"""
        import os

        monkeypatch.setattr('config.PathsConfig.data_dir', temp_dir)

        config = SystemConfig()

        # Directories should be created
        assert os.path.exists(config.paths.data_dir)

    def test_singleton_config(self):
        """Test configuration singleton pattern"""
        reset_config()

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2


class TestBiometricConfig:
    """Test biometric configuration"""

    def test_default_biometric_config(self):
        """Test default biometric settings"""
        config = BiometricConfig()

        assert config.model_name == 'Facenet'
        assert config.detector_backend == 'opencv'
        assert 0 < config.similarity_threshold < 1
        assert isinstance(config.min_face_size, tuple)

    def test_custom_biometric_config(self):
        """Test custom biometric settings"""
        config = BiometricConfig(
            model_name='VGG-Face',
            similarity_threshold=0.75
        )

        assert config.model_name == 'VGG-Face'
        assert config.similarity_threshold == 0.75
