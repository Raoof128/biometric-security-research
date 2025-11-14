#!/usr/bin/env python3
"""
Example 8: Custom Configuration

This example demonstrates how to create and use custom configurations
for different deployment scenarios and use cases.
"""

import sys
import os
import argparse
from dataclasses import asdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SystemConfig, BiometricConfig, LivenessConfig, SecurityConfig,
    PerformanceConfig, get_config
)
from biometric.face_recognition import FaceAuthenticator
from utils.logger import get_logger
import json

# Initialize
logger = get_logger(__name__)


def create_high_security_config():
    """Create configuration for high-security deployment"""
    config = SystemConfig()

    # Strict biometric settings
    config.biometric.model_name = "Facenet512"  # Most accurate
    config.biometric.similarity_threshold = 0.5  # Conservative
    config.biometric.detector_backend = "retinaface"  # Best detector

    # Enable all liveness detection
    config.liveness.enable_blink_detection = True
    config.liveness.enable_texture_analysis = True
    config.liveness.enable_depth_analysis = True
    config.liveness.texture_threshold = 0.7  # Strict
    config.liveness.min_blinks = 3  # Require more blinks

    # Maximum security
    config.security.enable_rate_limit = True
    config.security.max_auth_attempts = 3  # Very strict
    config.security.rate_limit_window = 300  # 5 minutes
    config.security.encrypt_templates = True
    config.security.enable_audit_log = True
    config.security.secure_delete = True

    # Performance trade-offs for security
    config.performance.enable_gpu = True
    config.performance.cache_embeddings = False  # Disable for max security

    return config


def create_fast_performance_config():
    """Create configuration optimized for speed"""
    config = SystemConfig()

    # Fast model
    config.biometric.model_name = "OpenFace"  # Fastest
    config.biometric.similarity_threshold = 0.65  # Balanced
    config.biometric.detector_backend = "opencv"  # Fast detector

    # Minimal liveness (speed priority)
    config.liveness.enable_blink_detection = False
    config.liveness.enable_texture_analysis = True  # Fast method only
    config.liveness.texture_threshold = 0.6

    # Basic security
    config.security.enable_rate_limit = True
    config.security.max_auth_attempts = 10  # Lenient
    config.security.encrypt_templates = False  # Faster

    # Maximum performance
    config.performance.enable_gpu = True
    config.performance.cache_embeddings = True
    config.performance.cache_size = 2000  # Large cache
    config.performance.num_workers = 8  # Max parallelism

    return config


def create_balanced_config():
    """Create balanced configuration (recommended default)"""
    config = SystemConfig()

    # Good balance
    config.biometric.model_name = "Facenet"
    config.biometric.similarity_threshold = 0.6
    config.biometric.detector_backend = "mtcnn"

    # Moderate liveness
    config.liveness.enable_texture_analysis = True
    config.liveness.texture_threshold = 0.65

    # Standard security
    config.security.enable_rate_limit = True
    config.security.max_auth_attempts = 5
    config.security.encrypt_templates = True
    config.security.enable_audit_log = True

    # Good performance
    config.performance.cache_embeddings = True
    config.performance.cache_size = 1000

    return config


def create_edge_device_config():
    """Create configuration for resource-constrained edge devices"""
    config = SystemConfig()

    # Lightweight model
    config.biometric.model_name = "OpenFace"
    config.biometric.similarity_threshold = 0.65
    config.biometric.detector_backend = "opencv"

    # Minimal processing
    config.liveness.enable_blink_detection = False
    config.liveness.enable_texture_analysis = True
    config.liveness.texture_threshold = 0.6

    # Basic security
    config.security.enable_rate_limit = True
    config.security.max_auth_attempts = 5
    config.security.encrypt_templates = False  # Save CPU

    # Low resource usage
    config.performance.enable_gpu = False  # No GPU on edge
    config.performance.cache_embeddings = True
    config.performance.cache_size = 100  # Small cache
    config.performance.num_workers = 2  # Limited parallelism

    return config


def main():
    """Demonstrate custom configuration usage"""
    parser = argparse.ArgumentParser(description="Custom Configuration Example")
    parser.add_argument('--profile', type=str, default='balanced',
                       choices=['high-security', 'fast', 'balanced', 'edge'],
                       help='Configuration profile')
    parser.add_argument('--save', type=str, help='Save config to JSON file')
    parser.add_argument('--load', type=str, help='Load config from JSON file')
    parser.add_argument('--compare', action='store_true',
                       help='Compare all profiles')
    args = parser.parse_args()

    print("="*70)
    print("Example 8: Custom Configuration")
    print("="*70)

    if args.compare:
        # Compare all profiles
        print("\n📊 Comparing Configuration Profiles")
        print("-"*70)

        profiles = {
            'High Security': create_high_security_config(),
            'Fast Performance': create_fast_performance_config(),
            'Balanced': create_balanced_config(),
            'Edge Device': create_edge_device_config(),
        }

        # Comparison table
        print("\n{:<20} {:<15} {:<15} {:<15} {:<15}".format(
            "Setting", "High Security", "Fast Perf", "Balanced", "Edge Device"
        ))
        print("-"*70)

        comparisons = [
            ('Model', lambda c: c.biometric.model_name),
            ('Threshold', lambda c: f"{c.biometric.similarity_threshold:.2f}"),
            ('Detector', lambda c: c.biometric.detector_backend),
            ('Liveness', lambda c: "Multi" if c.liveness.enable_blink_detection else "Basic"),
            ('Rate Limit', lambda c: f"{c.security.max_auth_attempts} attempts"),
            ('Encryption', lambda c: "Yes" if c.security.encrypt_templates else "No"),
            ('Cache Size', lambda c: str(c.performance.cache_size)),
            ('GPU', lambda c: "Yes" if c.performance.enable_gpu else "No"),
        ]

        for setting_name, getter in comparisons:
            values = [getter(config) for config in profiles.values()]
            print("{:<20} {:<15} {:<15} {:<15} {:<15}".format(
                setting_name, *values
            ))

        print("\n💡 Profile Recommendations:")
        print("   • High Security: Banking, government, critical infrastructure")
        print("   • Fast Performance: High-throughput systems, user-facing apps")
        print("   • Balanced: General purpose, recommended default")
        print("   • Edge Device: IoT, embedded systems, mobile devices")

    elif args.load:
        # Load custom configuration
        print(f"\n📂 Loading configuration from: {args.load}")

        if not os.path.exists(args.load):
            print(f"   ❌ Error: File not found")
            return

        config = SystemConfig.from_json(args.load)
        print("   ✓ Configuration loaded")

    else:
        # Create specific profile
        print(f"\n⚙️  Creating '{args.profile}' configuration profile...")

        if args.profile == 'high-security':
            config = create_high_security_config()
            description = "Maximum security with multiple liveness checks"
        elif args.profile == 'fast':
            config = create_fast_performance_config()
            description = "Optimized for speed with minimal overhead"
        elif args.profile == 'balanced':
            config = create_balanced_config()
            description = "Balanced security and performance (recommended)"
        elif args.profile == 'edge':
            config = create_edge_device_config()
            description = "Low resource usage for edge devices"

        print(f"   Description: {description}")

    # Display configuration
    if not args.compare:
        print("\n📋 Configuration Details")
        print("-"*70)

        print("\n🔹 Biometric Settings:")
        print(f"   Model: {config.biometric.model_name}")
        print(f"   Threshold: {config.biometric.similarity_threshold}")
        print(f"   Detector: {config.biometric.detector_backend}")

        print("\n🔹 Liveness Detection:")
        print(f"   Blink Detection: {'Enabled' if config.liveness.enable_blink_detection else 'Disabled'}")
        print(f"   Texture Analysis: {'Enabled' if config.liveness.enable_texture_analysis else 'Disabled'}")
        print(f"   Texture Threshold: {config.liveness.texture_threshold}")

        print("\n🔹 Security:")
        print(f"   Rate Limiting: {'Enabled' if config.security.enable_rate_limit else 'Disabled'}")
        print(f"   Max Attempts: {config.security.max_auth_attempts}")
        print(f"   Template Encryption: {'Enabled' if config.security.encrypt_templates else 'Disabled'}")
        print(f"   Audit Logging: {'Enabled' if config.security.enable_audit_log else 'Disabled'}")

        print("\n🔹 Performance:")
        print(f"   GPU Acceleration: {'Enabled' if config.performance.enable_gpu else 'Disabled'}")
        print(f"   Embedding Cache: {'Enabled' if config.performance.cache_embeddings else 'Disabled'}")
        print(f"   Cache Size: {config.performance.cache_size}")
        print(f"   Workers: {config.performance.num_workers}")

        # Validate configuration
        print("\n🔍 Validating configuration...")
        is_valid, errors = config.validate()

        if is_valid:
            print("   ✓ Configuration is valid")
        else:
            print("   ❌ Configuration has errors:")
            for error in errors:
                print(f"      - {error}")

        # Test configuration
        print("\n🧪 Testing configuration...")
        print("   Creating authenticator with custom config...")

        try:
            auth = FaceAuthenticator(
                model_name=config.biometric.model_name,
                detector=config.biometric.detector_backend
            )
            print("   ✓ Authenticator initialized successfully")

            # Display expected characteristics
            print("\n📈 Expected Characteristics:")

            if args.profile == 'high-security':
                print("   • Highest accuracy and security")
                print("   • Slower authentication (~300-400ms)")
                print("   • Higher memory usage (~2GB)")
                print("   • Best protection against attacks")

            elif args.profile == 'fast':
                print("   • Fastest authentication (~100-150ms)")
                print("   • Lower memory usage (~600MB)")
                print("   • Good accuracy (96-97%)")
                print("   • Basic attack protection")

            elif args.profile == 'balanced':
                print("   • Good accuracy (99%)")
                print("   • Fast authentication (~200ms)")
                print("   • Moderate memory usage (~1.4GB)")
                print("   • Good attack protection")

            elif args.profile == 'edge':
                print("   • Minimal resource usage (~400MB)")
                print("   • Fast on CPU (~150ms)")
                print("   • Acceptable accuracy (96%)")
                print("   • Basic security features")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

        # Save configuration
        if args.save:
            print(f"\n💾 Saving configuration to: {args.save}")
            config.to_json(args.save)
            print("   ✓ Configuration saved")

            print("\n   To use this configuration:")
            print(f"   1. Load in code: config = SystemConfig.from_json('{args.save}')")
            print(f"   2. Or set env: export CONFIG_FILE='{args.save}'")

    # Usage examples
    print("\n" + "="*70)
    print("Usage Examples")
    print("="*70)

    print("\n# Compare all profiles")
    print("python examples/08_custom_configuration.py --compare")

    print("\n# Create and save high-security config")
    print("python examples/08_custom_configuration.py \\")
    print("  --profile high-security \\")
    print("  --save configs/high_security.json")

    print("\n# Load custom config")
    print("python examples/08_custom_configuration.py \\")
    print("  --load configs/my_config.json")

    print("\n# Use in code")
    print("""
from config import SystemConfig
config = SystemConfig.from_json('configs/high_security.json')

from biometric.face_recognition import FaceAuthenticator
auth = FaceAuthenticator(
    model_name=config.biometric.model_name,
    detector=config.biometric.detector_backend
)
""")

    print("\n" + "="*70)
    print("Next Steps:")
    print("1. Create custom config for your use case")
    print("2. Test with your data")
    print("3. Run: python examples/09_security_features.py")
    print("4. Tune parameters based on results")
    print("="*70)


if __name__ == "__main__":
    main()
