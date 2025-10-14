#!/usr/bin/env python3
"""
Comprehensive system testing and validation script.
Tests all modules and ensures proper functionality.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test all module imports"""
    print("\n" + "="*60)
    print("TESTING MODULE IMPORTS")
    print("="*60)

    errors = []

    # Test biometric modules
    try:
        from biometric.face_recognition import FaceAuthenticator, RealtimeFaceAuth
        print("[+] biometric.face_recognition ... OK")
    except Exception as e:
        errors.append(f"biometric.face_recognition: {e}")
        print(f"[-] biometric.face_recognition ... FAILED: {e}")

    try:
        from biometric.fingerprint_matcher import FingerprintMatcher
        print("[+] biometric.fingerprint_matcher ... OK")
    except Exception as e:
        errors.append(f"biometric.fingerprint_matcher: {e}")
        print(f"[-] biometric.fingerprint_matcher ... FAILED: {e}")

    # Test attack modules
    try:
        from attacks.presentation_attacks import PresentationAttacks
        print("[+] attacks.presentation_attacks ... OK")
    except Exception as e:
        errors.append(f"attacks.presentation_attacks: {e}")
        print(f"[-] attacks.presentation_attacks ... FAILED: {e}")

    try:
        from attacks.deepfake_generator import LightweightDeepfake
        print("[+] attacks.deepfake_generator ... OK")
    except Exception as e:
        errors.append(f"attacks.deepfake_generator: {e}")
        print(f"[-] attacks.deepfake_generator ... FAILED: {e}")

    # Test defense modules
    try:
        from defenses.liveness_detection import LivenessDetector, AntiSpoofingSystem
        print("[+] defenses.liveness_detection ... OK")
    except Exception as e:
        errors.append(f"defenses.liveness_detection: {e}")
        print(f"[-] defenses.liveness_detection ... FAILED: {e}")

    # Test evaluation modules
    try:
        from evaluation.vulnerability_tester import VulnerabilityTester
        print("[+] evaluation.vulnerability_tester ... OK")
    except Exception as e:
        errors.append(f"evaluation.vulnerability_tester: {e}")
        print(f"[-] evaluation.vulnerability_tester ... FAILED: {e}")

    # Test reporting modules
    try:
        from reporting.report_generator import SecurityReportGenerator
        print("[+] reporting.report_generator ... OK")
    except Exception as e:
        errors.append(f"reporting.report_generator: {e}")
        print(f"[-] reporting.report_generator ... FAILED: {e}")

    if errors:
        print(f"\n[-] {len(errors)} import errors found")
        print("\n[!] Please install missing dependencies:")
        print("    pip install -r requirements.txt")
        return False
    else:
        print("\n[+] All imports successful!")
        return True


def test_directory_structure():
    """Test that all required directories exist"""
    print("\n" + "="*60)
    print("TESTING DIRECTORY STRUCTURE")
    print("="*60)

    required_dirs = [
        'biometric',
        'biometric/models',
        'attacks',
        'defenses',
        'evaluation',
        'reporting',
        'reporting/templates',
        'data',
        'data/enrolled_users',
        'data/test_samples',
        'data/attack_samples',
        'data/results',
        'data/results/charts',
    ]

    missing = []

    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"[+] {dir_path} ... EXISTS")
        else:
            missing.append(dir_path)
            print(f"[-] {dir_path} ... MISSING")
            # Create missing directory
            os.makedirs(dir_path, exist_ok=True)
            print(f"    [*] Created {dir_path}")

    if missing:
        print(f"\n[!] Created {len(missing)} missing directories")
    else:
        print("\n[+] All directories exist!")

    return True


def test_main_files():
    """Test that all main files exist"""
    print("\n" + "="*60)
    print("TESTING MAIN FILES")
    print("="*60)

    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        'PROJECT_SUMMARY.md',
        'GETTING_STARTED.md',
        'generate_test_data.py',
        'verify_installation.sh',
    ]

    missing = []

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"[+] {file_path} ... EXISTS")
        else:
            missing.append(file_path)
            print(f"[-] {file_path} ... MISSING")

    if missing:
        print(f"\n[-] {len(missing)} files missing")
        return False
    else:
        print("\n[+] All required files exist!")
        return True


def test_module_initialization():
    """Test that modules can be initialized"""
    print("\n" + "="*60)
    print("TESTING MODULE INITIALIZATION")
    print("="*60)

    errors = []

    # Test FaceAuthenticator
    try:
        from biometric.face_recognition import FaceAuthenticator
        auth = FaceAuthenticator()
        print("[+] FaceAuthenticator initialization ... OK")
    except Exception as e:
        errors.append(f"FaceAuthenticator: {e}")
        print(f"[-] FaceAuthenticator initialization ... FAILED: {e}")

    # Test FingerprintMatcher
    try:
        from biometric.fingerprint_matcher import FingerprintMatcher
        matcher = FingerprintMatcher()
        print("[+] FingerprintMatcher initialization ... OK")
    except Exception as e:
        errors.append(f"FingerprintMatcher: {e}")
        print(f"[-] FingerprintMatcher initialization ... FAILED: {e}")

    # Test PresentationAttacks
    try:
        from attacks.presentation_attacks import PresentationAttacks
        attacks = PresentationAttacks()
        print("[+] PresentationAttacks initialization ... OK")
    except Exception as e:
        errors.append(f"PresentationAttacks: {e}")
        print(f"[-] PresentationAttacks initialization ... FAILED: {e}")

    # Test LivenessDetector
    try:
        from defenses.liveness_detection import LivenessDetector
        liveness = LivenessDetector(use_dlib=False)  # Don't require dlib
        print("[+] LivenessDetector initialization ... OK")
    except Exception as e:
        errors.append(f"LivenessDetector: {e}")
        print(f"[-] LivenessDetector initialization ... FAILED: {e}")

    # Test AntiSpoofingSystem
    try:
        from defenses.liveness_detection import AntiSpoofingSystem
        anti_spoof = AntiSpoofingSystem()
        print("[+] AntiSpoofingSystem initialization ... OK")
    except Exception as e:
        errors.append(f"AntiSpoofingSystem: {e}")
        print(f"[-] AntiSpoofingSystem initialization ... FAILED: {e}")

    # Test SecurityReportGenerator
    try:
        from reporting.report_generator import SecurityReportGenerator
        reporter = SecurityReportGenerator()
        print("[+] SecurityReportGenerator initialization ... OK")
    except Exception as e:
        errors.append(f"SecurityReportGenerator: {e}")
        print(f"[-] SecurityReportGenerator initialization ... FAILED: {e}")

    if errors:
        print(f"\n[-] {len(errors)} initialization errors")
        return False
    else:
        print("\n[+] All modules initialized successfully!")
        return True


def test_cli_interface():
    """Test CLI interface"""
    print("\n" + "="*60)
    print("TESTING CLI INTERFACE")
    print("="*60)

    import subprocess

    try:
        result = subprocess.run(
            ['python3', 'main.py', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("[+] CLI --help command ... OK")
            return True
        else:
            print(f"[-] CLI --help command ... FAILED")
            print(f"    Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"[-] CLI test ... FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("BIOMETRIC SECURITY SYSTEM - COMPREHENSIVE TESTING")
    print("="*60)

    results = {}

    # Run tests
    results['imports'] = test_imports()
    results['directories'] = test_directory_structure()
    results['files'] = test_main_files()
    results['initialization'] = test_module_initialization()
    results['cli'] = test_cli_interface()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "[+]" if passed else "[-]"
        print(f"{symbol} {test_name.upper()}: {status}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nSystem is ready to use!")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Generate test data: python3 generate_test_data.py")
        print("  3. Try examples in QUICKSTART.md")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the errors above.")
        print("\nIf dependencies are missing:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
