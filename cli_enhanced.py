"""
Enhanced CLI with progress bars, better error handling, and improved UX
"""

import argparse
import sys
import os
from typing import Optional
from pathlib import Path

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Warning: tqdm not available. Install with: pip install tqdm")

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from utils.logger import get_logger
from utils.security import get_validator, get_rate_limiter, get_audit_logger
from utils.performance import get_performance_monitor, optimize_memory

# Import existing modules
from biometric.face_recognition import FaceAuthenticator, RealtimeFaceAuth
from biometric.fingerprint_matcher import FingerprintMatcher
from attacks.presentation_attacks import PresentationAttacks
from attacks.adversarial_attacks import AdversarialAttacker
from attacks.deepfake_generator import LightweightDeepfake
from defenses.liveness_detection import LivenessDetector, AntiSpoofingSystem
from evaluation.vulnerability_tester import VulnerabilityTester
from reporting.enhanced_report import EnhancedReportGenerator

# Initialize
config = get_config()
logger = get_logger(__name__)
validator = get_validator()
rate_limiter = get_rate_limiter()
audit_logger = get_audit_logger()
perf_monitor = get_performance_monitor()


def print_banner():
    """Print enhanced application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🔒 Biometric Security Research System v2.0                        ║
║   Enhanced with ML, Security Hardening & Interactive Reports        ║
║                                                                      ║
║   Features: Face + Fingerprint + Liveness + Advanced Attacks        ║
║   Security: Input Validation + Rate Limiting + Audit Logging        ║
║                                                                      ║
║   For Security Research and Educational Purposes                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    logger.info("Biometric Security System started")


def validate_and_check_file(filepath: str, purpose: str) -> bool:
    """
    Validate file with security checks

    Args:
        filepath: Path to validate
        purpose: Description of what file is for

    Returns:
        bool: True if valid
    """
    is_valid, error = validator.validate_file_path(filepath)

    if not is_valid:
        logger.error(f"File validation failed for {purpose}: {error}")
        print(f"\n❌ Error: {error}")
        return False

    logger.info(f"File validated for {purpose}: {filepath}")
    return True


def check_rate_limit(user_id: str) -> bool:
    """
    Check rate limit for user

    Args:
        user_id: User identifier

    Returns:
        bool: True if allowed
    """
    allowed, retry_after = rate_limiter.is_allowed(user_id)

    if not allowed:
        logger.warning(f"Rate limit exceeded for {user_id}")
        print(f"\n⚠️  Rate limit exceeded. Please try again in {retry_after} seconds.")
        return False

    return True


def enroll_user_enhanced(args):
    """Enhanced user enrollment with validation and progress tracking"""
    print(f"\n{'='*70}")
    print(f"📝 ENROLLING USER: {args.user_id}")
    print(f"{'='*70}")

    # Validate user ID
    is_valid, error = validator.validate_user_id(args.user_id)
    if not is_valid:
        print(f"\n❌ Error: {error}")
        logger.error(f"Invalid user ID: {args.user_id} - {error}")
        return

    # Check rate limit
    if not check_rate_limit(args.user_id):
        return

    perf_monitor.log_performance_snapshot("enrollment_start")

    if args.modality == 'face':
        auth = FaceAuthenticator(
            model_name=config.biometric.model_name,
            detector=config.biometric.detector_backend
        )

        if args.load_model and os.path.exists(args.load_model):
            logger.info(f"Loading existing model: {args.load_model}")
            auth.load_model(args.load_model)

        # Get image paths
        if args.images:
            images = args.images.split(',')
        elif args.image_dir:
            images = [
                os.path.join(args.image_dir, f)
                for f in os.listdir(args.image_dir)
                if f.endswith(('.jpg', '.png', '.jpeg'))
            ]
        else:
            print("\n❌ Error: Please provide --images or --image-dir")
            return

        # Validate all images
        print(f"\n🔍 Validating {len(images)} images...")
        valid_images = []

        if TQDM_AVAILABLE:
            image_iter = tqdm(images, desc="Validating images", unit="img")
        else:
            image_iter = images

        for img_path in image_iter:
            if validate_and_check_file(img_path, "enrollment image"):
                valid_images.append(img_path)

        if not valid_images:
            print("\n❌ Error: No valid images found")
            return

        print(f"\n✅ {len(valid_images)}/{len(images)} images validated")
        print(f"\n🚀 Processing enrollment...")

        # Enroll with progress tracking
        success = auth.enroll_user(args.user_id, valid_images)

        if success:
            save_path = args.save_model or config.paths.enrolled_users_dir + '/face_auth.pkl'
            auth.save_model(save_path)

            # Audit log
            audit_logger.log_enrollment(args.user_id, True, 'face')

            print(f"\n✅ SUCCESS! User enrolled and saved to {save_path}")
            print(f"📊 Enrolled with {len(valid_images)} face samples")

        else:
            audit_logger.log_enrollment(args.user_id, False, 'face')
            print("\n❌ Enrollment failed")

    elif args.modality == 'fingerprint':
        matcher = FingerprintMatcher()

        if args.load_model and os.path.exists(args.load_model):
            matcher.load_database(args.load_model)

        if not args.image:
            print("\n❌ Error: Please provide --image for fingerprint enrollment")
            return

        if not validate_and_check_file(args.image, "fingerprint image"):
            return

        success = matcher.enroll_fingerprint(args.user_id, args.image)

        if success:
            save_path = args.save_model or config.paths.enrolled_users_dir + '/fingerprint_db.pkl'
            matcher.save_database(save_path)

            audit_logger.log_enrollment(args.user_id, True, 'fingerprint')

            print(f"\n✅ SUCCESS! Fingerprint enrolled and saved to {save_path}")
        else:
            audit_logger.log_enrollment(args.user_id, False, 'fingerprint')
            print("\n❌ Enrollment failed")

    perf_monitor.log_performance_snapshot("enrollment_complete")
    optimize_memory()


def enhanced_attack_generation(args):
    """Generate attacks with new adversarial methods"""
    print(f"\n{'='*70}")
    print("🎯 GENERATING ATTACKS")
    print(f"{'='*70}")

    if not args.image:
        print("\n❌ Error: Please provide --image")
        return

    if not validate_and_check_file(args.image, "attack source image"):
        return

    # Standard attacks
    attacks = PresentationAttacks(output_dir=config.attack.output_dir)

    # Adversarial attacks
    adv_attacker = AdversarialAttacker()

    attack_types = args.attack_types.split(',') if args.attack_types else ['photo', 'mask', 'degraded']

    print(f"\n🚀 Generating {len(attack_types)} attack types...")

    results = {}

    if TQDM_AVAILABLE:
        attack_iter = tqdm(attack_types, desc="Generating attacks", unit="attack")
    else:
        attack_iter = attack_types

    for attack_type in attack_iter:
        try:
            if attack_type == 'photo':
                path = attacks.photo_attack(args.image)
                results['photo'] = path
            elif attack_type == 'mask':
                path = attacks.mask_attack_simulation(args.image)
                results['mask'] = path
            elif attack_type == 'degraded':
                path = attacks.degraded_quality_attack(args.image)
                results['degraded'] = path
            elif attack_type == 'adversarial':
                adv_results = adv_attacker.batch_generate_adversarial_attacks(args.image)
                results.update(adv_results)
            elif attack_type == 'patch':
                path = adv_attacker.generate_adversarial_patch(args.image)
                results['patch'] = path
            elif attack_type == 'fgsm':
                path = adv_attacker.generate_fgsm_attack(args.image)
                results['fgsm'] = path

        except Exception as e:
            logger.error(f"Failed to generate {attack_type} attack: {e}")
            print(f"\n⚠️  Failed to generate {attack_type}: {e}")

    print(f"\n✅ Generated {len(results)} attack samples:")
    for attack_type, path in results.items():
        print(f"    ✓ {attack_type}: {path}")


def generate_enhanced_report(args):
    """Generate enhanced interactive report"""
    print(f"\n{'='*70}")
    print("📊 GENERATING ENHANCED INTERACTIVE REPORT")
    print(f"{'='*70}")

    if not args.results_file or not os.path.exists(args.results_file):
        print(f"\n❌ Error: Results file not found: {args.results_file}")
        return

    print("\n🎨 Creating interactive visualizations...")

    report_gen = EnhancedReportGenerator(results_file=args.results_file)
    output_path = args.output or 'data/results/enhanced_security_report.html'

    report_gen.generate_interactive_dashboard(output_path)

    print(f"\n✅ Enhanced report generated: {output_path}")
    print("\n💡 Tip: Open the report in a web browser to view interactive charts!")


def show_system_status():
    """Show system status and configuration"""
    print(f"\n{'='*70}")
    print("ℹ️  SYSTEM STATUS")
    print(f"{'='*70}")

    print(f"\n📦 Configuration:")
    print(f"  Version: {config.version}")
    print(f"  Environment: {config.environment}")
    print(f"  Biometric Model: {config.biometric.model_name}")
    print(f"  Detector: {config.biometric.detector_backend}")
    print(f"  Threshold: {config.biometric.similarity_threshold}")

    print(f"\n🔒 Security:")
    print(f"  Encryption: {'Enabled' if config.security.enable_encryption else 'Disabled'}")
    print(f"  Max File Size: {config.security.max_file_size_mb}MB")
    print(f"  Rate Limit: {config.security.rate_limit_attempts} attempts / {config.security.rate_limit_window_seconds}s")

    print(f"\n⚡ Performance:")
    mem = perf_monitor.get_memory_usage()
    cpu = perf_monitor.get_cpu_usage()
    print(f"  Memory Usage: {mem['rss_mb']:.1f}MB ({mem['percent']:.1f}%)")
    print(f"  CPU Usage: {cpu:.1f}%")
    print(f"  GPU Enabled: {'Yes' if config.performance.enable_gpu else 'No'}")
    print(f"  Cache: {'Enabled' if config.performance.cache_embeddings else 'Disabled'}")

    print(f"\n📁 Paths:")
    print(f"  Data Directory: {config.paths.data_dir}")
    print(f"  Enrolled Users: {config.paths.enrolled_users_dir}")
    print(f"  Results: {config.paths.results_dir}")


def main():
    """Enhanced main entry point"""
    parser = argparse.ArgumentParser(
        description='Biometric Security Research System v2.0 - Enhanced Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')

    # Enroll command
    enroll_parser = subparsers.add_parser('enroll', help='Enroll a new user')
    enroll_parser.add_argument('--user-id', required=True, help='User ID')
    enroll_parser.add_argument('--modality', choices=['face', 'fingerprint'], default='face')
    enroll_parser.add_argument('--images', help='Comma-separated image paths')
    enroll_parser.add_argument('--image-dir', help='Directory containing enrollment images')
    enroll_parser.add_argument('--image', help='Single image (for fingerprint)')
    enroll_parser.add_argument('--save-model', help='Path to save model')
    enroll_parser.add_argument('--load-model', help='Path to existing model to update')

    # Attack generation
    attack_parser = subparsers.add_parser('attack', help='Generate presentation/adversarial attacks')
    attack_parser.add_argument('--image', required=True, help='Genuine image')
    attack_parser.add_argument('--attack-types',
                              help='Comma-separated attack types (photo,mask,degraded,adversarial,patch,fgsm)')

    # Enhanced report generation
    report_parser = subparsers.add_parser('enhanced-report', help='Generate enhanced interactive report')
    report_parser.add_argument('--results-file', required=True, help='Path to results JSON')
    report_parser.add_argument('--output', help='Output path for HTML report')

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Execute command
    if args.command == 'status':
        show_system_status()
    elif args.command == 'enroll':
        enroll_user_enhanced(args)
    elif args.command == 'attack':
        enhanced_attack_generation(args)
    elif args.command == 'enhanced-report':
        generate_enhanced_report(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
