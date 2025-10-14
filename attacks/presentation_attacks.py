"""
Presentation attack simulation module.
Generates photo attacks, video replays, mask simulations, and synthetic fingerprints.
"""

import cv2
import numpy as np
from PIL import Image
import os


class PresentationAttacks:
    """
    Simulate various presentation attacks for security testing.
    """

    def __init__(self, output_dir='data/attack_samples'):
        """
        Initialize presentation attack simulator

        Args:
            output_dir: Directory to save generated attack samples
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print(f"[+] PresentationAttacks initialized, output: {output_dir}")

    def photo_attack(self, genuine_image_path, attack_name='photo_attack'):
        """
        Simulate photo presentation attack (printed photo or screen display)

        Args:
            genuine_image_path: Path to genuine face image
            attack_name: Name for the attack sample

        Returns:
            str: Path to generated attack image
        """
        if not os.path.exists(genuine_image_path):
            print(f"[-] Genuine image not found: {genuine_image_path}")
            return None

        img = cv2.imread(genuine_image_path)
        if img is None:
            print(f"[-] Failed to read image: {genuine_image_path}")
            return None

        # Add paper/screen texture
        texture = np.random.normal(0, 5, img.shape).astype(np.uint8)
        photo_attack = cv2.add(img, texture)

        # Add slight reflection/glare (common in photos)
        h, w = img.shape[:2]
        glare_mask = np.zeros((h, w), dtype=np.uint8)

        # Random glare position
        glare_x = np.random.randint(w//4, 3*w//4)
        glare_y = np.random.randint(h//4, 3*h//4)
        glare_radius = min(w, h) // 4

        cv2.circle(glare_mask, (glare_x, glare_y), glare_radius, 255, -1)
        glare_mask = cv2.GaussianBlur(glare_mask, (51, 51), 0)

        photo_attack = cv2.addWeighted(
            photo_attack, 0.8,
            cv2.cvtColor(glare_mask, cv2.COLOR_GRAY2BGR), 0.2, 0
        )

        # Reduce color depth slightly (printing effect)
        photo_attack = (photo_attack // 16) * 16

        output_path = os.path.join(self.output_dir, f'{attack_name}.jpg')
        cv2.imwrite(output_path, photo_attack)
        print(f"[+] Photo attack generated: {output_path}")

        return output_path

    def video_replay_attack(self, genuine_video_path, output_frames=30, attack_name='replay_attack'):
        """
        Extract frames from video for replay attack simulation

        Args:
            genuine_video_path: Path to genuine video or use webcam
            output_frames: Number of frames to extract
            attack_name: Base name for attack frames

        Returns:
            list: Paths to generated frame images
        """
        if genuine_video_path == 'webcam':
            cap = cv2.VideoCapture(0)
            print("[*] Using webcam for video capture. Press 'q' to stop.")
        else:
            if not os.path.exists(genuine_video_path):
                print(f"[-] Video not found: {genuine_video_path}")
                return []
            cap = cv2.VideoCapture(genuine_video_path)

        if not cap.isOpened():
            print("[-] Error opening video source")
            return []

        frames = []
        count = 0

        while count < output_frames:
            ret, frame = cap.read()
            if not ret:
                break

            # Add digital screen artifacts
            frame = self.add_screen_artifacts(frame)

            output_path = os.path.join(
                self.output_dir,
                f'{attack_name}_frame_{count:03d}.jpg'
            )
            cv2.imwrite(output_path, frame)
            frames.append(output_path)
            count += 1

            # Show frame if using webcam
            if genuine_video_path == 'webcam':
                cv2.imshow('Capturing frames', frame)
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break

        cap.release()
        if genuine_video_path == 'webcam':
            cv2.destroyAllWindows()

        print(f"[+] Video replay attack generated: {len(frames)} frames")
        return frames

    def add_screen_artifacts(self, image):
        """
        Add screen display artifacts to image (pixel grid, moire pattern)

        Args:
            image: Input image

        Returns:
            numpy.ndarray: Image with screen artifacts
        """
        h, w = image.shape[:2]
        overlay = np.zeros_like(image)

        # Add pixel grid pattern
        for i in range(0, h, 2):
            overlay[i, :] = [1, 1, 1]
        for j in range(0, w, 2):
            overlay[:, j] = [1, 1, 1]

        # Add moire pattern
        x = np.arange(w)
        y = np.arange(h)
        X, Y = np.meshgrid(x, y)
        moire = np.sin(X * 0.1) * np.sin(Y * 0.1) * 5
        moire = moire.astype(np.uint8)
        moire = cv2.cvtColor(moire, cv2.COLOR_GRAY2BGR)

        # Combine artifacts
        result = cv2.addWeighted(image, 0.92, overlay, 0.05, 0)
        result = cv2.addWeighted(result, 0.97, moire, 0.03, 0)

        # Reduce sharpness (screens have limited resolution)
        result = cv2.GaussianBlur(result, (3, 3), 0)

        return result

    def mask_attack_simulation(self, genuine_image_path, attack_name='mask_attack'):
        """
        Simulate 3D mask attack characteristics

        Args:
            genuine_image_path: Path to genuine face image
            attack_name: Name for attack sample

        Returns:
            str: Path to generated attack image
        """
        if not os.path.exists(genuine_image_path):
            print(f"[-] Genuine image not found: {genuine_image_path}")
            return None

        img = cv2.imread(genuine_image_path)
        if img is None:
            print(f"[-] Failed to read image: {genuine_image_path}")
            return None

        # Reduce facial micro-details (masks lack fine texture)
        mask_img = cv2.bilateralFilter(img, 15, 80, 80)

        # Add slight warping (imperfect mask fit)
        h, w = img.shape[:2]
        map_x = np.zeros((h, w), dtype=np.float32)
        map_y = np.zeros((h, w), dtype=np.float32)

        for i in range(h):
            for j in range(w):
                map_x[i, j] = j + 2 * np.sin(i / 20.0)
                map_y[i, j] = i + 2 * np.cos(j / 20.0)

        mask_img = cv2.remap(
            mask_img, map_x, map_y,
            cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
        )

        # Reduce color variation (masks have uniform material)
        mask_img = cv2.fastNlMeansDenoisingColored(mask_img, None, 10, 10, 7, 21)

        # Make skin tone slightly more uniform
        mask_img = (mask_img // 8) * 8

        # Add slight plastic sheen
        sheen = np.ones_like(mask_img) * 10
        mask_img = cv2.add(mask_img, sheen)

        output_path = os.path.join(self.output_dir, f'{attack_name}.jpg')
        cv2.imwrite(output_path, mask_img)
        print(f"[+] Mask attack simulation generated: {output_path}")

        return output_path

    def synthetic_fingerprint(self, base_pattern='arch', attack_name='synthetic_fingerprint'):
        """
        Generate synthetic fingerprint pattern

        Args:
            base_pattern: 'arch', 'loop', or 'whorl'
            attack_name: Name for attack sample

        Returns:
            str: Path to generated synthetic fingerprint
        """
        size = 300
        img = np.zeros((size, size), dtype=np.uint8)

        center = (size // 2, size // 2)

        # Generate ridge patterns based on type
        if base_pattern == 'arch':
            # Arch pattern
            for r in range(20, size // 2, 6):
                cv2.ellipse(img, center, (r, r // 2), 0, 180, 360, 255, 2)

        elif base_pattern == 'loop':
            # Loop pattern
            for r in range(20, size // 2, 6):
                cv2.ellipse(img, center, (r, r), 0, 90, 270, 255, 2)
                # Add loop curve
                offset_y = r // 2
                cv2.ellipse(img, (center[0], center[1] - offset_y),
                           (r // 2, r // 3), 0, 0, 180, 255, 2)

        elif base_pattern == 'whorl':
            # Whorl pattern (circular)
            for r in range(20, size // 2, 6):
                cv2.circle(img, center, r, 255, 2)

        else:
            # Default to random pattern
            for r in range(20, size // 2, 6):
                cv2.ellipse(img, center, (r, r), 0, 0, 360, 255, 2)

        # Add minutiae points (ridge endings and bifurcations)
        num_minutiae = np.random.randint(20, 40)
        for _ in range(num_minutiae):
            x = np.random.randint(50, size - 50)
            y = np.random.randint(50, size - 50)
            cv2.circle(img, (x, y), 2, 0, -1)  # Dark dots for minutiae

        # Add noise to make it look realistic
        noise = np.random.randint(0, 50, (size, size), dtype=np.uint8)
        img = cv2.add(img, noise)

        # Add some random breaks in ridges
        for _ in range(15):
            x1 = np.random.randint(0, size)
            y1 = np.random.randint(0, size)
            x2 = x1 + np.random.randint(-10, 10)
            y2 = y1 + np.random.randint(-10, 10)
            cv2.line(img, (x1, y1), (x2, y2), 0, 2)

        output_path = os.path.join(
            self.output_dir,
            f'{attack_name}_{base_pattern}.jpg'
        )
        cv2.imwrite(output_path, img)
        print(f"[+] Synthetic fingerprint generated: {output_path}")

        return output_path

    def degraded_quality_attack(self, genuine_image_path, attack_name='degraded_attack'):
        """
        Create degraded quality image (low resolution, compression artifacts)

        Args:
            genuine_image_path: Path to genuine image
            attack_name: Name for attack sample

        Returns:
            str: Path to generated attack image
        """
        if not os.path.exists(genuine_image_path):
            print(f"[-] Genuine image not found: {genuine_image_path}")
            return None

        img = cv2.imread(genuine_image_path)
        if img is None:
            return None

        # Downscale to low resolution
        h, w = img.shape[:2]
        small = cv2.resize(img, (w // 4, h // 4), interpolation=cv2.INTER_AREA)

        # Upscale back (creates pixelation)
        degraded = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

        # Add JPEG compression artifacts
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 20]
        _, encimg = cv2.imencode('.jpg', degraded, encode_param)
        degraded = cv2.imdecode(encimg, 1)

        # Add noise
        noise = np.random.randint(-20, 20, degraded.shape, dtype=np.int16)
        degraded = np.clip(degraded.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        output_path = os.path.join(self.output_dir, f'{attack_name}.jpg')
        cv2.imwrite(output_path, degraded)
        print(f"[+] Degraded quality attack generated: {output_path}")

        return output_path

    def batch_generate_attacks(self, genuine_image_path, attack_types=None):
        """
        Generate multiple attack types from a single genuine image

        Args:
            genuine_image_path: Path to genuine image
            attack_types: List of attack types to generate
                         ['photo', 'mask', 'degraded'] for faces
                         ['synthetic'] for fingerprints

        Returns:
            dict: Dictionary of attack type to generated file path
        """
        if attack_types is None:
            attack_types = ['photo', 'mask', 'degraded']

        base_name = os.path.splitext(os.path.basename(genuine_image_path))[0]
        results = {}

        print(f"[*] Generating {len(attack_types)} attack types for {base_name}")

        for attack_type in attack_types:
            if attack_type == 'photo':
                path = self.photo_attack(genuine_image_path, f'{base_name}_photo')
                results['photo'] = path

            elif attack_type == 'mask':
                path = self.mask_attack_simulation(genuine_image_path, f'{base_name}_mask')
                results['mask'] = path

            elif attack_type == 'degraded':
                path = self.degraded_quality_attack(genuine_image_path, f'{base_name}_degraded')
                results['degraded'] = path

            elif attack_type == 'synthetic':
                # For fingerprints
                for pattern in ['arch', 'loop', 'whorl']:
                    path = self.synthetic_fingerprint(pattern, f'{base_name}_synthetic')
                    results[f'synthetic_{pattern}'] = path

        print(f"[+] Batch attack generation complete: {len(results)} attacks created")
        return results
