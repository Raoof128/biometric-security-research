#!/usr/bin/env python3
"""
Example 1: Simple User Enrollment

This example demonstrates how to enroll users with face recognition.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from biometric.face_recognition import FaceAuthenticator
from config import get_config
from utils.logger import get_logger

# Initialize
logger = get_logger(__name__)
config = get_config()


def main():
    """Enroll a user with face images"""
    print("="*70)
    print("Example 1: Simple User Enrollment")
    print("="*70)

    # Create authenticator
    auth = FaceAuthenticator(
        model_name=config.biometric.model_name,
        detector=config.biometric.detector_backend
    )

    # Example enrollment (modify paths as needed)
    user_id = "alice"
    image_paths = [
        "data/examples/alice_1.jpg",
        "data/examples/alice_2.jpg",
        "data/examples/alice_3.jpg",
    ]

    print(f"\n📝 Enrolling user: {user_id}")
    print(f"📷 Using {len(image_paths)} images")

    # Check if images exist
    existing_images = [img for img in image_paths if os.path.exists(img)]

    if not existing_images:
        print("\n⚠️  Warning: No example images found!")
        print("   Please create sample images in data/examples/ or modify the paths")
        print("\n💡 Tip: You can use your own images:")
        print("   image_paths = ['path/to/image1.jpg', 'path/to/image2.jpg']")
        return

    # Enroll user
    success = auth.enroll_user(user_id, existing_images)

    if success:
        # Save model
        model_path = "data/enrolled_users/example_face_auth.pkl"
        auth.save_model(model_path)

        print(f"\n✅ Success! User enrolled")
        print(f"📁 Model saved to: {model_path}")

        print("\n📊 Enrollment Summary:")
        print(f"   User ID: {user_id}")
        print(f"   Images: {len(existing_images)}")
        print(f"   Model: {config.biometric.model_name}")

    else:
        print("\n❌ Enrollment failed")
        print("   Check that images contain clear faces")

    print("\n" + "="*70)
    print("Next Steps:")
    print("1. Run: python examples/02_authentication.py")
    print("2. Try enrolling more users")
    print("3. Experiment with different model settings")
    print("="*70)


if __name__ == "__main__":
    main()
