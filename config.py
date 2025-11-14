"""
Configuration management system for biometric security research.
Centralized configuration with environment variable support and validation.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class BiometricConfig:
    """Face recognition configuration"""
    model_name: str = 'Facenet'  # Options: 'Facenet', 'VGG-Face', 'OpenFace', 'DeepFace'
    detector_backend: str = 'opencv'  # Options: 'opencv', 'ssd', 'mtcnn', 'retinaface'
    similarity_threshold: float = 0.6
    min_face_size: tuple = (100, 100)
    enforce_detection: bool = False


@dataclass
class LivenessConfig:
    """Liveness detection configuration"""
    use_dlib: bool = True
    ear_threshold: float = 0.25
    blink_frames: int = 2
    texture_entropy_threshold: float = 5.0
    flash_test_duration: float = 2.0
    flash_difference_threshold: float = 10.0
    edge_density_min: float = 0.1
    edge_density_max: float = 0.3
    color_diversity_threshold: float = 15.0


@dataclass
class AttackConfig:
    """Attack generation configuration"""
    output_dir: str = 'data/attack_samples'
    photo_glare_intensity: float = 0.2
    mask_smoothing: int = 15
    degraded_quality: int = 20
    degraded_scale_factor: int = 4


@dataclass
class SecurityConfig:
    """Security hardening configuration"""
    max_file_size_mb: int = 50
    allowed_extensions: tuple = ('.jpg', '.jpeg', '.png', '.bmp')
    enable_encryption: bool = True
    encryption_algorithm: str = 'AES-256-GCM'
    secure_delete: bool = True
    rate_limit_attempts: int = 5
    rate_limit_window_seconds: int = 60


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    batch_size: int = 1
    num_workers: int = 1
    enable_gpu: bool = False
    memory_limit_mb: int = 4096
    cache_embeddings: bool = True
    frame_skip: int = 5  # For real-time processing


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file: str = 'logs/biometric_security.log'
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    max_bytes: int = 10485760  # 10 MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


@dataclass
class PathsConfig:
    """Data paths configuration"""
    data_dir: str = 'data'
    enrolled_users_dir: str = 'data/enrolled_users'
    test_samples_dir: str = 'data/test_samples'
    attack_samples_dir: str = 'data/attack_samples'
    results_dir: str = 'data/results'
    models_dir: str = 'biometric/models'
    logs_dir: str = 'logs'


@dataclass
class SystemConfig:
    """Main system configuration"""
    biometric: BiometricConfig = field(default_factory=BiometricConfig)
    liveness: LivenessConfig = field(default_factory=LivenessConfig)
    attack: AttackConfig = field(default_factory=AttackConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)

    version: str = '2.0.0'
    environment: str = 'development'  # development, testing, production

    def __post_init__(self):
        """Load environment variables and validate configuration"""
        self._load_from_env()
        self._create_directories()

    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Biometric settings
        if os.getenv('BIOMETRIC_MODEL'):
            self.biometric.model_name = os.getenv('BIOMETRIC_MODEL')
        if os.getenv('BIOMETRIC_THRESHOLD'):
            self.biometric.similarity_threshold = float(os.getenv('BIOMETRIC_THRESHOLD'))

        # Security settings
        if os.getenv('MAX_FILE_SIZE_MB'):
            self.security.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB'))
        if os.getenv('ENABLE_ENCRYPTION'):
            self.security.enable_encryption = os.getenv('ENABLE_ENCRYPTION').lower() == 'true'

        # Performance settings
        if os.getenv('ENABLE_GPU'):
            self.performance.enable_gpu = os.getenv('ENABLE_GPU').lower() == 'true'
        if os.getenv('MEMORY_LIMIT_MB'):
            self.performance.memory_limit_mb = int(os.getenv('MEMORY_LIMIT_MB'))

        # Logging settings
        if os.getenv('LOG_LEVEL'):
            self.logging.level = os.getenv('LOG_LEVEL')

        # Environment
        if os.getenv('ENVIRONMENT'):
            self.environment = os.getenv('ENVIRONMENT')

    def _create_directories(self):
        """Create required directories if they don't exist"""
        directories = [
            self.paths.data_dir,
            self.paths.enrolled_users_dir,
            self.paths.test_samples_dir,
            self.paths.attack_samples_dir,
            self.paths.results_dir,
            self.paths.models_dir,
            self.paths.logs_dir
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)

    def to_json(self, filepath: Optional[str] = None) -> str:
        """
        Export configuration to JSON

        Args:
            filepath: Optional path to save JSON file

        Returns:
            str: JSON string
        """
        config_dict = self.to_dict()
        json_str = json.dumps(config_dict, indent=2)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)

        return json_str

    @classmethod
    def from_json(cls, filepath: str) -> 'SystemConfig':
        """
        Load configuration from JSON file

        Args:
            filepath: Path to JSON configuration file

        Returns:
            SystemConfig: Loaded configuration
        """
        with open(filepath, 'r') as f:
            config_dict = json.load(f)

        return cls(
            biometric=BiometricConfig(**config_dict.get('biometric', {})),
            liveness=LivenessConfig(**config_dict.get('liveness', {})),
            attack=AttackConfig(**config_dict.get('attack', {})),
            security=SecurityConfig(**config_dict.get('security', {})),
            performance=PerformanceConfig(**config_dict.get('performance', {})),
            logging=LoggingConfig(**config_dict.get('logging', {})),
            paths=PathsConfig(**config_dict.get('paths', {})),
            version=config_dict.get('version', '2.0.0'),
            environment=config_dict.get('environment', 'development')
        )

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration settings

        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []

        # Validate biometric config
        if self.biometric.model_name not in ['Facenet', 'VGG-Face', 'OpenFace', 'DeepFace', 'ArcFace']:
            errors.append(f"Invalid model_name: {self.biometric.model_name}")

        if not 0 < self.biometric.similarity_threshold < 1:
            errors.append(f"similarity_threshold must be between 0 and 1: {self.biometric.similarity_threshold}")

        # Validate liveness config
        if not 0 < self.liveness.ear_threshold < 1:
            errors.append(f"ear_threshold must be between 0 and 1: {self.liveness.ear_threshold}")

        # Validate security config
        if self.security.max_file_size_mb < 1:
            errors.append(f"max_file_size_mb must be positive: {self.security.max_file_size_mb}")

        # Validate performance config
        if self.performance.batch_size < 1:
            errors.append(f"batch_size must be positive: {self.performance.batch_size}")

        # Validate logging config
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level not in valid_log_levels:
            errors.append(f"Invalid log level: {self.logging.level}. Must be one of {valid_log_levels}")

        return (len(errors) == 0, errors)


# Global configuration instance
_config: Optional[SystemConfig] = None


def get_config() -> SystemConfig:
    """
    Get global configuration instance (singleton pattern)

    Returns:
        SystemConfig: Global configuration
    """
    global _config
    if _config is None:
        _config = SystemConfig()
    return _config


def load_config(filepath: str) -> SystemConfig:
    """
    Load configuration from file and set as global config

    Args:
        filepath: Path to configuration file

    Returns:
        SystemConfig: Loaded configuration
    """
    global _config
    _config = SystemConfig.from_json(filepath)
    return _config


def reset_config():
    """Reset configuration to default"""
    global _config
    _config = SystemConfig()
    return _config


# Convenience function for accessing config
config = get_config
