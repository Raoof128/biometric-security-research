#!/usr/bin/env python3
"""
Example 3: Generate Presentation Attacks

This example demonstrates how to generate various presentation attacks.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from attacks.presentation_attacks import PresentationAttacks
from attacks.adversarial_attacks import AdversarialAttacker
from config import get_config
from utils.logger import get_logger

# Initialize
logger = get_logger(__name__)
config = get_config()


def main():
    """Generate various presentation attacks"""
    print("="*70)
    print("Example 3: Generate Presentation Attacks")
    print("="*70)

    # Source image
    source_image = "data/examples/alice_1.jpg"

    if not os.path.exists(source_image):
        print(f"\n⚠️  Source image not found: {source_image}")
        print("   Create example images or modify the path")
        return

    print(f"\n📷 Source image: {source_image}")

    # 1. Standard presentation attacks
    print("\n🎯 Generating standard presentation attacks...")
    attacks = PresentationAttacks()

    attack_types = ['photo', 'mask', 'degraded']
    results = attacks.batch_generate_attacks(source_image, attack_types)

    print(f"\n✅ Generated {len(results)} standard attacks:")
    for attack_type, path in results.items():
        print(f"   ✓ {attack_type}: {path}")

    # 2. Adversarial attacks
    print("\n⚔️  Generating adversarial attacks...")
    adv_attacker = AdversarialAttacker()

    adv_types = ['patch', 'fgsm', 'pixel']
    adv_results = adv_attacker.batch_generate_adversarial_attacks(
        source_image,
        adv_types
    )

    print(f"\n✅ Generated {len(adv_results)} adversarial attacks:")
    for attack_type, path in adv_results.items():
        if path:
            print(f"   ✓ {attack_type}: {path}")

    # Summary
    print("\n" + "="*70)
    print("📊 Attack Generation Summary:")
    print(f"   Standard Attacks: {len(results)}")
    print(f"   Adversarial Attacks: {len([p for p in adv_results.values() if p])}")
    print(f"   Total: {len(results) + len([p for p in adv_results.values() if p])}")
    print("\n💡 Next Steps:")
    print("   1. Test attacks against authentication system")
    print("   2. Run liveness detection on attack samples")
    print("   3. Generate vulnerability reports")
    print("="*70)


if __name__ == "__main__":
    main()
