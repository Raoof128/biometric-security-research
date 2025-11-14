#!/usr/bin/env python3
"""
Example 2: User Authentication

This example demonstrates how to authenticate users.
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from biometric.face_recognition import FaceAuthenticator
from config import get_config
from utils.logger import get_logger
from utils.security import get_validator, get_audit_logger

# Initialize
logger = get_logger(__name__)
config = get_config()
validator = get_validator()
audit_logger = get_audit_logger()


def main():
    """Authenticate a user"""
    parser = argparse.ArgumentParser(description="Authenticate user example")
    parser.add_argument("--image", default="data/examples/alice_test.jpg",
                      help="Image to authenticate")
    parser.add_argument("--model", default="data/enrolled_users/example_face_auth.pkl",
                      help="Path to enrolled users model")
    args = parser.parse_args()

    print("="*70)
    print("Example 2: User Authentication")
    print("="*70)

    # Validate input
    if os.path.exists(args.image):
        is_valid, error = validator.validate_file_path(args.image)
        if not is_valid:
            print(f"\n❌ Error: {error}")
            return
    else:
        print(f"\n⚠️  Image not found: {args.image}")
        print("   Using placeholder path for demonstration")

    # Load authenticator
    auth = FaceAuthenticator()

    if not os.path.exists(args.model):
        print(f"\n⚠️  Model not found: {args.model}")
        print("   Run examples/01_simple_enrollment.py first")
        return

    auth.load_model(args.model)
    print(f"\n📁 Loaded model: {args.model}")
    print(f"👥 Enrolled users: {len(auth.enrolled_users)}")

    if not os.path.exists(args.image):
        print("\n⚠️  Skipping authentication (no test image)")
        return

    # Authenticate
    print(f"\n🔍 Authenticating: {args.image}")

    user_id, score = auth.authenticate(args.image)

    # Log authentication attempt
    audit_logger.log_authentication_attempt(
        user_id=user_id or "unknown",
        success=user_id is not None,
        method="face",
        details={"score": score, "image": args.image}
    )

    # Display result
    print("\n" + "="*70)
    if user_id:
        print(f"✅ AUTHENTICATED")
        print(f"   User: {user_id}")
        print(f"   Confidence: {score:.2%}")
        print(f"   Status: Access Granted")
    else:
        print(f"❌ REJECTED")
        print(f"   Best Match Score: {score:.2%}")
        print(f"   Threshold: {config.biometric.similarity_threshold}")
        print(f"   Status: Access Denied")
    print("="*70)

    print("\n📝 Audit log entry created")
    print(f"   Check: {config.paths.logs_dir}/audit.log")


if __name__ == "__main__":
    main()
