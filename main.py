#!/usr/bin/env python3
"""
Biometric Authentication & Anti-Spoofing Security Research System
Main CLI interface for all operations.
"""

import argparse
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from biometric.face_recognition import FaceAuthenticator, RealtimeFaceAuth
from biometric.fingerprint_matcher import FingerprintMatcher
from attacks.presentation_attacks import PresentationAttacks
from attacks.deepfake_generator import LightweightDeepfake
from defenses.liveness_detection import LivenessDetector, AntiSpoofingSystem
from evaluation.vulnerability_tester import VulnerabilityTester
from reporting.report_generator import SecurityReportGenerator


def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   Biometric Authentication & Anti-Spoofing Security Research        ║
║   Face Recognition + Fingerprint + Liveness Detection               ║
║                                                                      ║
║   For Security Research and Educational Purposes                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def enroll_user(args):
    """Enroll a new user"""
    print(f"\n[*] Enrolling user: {args.user_id}")

    if args.modality == 'face':
        auth = FaceAuthenticator()

        if args.load_model and os.path.exists(args.load_model):
            auth.load_model(args.load_model)

        # Get image paths
        if args.images:
            images = args.images.split(',')
        elif args.image_dir:
            images = [os.path.join(args.image_dir, f) for f in os.listdir(args.image_dir)
                     if f.endswith(('.jpg', '.png', '.jpeg'))]
        else:
            print("[-] Error: Please provide --images or --image-dir")
            return

        success = auth.enroll_user(args.user_id, images)

        if success:
            save_path = args.save_model or 'data/enrolled_users/face_auth.pkl'
            auth.save_model(save_path)
            print(f"[+] User enrolled successfully and saved to {save_path}")
        else:
            print("[-] Enrollment failed")

    elif args.modality == 'fingerprint':
        matcher = FingerprintMatcher()

        if args.load_model and os.path.exists(args.load_model):
            matcher.load_database(args.load_model)

        if not args.image:
            print("[-] Error: Please provide --image for fingerprint enrollment")
            return

        success = matcher.enroll_fingerprint(args.user_id, args.image)

        if success:
            save_path = args.save_model or 'data/enrolled_users/fingerprint_db.pkl'
            matcher.save_database(save_path)
            print(f"[+] Fingerprint enrolled successfully and saved to {save_path}")
        else:
            print("[-] Enrollment failed")


def authenticate_user(args):
    """Authenticate a user"""
    print(f"\n[*] Authenticating user with {args.modality}...")

    if args.modality == 'face':
        auth = FaceAuthenticator()

        model_path = args.load_model or 'data/enrolled_users/face_auth.pkl'
        if os.path.exists(model_path):
            auth.load_model(model_path)
        else:
            print(f"[-] No enrolled users found at {model_path}")
            return

        if args.image:
            user_id, score = auth.authenticate(args.image)
            if user_id:
                print(f"[+] AUTHENTICATED: {user_id} (confidence: {score:.2%})")
            else:
                print(f"[-] REJECTED (best score: {score:.2%})")
        else:
            print("[-] Error: Please provide --image")

    elif args.modality == 'fingerprint':
        matcher = FingerprintMatcher()

        model_path = args.load_model or 'data/enrolled_users/fingerprint_db.pkl'
        if os.path.exists(model_path):
            matcher.load_database(model_path)
        else:
            print(f"[-] No enrolled fingerprints found at {model_path}")
            return

        if args.image:
            user_id, score = matcher.match_fingerprint(args.image)
            if user_id:
                print(f"[+] AUTHENTICATED: {user_id} (confidence: {score:.2%})")
            else:
                print(f"[-] REJECTED (best score: {score:.2%})")
        else:
            print("[-] Error: Please provide --image")


def realtime_auth(args):
    """Real-time face authentication using webcam"""
    print("\n[*] Starting real-time face authentication...")

    auth = FaceAuthenticator()

    model_path = args.load_model or 'data/enrolled_users/face_auth.pkl'
    if os.path.exists(model_path):
        auth.load_model(model_path)
    else:
        print(f"[-] No enrolled users found at {model_path}")
        print("[*] Continuing without enrolled users (detection only)")

    realtime = RealtimeFaceAuth(auth)
    realtime.run()


def generate_attacks(args):
    """Generate presentation attacks"""
    print("\n[*] Generating presentation attacks...")

    attacks = PresentationAttacks()

    if not args.image:
        print("[-] Error: Please provide --image")
        return

    attack_types = args.attack_types.split(',') if args.attack_types else ['photo', 'mask', 'degraded']

    print(f"[*] Generating attacks: {', '.join(attack_types)}")
    results = attacks.batch_generate_attacks(args.image, attack_types)

    print(f"\n[+] Generated {len(results)} attack samples:")
    for attack_type, path in results.items():
        print(f"    - {attack_type}: {path}")


def generate_deepfake(args):
    """Generate deepfake"""
    print("\n[*] Generating deepfake...")

    deepfake = LightweightDeepfake()

    if not args.source or not args.target:
        print("[-] Error: Please provide --source and --target")
        return

    output = args.output or 'data/attack_samples/deepfake_result.jpg'

    result = deepfake.simple_face_swap(args.source, args.target, output)

    if result:
        print(f"[+] Deepfake generated: {result}")
    else:
        print("[-] Deepfake generation failed")


def test_liveness(args):
    """Test liveness detection"""
    print("\n[*] Testing liveness detection...")

    liveness = LivenessDetector()

    if args.test_type == 'blink':
        print("[*] Starting blink detection test (press 'q' to quit)")
        import cv2
        cap = cv2.VideoCapture(0)

        liveness.reset_blink_counter()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            is_live, annotated = liveness.detect_blink(frame)
            cv2.imshow('Blink Detection', annotated)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    elif args.test_type == 'texture':
        if not args.image:
            print("[-] Error: Please provide --image for texture analysis")
            return

        is_real, entropy = liveness.texture_analysis(args.image)
        print(f"[*] Result: {'REAL' if is_real else 'SPOOF'} (entropy: {entropy:.2f})")

    elif args.test_type == 'flash':
        print("[*] Starting active flash test...")
        is_live, diff = liveness.active_flash_test()
        print(f"[*] Result: {'LIVE' if is_live else 'SPOOF'} (difference: {diff:.2f})")

    elif args.test_type == 'comprehensive':
        if not args.image:
            print("[-] Error: Please provide --image")
            return

        anti_spoof = AntiSpoofingSystem()
        results = anti_spoof.comprehensive_check(args.image, use_webcam=args.use_webcam)

        print("\n[*] Comprehensive Anti-Spoofing Results:")
        for check_name, check_data in results['checks'].items():
            print(f"    {check_name}: {check_data}")

        print(f"\n[*] Final Decision: {'REAL' if results['final_decision'] else 'SPOOF'}")
        print(f"[*] Confidence: {results['confidence']:.2%}")


def run_vulnerability_test(args):
    """Run comprehensive vulnerability testing"""
    print("\n[*] Starting vulnerability assessment...")

    # Initialize authenticators
    face_auth = FaceAuthenticator()
    fingerprint_auth = FingerprintMatcher()

    # Load models
    face_model = args.face_model or 'data/enrolled_users/face_auth.pkl'
    if os.path.exists(face_model):
        face_auth.load_model(face_model)
    else:
        print(f"[!] Warning: No face model found at {face_model}")

    fp_model = args.fingerprint_model or 'data/enrolled_users/fingerprint_db.pkl'
    if os.path.exists(fp_model):
        fingerprint_auth.load_database(fp_model)
    else:
        print(f"[!] Warning: No fingerprint model found at {fp_model}")

    # Create tester
    tester = VulnerabilityTester(face_auth, fingerprint_auth)

    # Run assessment
    if args.test_dir:
        results = tester.run_full_assessment(args.test_dir, args.attack_source_dir)
    else:
        print("[-] Error: Please provide --test-dir")
        return

    # Generate report
    print("\n[*] Generating security report...")
    report_gen = SecurityReportGenerator(results_file='data/results/vulnerability_test.json')
    report_gen.generate_html_report(args.output or 'data/results/security_report.html')

    # Print executive summary
    print("\n" + report_gen.generate_executive_summary())


def generate_report(args):
    """Generate security report from existing results"""
    print("\n[*] Generating security report...")

    if not args.results_file:
        print("[-] Error: Please provide --results-file")
        return

    report_gen = SecurityReportGenerator(results_file=args.results_file)
    output_path = args.output or 'data/results/security_report.html'

    report_gen.generate_html_report(output_path)

    print(f"[+] Report generated: {output_path}")
    print("\n" + report_gen.generate_executive_summary())


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Biometric Authentication & Anti-Spoofing Security Research System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enroll a user with face
  python main.py enroll --user-id alice --modality face --images img1.jpg,img2.jpg,img3.jpg

  # Authenticate with face
  python main.py authenticate --modality face --image test.jpg

  # Real-time authentication
  python main.py realtime

  # Generate attacks
  python main.py attack --image genuine.jpg --attack-types photo,mask,degraded

  # Test liveness
  python main.py liveness --test-type comprehensive --image test.jpg

  # Run vulnerability assessment
  python main.py vulnerability-test --test-dir data/test_samples

  # Generate report
  python main.py report --results-file data/results/vulnerability_test.json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Enroll command
    enroll_parser = subparsers.add_parser('enroll', help='Enroll a new user')
    enroll_parser.add_argument('--user-id', required=True, help='User ID')
    enroll_parser.add_argument('--modality', choices=['face', 'fingerprint'], default='face')
    enroll_parser.add_argument('--images', help='Comma-separated image paths')
    enroll_parser.add_argument('--image-dir', help='Directory containing enrollment images')
    enroll_parser.add_argument('--image', help='Single image (for fingerprint)')
    enroll_parser.add_argument('--save-model', help='Path to save model')
    enroll_parser.add_argument('--load-model', help='Path to existing model to update')

    # Authenticate command
    auth_parser = subparsers.add_parser('authenticate', help='Authenticate a user')
    auth_parser.add_argument('--modality', choices=['face', 'fingerprint'], default='face')
    auth_parser.add_argument('--image', required=True, help='Image to authenticate')
    auth_parser.add_argument('--load-model', help='Path to model')

    # Real-time authentication
    realtime_parser = subparsers.add_parser('realtime', help='Real-time face authentication')
    realtime_parser.add_argument('--load-model', help='Path to model')

    # Attack generation
    attack_parser = subparsers.add_parser('attack', help='Generate presentation attacks')
    attack_parser.add_argument('--image', required=True, help='Genuine image')
    attack_parser.add_argument('--attack-types', help='Comma-separated attack types (photo,mask,degraded)')

    # Deepfake generation
    deepfake_parser = subparsers.add_parser('deepfake', help='Generate deepfake')
    deepfake_parser.add_argument('--source', required=True, help='Source face image')
    deepfake_parser.add_argument('--target', required=True, help='Target image')
    deepfake_parser.add_argument('--output', help='Output path')

    # Liveness testing
    liveness_parser = subparsers.add_parser('liveness', help='Test liveness detection')
    liveness_parser.add_argument('--test-type', choices=['blink', 'texture', 'flash', 'comprehensive'],
                                 default='comprehensive')
    liveness_parser.add_argument('--image', help='Image to test')
    liveness_parser.add_argument('--use-webcam', action='store_true', help='Use webcam for blink detection')

    # Vulnerability testing
    vuln_parser = subparsers.add_parser('vulnerability-test', help='Run vulnerability assessment')
    vuln_parser.add_argument('--test-dir', help='Directory with genuine test images')
    vuln_parser.add_argument('--attack-source-dir', help='Directory with images for attack generation')
    vuln_parser.add_argument('--face-model', help='Path to face model')
    vuln_parser.add_argument('--fingerprint-model', help='Path to fingerprint model')
    vuln_parser.add_argument('--output', help='Output path for report')

    # Report generation
    report_parser = subparsers.add_parser('report', help='Generate security report')
    report_parser.add_argument('--results-file', required=True, help='Path to results JSON')
    report_parser.add_argument('--output', help='Output path for HTML report')

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Execute command
    if args.command == 'enroll':
        enroll_user(args)
    elif args.command == 'authenticate':
        authenticate_user(args)
    elif args.command == 'realtime':
        realtime_auth(args)
    elif args.command == 'attack':
        generate_attacks(args)
    elif args.command == 'deepfake':
        generate_deepfake(args)
    elif args.command == 'liveness':
        test_liveness(args)
    elif args.command == 'vulnerability-test':
        run_vulnerability_test(args)
    elif args.command == 'report':
        generate_report(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
