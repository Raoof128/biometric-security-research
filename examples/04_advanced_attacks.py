#!/usr/bin/env python3
"""
Example 4: Advanced Adversarial Attacks

This example demonstrates how to generate sophisticated adversarial attacks
that can fool biometric authentication systems.
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from attacks.adversarial_attacks import AdversarialAttacker
from biometric.face_recognition import FaceAuthenticator
from config import get_config
from utils.logger import get_logger
import cv2

# Initialize
logger = get_logger(__name__)
config = get_config()


def main():
    """Generate and test adversarial attacks"""
    parser = argparse.ArgumentParser(description="Advanced Adversarial Attacks Example")
    parser.add_argument('--image', type=str, default='data/examples/alice_1.jpg',
                       help='Path to target image')
    parser.add_argument('--attack-type', type=str, default='all',
                       choices=['fgsm', 'patch', 'glasses', 'pixel', 'morphing', 'all'],
                       help='Type of adversarial attack')
    parser.add_argument('--output-dir', type=str, default='data/attack_samples/adversarial',
                       help='Output directory for attack samples')
    args = parser.parse_args()

    print("="*70)
    print("Example 4: Advanced Adversarial Attacks")
    print("="*70)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize attacker
    print("\n⚙️  Initializing adversarial attacker...")
    attacker = AdversarialAttacker(
        model_name=config.biometric.model_name
    )

    # Check if image exists
    if not os.path.exists(args.image):
        print(f"\n⚠️  Warning: Image not found: {args.image}")
        print("   Please provide a valid image path")
        return

    print(f"\n🎯 Target image: {args.image}")

    # Generate attacks
    attacks_to_run = []
    if args.attack_type == 'all':
        attacks_to_run = ['fgsm', 'patch', 'glasses', 'pixel', 'morphing']
    else:
        attacks_to_run = [args.attack_type]

    print(f"\n🔨 Generating {len(attacks_to_run)} attack type(s)...")
    print("-" * 70)

    results = {}

    for attack_type in attacks_to_run:
        print(f"\n📍 Attack: {attack_type.upper()}")

        try:
            if attack_type == 'fgsm':
                # Fast Gradient Sign Method
                print("   Method: Fast Gradient Sign Method (FGSM)")
                print("   Description: Single-step gradient-based attack")
                attacked_img = attacker.generate_fgsm_attack(
                    args.image,
                    epsilon=0.05
                )
                output_path = os.path.join(args.output_dir, f'fgsm_attack.jpg')

            elif attack_type == 'patch':
                # Adversarial Patch
                print("   Method: Adversarial Patch")
                print("   Description: Optimized patch overlay attack")
                attacked_img = attacker.generate_adversarial_patch(
                    args.image,
                    patch_size=(50, 50),
                    iterations=100
                )
                output_path = os.path.join(args.output_dir, f'patch_attack.jpg')

            elif attack_type == 'glasses':
                # Adversarial Glasses
                print("   Method: Adversarial Glasses")
                print("   Description: Glasses-based physical attack")
                attacked_img = attacker.generate_glasses_attack(
                    args.image,
                    iterations=50
                )
                output_path = os.path.join(args.output_dir, f'glasses_attack.jpg')

            elif attack_type == 'pixel':
                # Pixel Attack
                print("   Method: One-Pixel Attack")
                print("   Description: Minimal perturbation attack")
                attacked_img = attacker.generate_pixel_attack(
                    args.image,
                    num_pixels=10,
                    iterations=50
                )
                output_path = os.path.join(args.output_dir, f'pixel_attack.jpg')

            elif attack_type == 'morphing':
                # Face Morphing
                print("   Method: Face Morphing")
                print("   Description: Blend two face images")
                # For morphing, we need a second image
                # Try to find another image in the same directory
                img_dir = os.path.dirname(args.image)
                other_images = [f for f in os.listdir(img_dir)
                              if f.endswith(('.jpg', '.png')) and
                              os.path.join(img_dir, f) != args.image]

                if other_images:
                    image2_path = os.path.join(img_dir, other_images[0])
                    attacked_img = attacker.generate_morphing_attack(
                        args.image,
                        image2_path,
                        alpha=0.5
                    )
                else:
                    print("   ⚠️  Skipping: Need two images for morphing")
                    continue

                output_path = os.path.join(args.output_dir, f'morphing_attack.jpg')

            # Save attacked image
            cv2.imwrite(output_path, attacked_img)
            print(f"   ✓ Generated: {output_path}")

            # Calculate perturbation metrics
            original = cv2.imread(args.image)
            if original.shape == attacked_img.shape:
                diff = cv2.absdiff(original, attacked_img)
                perturbation = diff.mean()
                print(f"   Perturbation: {perturbation:.2f} (mean pixel difference)")

            results[attack_type] = {
                'success': True,
                'output_path': output_path,
                'perturbation': perturbation if 'perturbation' in locals() else None
            }

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[attack_type] = {'success': False, 'error': str(e)}

    # Summary
    print("\n" + "="*70)
    print("Attack Generation Summary")
    print("="*70)

    successful = sum(1 for r in results.values() if r.get('success'))
    print(f"\n✓ Successfully generated: {successful}/{len(results)} attacks")
    print(f"📁 Output directory: {args.output_dir}")

    if successful > 0:
        print("\n📊 Attack Files:")
        for attack_type, result in results.items():
            if result.get('success'):
                print(f"   • {attack_type}: {result['output_path']}")

    print("\n" + "="*70)
    print("Next Steps:")
    print("1. Test attacks against authentication system")
    print("2. Run: python examples/05_liveness_detection.py")
    print("3. Evaluate attack effectiveness")
    print("4. Compare with presentation attacks")
    print("="*70)


if __name__ == "__main__":
    main()
