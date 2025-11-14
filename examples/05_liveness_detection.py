#!/usr/bin/env python3
"""
Example 5: Liveness Detection

This example demonstrates various anti-spoofing and liveness detection techniques
to protect against presentation attacks.
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from defenses.liveness_detection import LivenessDetector
from config import get_config
from utils.logger import get_logger
import cv2

# Initialize
logger = get_logger(__name__)
config = get_config()


def main():
    """Test liveness detection methods"""
    parser = argparse.ArgumentParser(description="Liveness Detection Example")
    parser.add_argument('--image', type=str, help='Path to test image')
    parser.add_argument('--video', type=str, help='Path to test video')
    parser.add_argument('--method', type=str, default='all',
                       choices=['blink', 'texture', 'depth', 'flash', 'challenge', 'all'],
                       help='Liveness detection method')
    args = parser.parse_args()

    print("="*70)
    print("Example 5: Liveness Detection & Anti-Spoofing")
    print("="*70)

    # Initialize detector
    print("\n⚙️  Initializing liveness detector...")
    detector = LivenessDetector()

    methods_to_test = []
    if args.method == 'all':
        methods_to_test = ['texture', 'blink', 'challenge']
    else:
        methods_to_test = [args.method]

    print(f"\n🔍 Testing {len(methods_to_test)} method(s)")
    print("-" * 70)

    results = {}

    # Test each method
    for method in methods_to_test:
        print(f"\n📍 Method: {method.upper()}")

        try:
            if method == 'texture':
                # Texture Analysis (requires image)
                if not args.image:
                    test_image = 'data/examples/alice_1.jpg'
                    if not os.path.exists(test_image):
                        print("   ⚠️  No test image available")
                        continue
                else:
                    test_image = args.image

                print(f"   Input: {test_image}")
                print("   Description: Local Binary Pattern (LBP) texture analysis")

                is_live, score = detector.check_texture_liveness(test_image)

                print(f"   Result: {'✓ LIVE' if is_live else '✗ SPOOF'}")
                print(f"   Score: {score:.2%}")
                print(f"   Threshold: {config.liveness.texture_threshold}")

                results[method] = {
                    'is_live': is_live,
                    'score': score,
                    'method': 'texture_analysis'
                }

            elif method == 'blink':
                # Blink Detection (requires video)
                if not args.video:
                    print("   ⚠️  Blink detection requires video input")
                    print("   Usage: --video path/to/video.mp4")
                    continue

                print(f"   Input: {args.video}")
                print("   Description: Eye blink detection over video frames")

                is_live, num_blinks = detector.detect_blink(args.video)

                print(f"   Result: {'✓ LIVE' if is_live else '✗ SPOOF'}")
                print(f"   Blinks detected: {num_blinks}")
                print(f"   Minimum required: {config.liveness.min_blinks}")

                results[method] = {
                    'is_live': is_live,
                    'blinks': num_blinks,
                    'method': 'blink_detection'
                }

            elif method == 'depth':
                # Depth Analysis (requires depth camera)
                print("   Description: Depth map analysis (requires depth camera)")
                print("   ⚠️  This method requires special hardware")
                print("   Status: Demo mode only")

                # Simulated result for demonstration
                results[method] = {
                    'method': 'depth_analysis',
                    'note': 'Requires depth camera hardware'
                }

            elif method == 'flash':
                # Active Flash Test
                print("   Description: Active flash illumination test")
                print("   ⚠️  This method requires camera with flash control")
                print("   Status: Demo mode only")

                # Simulated result
                results[method] = {
                    'method': 'active_flash',
                    'note': 'Requires camera flash control'
                }

            elif method == 'challenge':
                # Challenge-Response
                print("   Description: Interactive challenge-response")
                print("   Examples:")
                print("   - 'Turn your head left'")
                print("   - 'Smile'")
                print("   - 'Look up'")
                print("   Status: Requires user interaction")

                # Simulated result
                results[method] = {
                    'method': 'challenge_response',
                    'note': 'Requires interactive session'
                }

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[method] = {'error': str(e)}

    # Test against known attacks
    print("\n" + "="*70)
    print("Testing Against Known Attacks")
    print("="*70)

    attack_dir = 'data/attack_samples'
    if os.path.exists(attack_dir):
        attack_files = [
            os.path.join(attack_dir, f)
            for f in os.listdir(attack_dir)
            if f.endswith(('.jpg', '.png'))
        ]

        if attack_files:
            print(f"\n🎯 Found {len(attack_files)} attack samples")
            print("\nTesting with texture analysis...")

            detected_attacks = 0
            for attack_file in attack_files[:5]:  # Test first 5
                is_live, score = detector.check_texture_liveness(attack_file)
                status = "✓ Detected" if not is_live else "✗ Missed"
                print(f"   {os.path.basename(attack_file)}: {status} (score: {score:.2%})")
                if not is_live:
                    detected_attacks += 1

            detection_rate = detected_attacks / min(len(attack_files), 5)
            print(f"\n📊 Detection Rate: {detection_rate:.1%}")
        else:
            print("\n⚠️  No attack samples found")
    else:
        print(f"\n⚠️  Attack samples directory not found: {attack_dir}")
        print("   Generate attacks first: python examples/03_generate_attacks.py")

    # Summary
    print("\n" + "="*70)
    print("Liveness Detection Summary")
    print("="*70)

    tested = len([r for r in results.values() if not r.get('error')])
    print(f"\n✓ Methods tested: {tested}/{len(results)}")

    if any(r.get('is_live') is not None for r in results.values()):
        print("\n📊 Results:")
        for method, result in results.items():
            if result.get('is_live') is not None:
                status = "LIVE ✓" if result['is_live'] else "SPOOF ✗"
                print(f"   • {method}: {status}")
                if 'score' in result:
                    print(f"     Score: {result['score']:.2%}")

    print("\n💡 Recommendations:")
    print("   1. Use multiple liveness detection methods")
    print("   2. Texture analysis is fast but can be fooled")
    print("   3. Blink detection adds robustness (video required)")
    print("   4. Challenge-response has best security but worst UX")
    print("   5. Combine methods for defense-in-depth")

    print("\n" + "="*70)
    print("Next Steps:")
    print("1. Test with different attack types")
    print("2. Run: python examples/06_vulnerability_testing.py")
    print("3. Tune liveness thresholds in config")
    print("4. Compare detection rates across methods")
    print("="*70)


if __name__ == "__main__":
    main()
