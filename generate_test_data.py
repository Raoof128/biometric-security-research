#!/usr/bin/env python3
"""
Generate synthetic test data for demonstration purposes.
Creates sample fingerprints for testing without requiring real biometric data.
"""

import cv2
import numpy as np
import os


def generate_synthetic_face(output_path, color=(100, 150, 180), size=(400, 400)):
    """Generate a simple synthetic face image for testing"""
    img = np.ones((size[0], size[1], 3), dtype=np.uint8) * 240

    # Face shape (ellipse)
    center = (size[0] // 2, size[1] // 2)
    axes = (size[0] // 3, size[1] // 2 - 20)
    cv2.ellipse(img, center, axes, 0, 0, 360, color, -1)

    # Eyes
    eye_y = center[1] - 50
    left_eye_x = center[0] - 60
    right_eye_x = center[0] + 60

    cv2.circle(img, (left_eye_x, eye_y), 15, (255, 255, 255), -1)
    cv2.circle(img, (right_eye_x, eye_y), 15, (255, 255, 255), -1)
    cv2.circle(img, (left_eye_x, eye_y), 8, (50, 50, 50), -1)
    cv2.circle(img, (right_eye_x, eye_y), 8, (50, 50, 50), -1)

    # Nose
    nose_points = np.array([
        [center[0], center[1] - 20],
        [center[0] - 15, center[1] + 20],
        [center[0] + 15, center[1] + 20]
    ])
    cv2.polylines(img, [nose_points], True, (80, 100, 120), 2)

    # Mouth
    mouth_y = center[1] + 60
    cv2.ellipse(img, (center[0], mouth_y), (40, 20), 0, 0, 180, (150, 100, 100), 2)

    # Add some texture
    noise = np.random.randint(-10, 10, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    cv2.imwrite(output_path, img)
    return output_path


def generate_synthetic_fingerprint(output_path, pattern='loop'):
    """Generate a synthetic fingerprint"""
    size = 300
    img = np.zeros((size, size), dtype=np.uint8)

    center = (size // 2, size // 2)

    # Generate ridge patterns
    if pattern == 'arch':
        for r in range(20, size // 2, 6):
            cv2.ellipse(img, center, (r, r // 2), 0, 180, 360, 255, 2)

    elif pattern == 'loop':
        for r in range(20, size // 2, 6):
            cv2.ellipse(img, center, (r, r), 0, 90, 270, 255, 2)
            offset_y = r // 2
            cv2.ellipse(img, (center[0], center[1] - offset_y),
                       (r // 2, r // 3), 0, 0, 180, 255, 2)

    elif pattern == 'whorl':
        for r in range(20, size // 2, 6):
            cv2.circle(img, center, r, 255, 2)

    # Add minutiae points
    num_minutiae = np.random.randint(20, 40)
    for _ in range(num_minutiae):
        x = np.random.randint(50, size - 50)
        y = np.random.randint(50, size - 50)
        cv2.circle(img, (x, y), 2, 0, -1)

    # Add noise
    noise = np.random.randint(0, 50, (size, size), dtype=np.uint8)
    img = cv2.add(img, noise)

    # Add random breaks
    for _ in range(15):
        x1 = np.random.randint(0, size)
        y1 = np.random.randint(0, size)
        x2 = x1 + np.random.randint(-10, 10)
        y2 = y1 + np.random.randint(-10, 10)
        cv2.line(img, (x1, y1), (x2, y2), 0, 2)

    cv2.imwrite(output_path, img)
    return output_path


def main():
    """Generate test data"""
    print("[*] Generating synthetic test data...")

    # Create directories
    os.makedirs('data/demo/alice', exist_ok=True)
    os.makedirs('data/demo/bob', exist_ok=True)
    os.makedirs('data/demo/fingerprints', exist_ok=True)

    # Generate synthetic faces for Alice
    print("[*] Generating faces for Alice...")
    for i in range(3):
        color = tuple(np.random.randint(80, 200, 3).tolist())
        path = generate_synthetic_face(
            f'data/demo/alice/photo_{i+1}.jpg',
            color=color
        )
        print(f"    [+] Generated: {path}")

    # Generate synthetic faces for Bob
    print("[*] Generating faces for Bob...")
    for i in range(3):
        color = tuple(np.random.randint(80, 200, 3).tolist())
        path = generate_synthetic_face(
            f'data/demo/bob/photo_{i+1}.jpg',
            color=color
        )
        print(f"    [+] Generated: {path}")

    # Generate synthetic fingerprints
    print("[*] Generating fingerprints...")
    patterns = ['arch', 'loop', 'whorl']
    for pattern in patterns:
        path = generate_synthetic_fingerprint(
            f'data/demo/fingerprints/{pattern}.jpg',
            pattern=pattern
        )
        print(f"    [+] Generated: {path}")

    print("\n[+] Test data generation complete!")
    print("\nNext steps:")
    print("1. python main.py enroll --user-id alice --modality face --image-dir data/demo/alice/")
    print("2. python main.py authenticate --modality face --image data/demo/alice/photo_1.jpg")
    print("3. python main.py attack --image data/demo/alice/photo_1.jpg --attack-types photo,mask")


if __name__ == '__main__':
    main()
