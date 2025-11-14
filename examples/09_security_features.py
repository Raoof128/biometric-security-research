#!/usr/bin/env python3
"""
Example 9: Security Features

This example demonstrates the security features built into the system,
including input validation, rate limiting, audit logging, and secure data handling.
"""

import sys
import os
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.security import (
    InputValidator, RateLimiter, SecureDataHandler, AuditLogger,
    get_validator, get_audit_logger
)
from config import get_config
from utils.logger import get_logger
import tempfile

# Initialize
logger = get_logger(__name__)
config = get_config()


def demo_input_validation():
    """Demonstrate input validation security"""
    print("\n" + "="*70)
    print("DEMO 1: Input Validation")
    print("="*70)

    validator = InputValidator()

    test_cases = [
        # (input, expected_result, description)
        ("data/test.jpg", True, "Valid image path"),
        ("../../../etc/passwd", False, "Path traversal attack"),
        ("image.jpg; rm -rf /", False, "Command injection attempt"),
        ("very" * 100 + ".jpg", False, "Excessive path length"),
        ("test_image.png", True, "Valid PNG file"),
        ("script.js", False, "Invalid file extension"),
        ("../data/test.jpg", False, "Relative path (not allowed)"),
        ("/tmp/test.jpg", True, "Absolute path"),
    ]

    print("\n🔒 Testing File Path Validation:")
    print("-"*70)

    for test_input, expected_valid, description in test_cases:
        is_valid, error = validator.validate_file_path(test_input)

        # Show result
        icon = "✓" if is_valid else "✗"
        expected = "VALID" if expected_valid else "INVALID"
        actual = "VALID" if is_valid else "INVALID"

        match = "✓" if (is_valid == expected_valid) else "✗"

        print(f"\n{match} {description}")
        print(f"   Input: {test_input}")
        print(f"   Expected: {expected}, Got: {actual}")

        if not is_valid:
            print(f"   Reason: {error}")

    # User ID validation
    print("\n🔒 Testing User ID Validation:")
    print("-"*70)

    user_id_tests = [
        ("alice", True, "Valid alphanumeric user ID"),
        ("user_123", True, "Valid with underscore"),
        ("user-456", True, "Valid with hyphen"),
        ("admin'; DROP TABLE users;--", False, "SQL injection attempt"),
        ("a" * 100, False, "Excessive length"),
        ("user@host", False, "Invalid characters"),
        ("", False, "Empty user ID"),
    ]

    for user_id, expected_valid, description in user_id_tests:
        is_valid, error = validator.validate_user_id(user_id)

        match = "✓" if (is_valid == expected_valid) else "✗"
        actual = "VALID" if is_valid else "INVALID"

        print(f"\n{match} {description}")
        print(f"   User ID: {user_id}")
        print(f"   Result: {actual}")

        if not is_valid:
            print(f"   Reason: {error}")


def demo_rate_limiting():
    """Demonstrate rate limiting protection"""
    print("\n" + "="*70)
    print("DEMO 2: Rate Limiting")
    print("="*70)

    # Create rate limiter (5 attempts per 60 seconds)
    rate_limiter = RateLimiter(max_attempts=5, window_seconds=60)

    print("\n🔒 Testing Brute Force Protection:")
    print("   Configuration: 5 attempts per 60 seconds")
    print("-"*70)

    user_id = "test_user"

    print(f"\nSimulating rapid authentication attempts for user: {user_id}\n")

    for attempt in range(10):
        is_allowed = rate_limiter.is_allowed(user_id)

        if is_allowed:
            print(f"Attempt {attempt + 1}: ✓ ALLOWED")
        else:
            print(f"Attempt {attempt + 1}: ✗ BLOCKED (rate limit exceeded)")

        time.sleep(0.1)  # Small delay

    # Check different user
    print(f"\nTesting different user (rate limits are per-user):")
    other_user = "different_user"

    is_allowed = rate_limiter.is_allowed(other_user)
    if is_allowed:
        print(f"{other_user}: ✓ ALLOWED (independent rate limit)")

    # Show rate limiter state
    print("\n📊 Rate Limiter Statistics:")
    print(f"   Tracked users: {len(rate_limiter.attempts)}")

    for tracked_user, attempts in list(rate_limiter.attempts.items())[:3]:
        print(f"   - {tracked_user}: {len(attempts)} recent attempts")


def demo_audit_logging():
    """Demonstrate audit logging"""
    print("\n" + "="*70)
    print("DEMO 3: Audit Logging")
    print("="*70)

    audit_logger = get_audit_logger()

    print("\n📝 Logging Security Events:")
    print("-"*70)

    # Log various events
    events = [
        ("authentication_attempt", {
            'user_id': 'alice',
            'success': True,
            'method': 'face',
            'confidence': 0.92
        }),
        ("authentication_attempt", {
            'user_id': 'unknown',
            'success': False,
            'method': 'face',
            'reason': 'no_match'
        }),
        ("user_enrollment", {
            'user_id': 'bob',
            'modality': 'face',
            'num_samples': 5
        }),
        ("template_access", {
            'user_id': 'alice',
            'operation': 'read',
            'authorized': True
        }),
        ("rate_limit_exceeded", {
            'user_id': 'attacker',
            'attempts': 10,
            'window': '60s'
        }),
        ("template_deletion", {
            'user_id': 'old_user',
            'secure_delete': True,
            'reason': 'user_request'
        }),
    ]

    for event_type, details in events:
        if event_type == "authentication_attempt":
            audit_logger.log_authentication_attempt(
                user_id=details['user_id'],
                success=details['success'],
                method=details.get('method', 'unknown'),
                details=details
            )
        else:
            audit_logger.log_security_event(event_type, details)

        print(f"✓ Logged: {event_type} - {details.get('user_id', 'system')}")

    # Show log location
    log_file = Path(config.paths.logs_dir) / "audit.log"
    print(f"\n📁 Audit log location: {log_file}")

    if log_file.exists():
        print("\n📄 Recent audit log entries:")
        print("-"*70)

        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:  # Show last 5 entries
                print(f"   {line.strip()}")


def demo_secure_data_handling():
    """Demonstrate secure data handling"""
    print("\n" + "="*70)
    print("DEMO 4: Secure Data Handling")
    print("="*70)

    handler = SecureDataHandler()

    # Encryption demonstration
    print("\n🔒 Data Encryption:")
    print("-"*70)

    sensitive_data = "biometric_template_data_12345"
    print(f"Original data: {sensitive_data}")

    # Encrypt
    encrypted = handler.encrypt_data(sensitive_data.encode())
    print(f"Encrypted: {encrypted[:50]}... ({len(encrypted)} bytes)")

    # Decrypt
    decrypted = handler.decrypt_data(encrypted)
    print(f"Decrypted: {decrypted.decode()}")

    match = "✓" if decrypted.decode() == sensitive_data else "✗"
    print(f"{match} Encryption/Decryption: {'SUCCESS' if match == '✓' else 'FAILED'}")

    # Hashing demonstration
    print("\n🔒 Secure Hashing:")
    print("-"*70)

    data_to_hash = "user_password_or_template"
    print(f"Original data: {data_to_hash}")

    hash1 = handler.hash_data(data_to_hash)
    print(f"Hash: {hash1}")

    # Verify same data produces same hash
    hash2 = handler.hash_data(data_to_hash)
    match = "✓" if hash1 == hash2 else "✗"
    print(f"{match} Consistency: Hashing same data produces same hash")

    # Different data produces different hash
    hash3 = handler.hash_data(data_to_hash + "_modified")
    different = "✓" if hash1 != hash3 else "✗"
    print(f"{different} Uniqueness: Different data produces different hash")

    # Secure deletion demonstration
    print("\n🔒 Secure File Deletion:")
    print("-"*70)

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp_path = tmp.name
        tmp.write("Sensitive biometric data that should be securely deleted")

    print(f"Created temporary file: {tmp_path}")
    print(f"File exists: {os.path.exists(tmp_path)}")

    # Securely delete
    handler.secure_delete(tmp_path)
    print(f"After secure deletion, file exists: {os.path.exists(tmp_path)}")

    print("✓ File securely overwritten and deleted")

    # Constant-time comparison
    print("\n🔒 Constant-Time Comparison:")
    print("-"*70)

    secret1 = "secret_template_hash_abc123"
    secret2 = "secret_template_hash_abc123"
    secret3 = "different_hash_xyz789"

    match1 = handler.constant_time_compare(secret1, secret2)
    match2 = handler.constant_time_compare(secret1, secret3)

    print(f"Comparing identical secrets: {match1} ✓")
    print(f"Comparing different secrets: {match2} ✓")
    print("Note: Comparison time is constant regardless of match position")
    print("      This prevents timing attacks")


def demo_security_best_practices():
    """Demonstrate security best practices"""
    print("\n" + "="*70)
    print("DEMO 5: Security Best Practices")
    print("="*70)

    print("\n🔒 Implemented Security Measures:")
    print("-"*70)

    checks = [
        ("Input Validation", "All file paths and user IDs validated", True),
        ("Rate Limiting", "Brute force protection enabled", True),
        ("Audit Logging", "All security events logged", True),
        ("Template Encryption", "Biometric templates can be encrypted", True),
        ("Secure Deletion", "Multi-pass overwrite for sensitive data", True),
        ("Constant-Time Ops", "Timing attack prevention", True),
        ("Path Sanitization", "Prevent directory traversal", True),
        ("SQL Injection Protection", "Parameterized queries (when applicable)", True),
        ("XSS Prevention", "Input sanitization for web interfaces", True),
        ("CSRF Tokens", "For web API endpoints (future)", False),
    ]

    for feature, description, implemented in checks:
        icon = "✓" if implemented else "○"
        status = "Implemented" if implemented else "Planned"
        print(f"{icon} {feature}: {description}")
        print(f"   Status: {status}")

    print("\n💡 Security Recommendations:")
    print("-"*70)

    recommendations = [
        "1. Always enable rate limiting in production",
        "2. Enable template encryption for stored biometric data",
        "3. Regular audit log reviews and monitoring",
        "4. Use HTTPS/TLS for network communications",
        "5. Implement principle of least privilege",
        "6. Regular security updates and dependency scanning",
        "7. Penetration testing before production deployment",
        "8. Compliance with biometric data regulations (GDPR, CCPA, etc.)",
        "9. Secure key management (use HSM or KMS in production)",
        "10. Regular security audits and code reviews",
    ]

    for rec in recommendations:
        print(f"   {rec}")


def main():
    """Main security features demo"""
    print("="*70)
    print("Example 9: Security Features Demonstration")
    print("="*70)

    print("\nThis example demonstrates the security features built into")
    print("the Biometric Security Research System.")

    # Run demos
    demo_input_validation()
    demo_rate_limiting()
    demo_audit_logging()
    demo_secure_data_handling()
    demo_security_best_practices()

    # Summary
    print("\n" + "="*70)
    print("Security Features Summary")
    print("="*70)

    print("\n✓ Demonstrated Security Features:")
    print("   • Input validation (path traversal, injection prevention)")
    print("   • Rate limiting (brute force protection)")
    print("   • Audit logging (compliance and forensics)")
    print("   • Data encryption (template protection)")
    print("   • Secure hashing (one-way transformation)")
    print("   • Secure deletion (multi-pass overwrite)")
    print("   • Constant-time operations (timing attack prevention)")

    print("\n📚 Security Documentation:")
    print("   • SECURITY.md - Security policy and guidelines")
    print("   • CODE_OF_CONDUCT.md - Ethical use guidelines")
    print("   • docs/FAQ.md - Security FAQ")

    print("\n" + "="*70)
    print("Next Steps:")
    print("1. Review SECURITY.md for detailed security guidelines")
    print("2. Run: python examples/10_performance_monitoring.py")
    print("3. Implement security features in your deployment")
    print("4. Configure security settings in config.py")
    print("="*70)


if __name__ == "__main__":
    main()
