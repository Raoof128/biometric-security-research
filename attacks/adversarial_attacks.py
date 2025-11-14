"""
Advanced adversarial attack methods.
Implements adversarial patches and perturbation-based attacks.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import os

from utils.logger import get_logger

logger = get_logger(__name__)


class AdversarialAttacker:
    """
    Generate adversarial examples to fool biometric systems
    """

    def __init__(self, output_dir: str = 'data/attack_samples/adversarial'):
        """
        Initialize adversarial attacker

        Args:
            output_dir: Directory to save adversarial examples
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Adversarial attacker initialized, output: {output_dir}")

    def generate_adversarial_patch(
        self,
        base_image_path: str,
        patch_size: Tuple[int, int] = (50, 50),
        patch_position: Optional[Tuple[int, int]] = None,
        attack_name: str = 'adversarial_patch'
    ) -> Optional[str]:
        """
        Generate adversarial patch attack

        Args:
            base_image_path: Path to base image
            patch_size: Size of adversarial patch (width, height)
            patch_position: Position to place patch (x, y), None for random
            attack_name: Name for output file

        Returns:
            str: Path to generated attack image
        """
        if not os.path.exists(base_image_path):
            logger.error(f"Base image not found: {base_image_path}")
            return None

        img = cv2.imread(base_image_path)
        if img is None:
            logger.error(f"Failed to read image: {base_image_path}")
            return None

        h, w = img.shape[:2]
        patch_w, patch_h = patch_size

        # Generate adversarial patch
        # This is a simplified version - real adversarial patches would be optimized
        # using gradient-based methods targeting specific models
        patch = self._generate_optimized_patch(patch_size)

        # Determine patch position
        if patch_position is None:
            # Random position, avoiding edges
            max_x = w - patch_w - 10
            max_y = h - patch_h - 10
            patch_x = np.random.randint(10, max_x) if max_x > 10 else 10
            patch_y = np.random.randint(10, max_y) if max_y > 10 else 10
        else:
            patch_x, patch_y = patch_position

        # Apply patch to image
        result = img.copy()
        result[patch_y:patch_y+patch_h, patch_x:patch_x+patch_w] = patch

        # Save result
        output_path = os.path.join(self.output_dir, f'{attack_name}.jpg')
        cv2.imwrite(output_path, result)

        logger.info(f"Adversarial patch attack generated: {output_path}")
        return output_path

    def _generate_optimized_patch(self, size: Tuple[int, int]) -> np.ndarray:
        """
        Generate optimized adversarial patch

        Args:
            size: Patch size (width, height)

        Returns:
            numpy.ndarray: Adversarial patch
        """
        w, h = size

        # Create patch with high-frequency patterns that confuse CNNs
        patch = np.zeros((h, w, 3), dtype=np.uint8)

        # Add checkerboard pattern (high frequency)
        for i in range(h):
            for j in range(w):
                if (i // 5 + j // 5) % 2 == 0:
                    patch[i, j] = [255, 0, 255]  # Magenta
                else:
                    patch[i, j] = [0, 255, 255]  # Cyan

        # Add noise
        noise = np.random.randint(-30, 30, (h, w, 3), dtype=np.int16)
        patch = np.clip(patch.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Add geometric patterns
        center = (w // 2, h // 2)
        cv2.circle(patch, center, min(w, h) // 4, (255, 255, 0), 2)

        # Add diagonal lines
        cv2.line(patch, (0, 0), (w-1, h-1), (0, 0, 0), 2)
        cv2.line(patch, (w-1, 0), (0, h-1), (255, 255, 255), 2)

        return patch

    def generate_fgsm_attack(
        self,
        image_path: str,
        epsilon: float = 0.1,
        attack_name: str = 'fgsm_attack'
    ) -> Optional[str]:
        """
        Generate Fast Gradient Sign Method (FGSM) attack

        Args:
            image_path: Path to original image
            epsilon: Perturbation magnitude (0.0 to 1.0)
            attack_name: Name for output file

        Returns:
            str: Path to adversarial example
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None

        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to read image: {image_path}")
            return None

        # Normalize image to [0, 1]
        img_normalized = img.astype(np.float32) / 255.0

        # Generate pseudo-gradient (simplified - real FGSM needs model gradients)
        # This creates a universal perturbation pattern
        h, w = img.shape[:2]
        gradient_sign = np.random.choice([-1, 1], size=(h, w, 3))

        # Apply perturbation
        perturbation = epsilon * gradient_sign
        adversarial = np.clip(img_normalized + perturbation, 0, 1)

        # Convert back to uint8
        adversarial = (adversarial * 255).astype(np.uint8)

        # Save result
        output_path = os.path.join(self.output_dir, f'{attack_name}.jpg')
        cv2.imwrite(output_path, adversarial)

        logger.info(f"FGSM attack generated: {output_path}")
        return output_path

    def generate_glasses_attack(
        self,
        image_path: str,
        attack_name: str = 'glasses_attack'
    ) -> Optional[str]:
        """
        Generate adversarial glasses attack (physical adversarial example)

        Args:
            image_path: Path to face image
            attack_name: Name for output file

        Returns:
            str: Path to attack image
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None

        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to read image: {image_path}")
            return None

        h, w = img.shape[:2]

        # Detect face region (simple center-based approach)
        # In real implementation, use face detection
        face_center_y = h // 2
        face_width = w // 2

        # Create adversarial glasses
        glasses = self._create_adversarial_glasses((face_width, h // 8))

        # Position glasses on face
        glasses_y = int(face_center_y - h * 0.1)
        glasses_x = w // 4
        glasses_h, glasses_w = glasses.shape[:2]

        # Ensure glasses fit in image
        if glasses_y + glasses_h > h or glasses_x + glasses_w > w:
            logger.warning("Glasses don't fit on image, adjusting size")
            glasses = cv2.resize(glasses, (min(glasses_w, w - glasses_x), min(glasses_h, h - glasses_y)))
            glasses_h, glasses_w = glasses.shape[:2]

        # Apply glasses with alpha blending
        result = img.copy()
        roi = result[glasses_y:glasses_y+glasses_h, glasses_x:glasses_x+glasses_w]

        # Simple overlay (in real implementation, use proper alpha blending)
        mask = cv2.cvtColor(glasses, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        # Black out area under glasses
        roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

        # Take glasses region
        glasses_fg = cv2.bitwise_and(glasses, glasses, mask=mask)

        # Combine
        dst = cv2.add(roi_bg, glasses_fg)
        result[glasses_y:glasses_y+glasses_h, glasses_x:glasses_x+glasses_w] = dst

        # Save result
        output_path = os.path.join(self.output_dir, f'{attack_name}.jpg')
        cv2.imwrite(output_path, result)

        logger.info(f"Adversarial glasses attack generated: {output_path}")
        return output_path

    def _create_adversarial_glasses(self, size: Tuple[int, int]) -> np.ndarray:
        """
        Create adversarial glasses pattern

        Args:
            size: Glasses size (width, height)

        Returns:
            numpy.ndarray: Adversarial glasses image
        """
        w, h = size
        glasses = np.zeros((h, w, 3), dtype=np.uint8)

        # Frame
        cv2.rectangle(glasses, (5, 5), (w//2 - 5, h - 5), (50, 50, 50), 2)
        cv2.rectangle(glasses, (w//2 + 5, 5), (w - 5, h - 5), (50, 50, 50), 2)

        # Bridge
        cv2.line(glasses, (w//2 - 5, h//2), (w//2 + 5, h//2), (50, 50, 50), 2)

        # Adversarial pattern in lenses
        # Left lens
        for i in range(5, h-5, 3):
            cv2.line(glasses, (7, i), (w//2 - 7, i),
                    (np.random.randint(200, 255), np.random.randint(0, 100), np.random.randint(200, 255)), 1)

        # Right lens
        for i in range(5, h-5, 3):
            cv2.line(glasses, (w//2 + 7, i), (w - 7, i),
                    (np.random.randint(200, 255), np.random.randint(0, 100), np.random.randint(200, 255)), 1)

        return glasses

    def generate_pixel_attack(
        self,
        image_path: str,
        num_pixels: int = 100,
        attack_name: str = 'pixel_attack'
    ) -> Optional[str]:
        """
        Generate one-pixel/few-pixel attack

        Args:
            image_path: Path to original image
            num_pixels: Number of pixels to perturb
            attack_name: Name for output file

        Returns:
            str: Path to adversarial example
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None

        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to read image: {image_path}")
            return None

        h, w = img.shape[:2]
        result = img.copy()

        # Randomly select pixels to perturb
        for _ in range(num_pixels):
            x = np.random.randint(0, w)
            y = np.random.randint(0, h)

            # Set to adversarial color
            result[y, x] = [np.random.randint(0, 256) for _ in range(3)]

        # Save result
        output_path = os.path.join(self.output_dir, f'{attack_name}.jpg')
        cv2.imwrite(output_path, result)

        logger.info(f"Pixel attack generated: {output_path}")
        return output_path

    def generate_morphing_attack(
        self,
        image1_path: str,
        image2_path: str,
        alpha: float = 0.5,
        attack_name: str = 'morphing_attack'
    ) -> Optional[str]:
        """
        Generate face morphing attack (blend two faces)

        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            alpha: Blending factor (0.0 to 1.0)
            attack_name: Name for output file

        Returns:
            str: Path to morphed image
        """
        if not os.path.exists(image1_path) or not os.path.exists(image2_path):
            logger.error("One or both images not found")
            return None

        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)

        if img1 is None or img2 is None:
            logger.error("Failed to read images")
            return None

        # Resize to same size
        h, w = img1.shape[:2]
        img2_resized = cv2.resize(img2, (w, h))

        # Simple morphing (alpha blending)
        # Real morphing would use facial landmarks for better alignment
        morphed = cv2.addWeighted(img1, alpha, img2_resized, 1 - alpha, 0)

        # Save result
        output_path = os.path.join(self.output_dir, f'{attack_name}.jpg')
        cv2.imwrite(output_path, morphed)

        logger.info(f"Morphing attack generated: {output_path}")
        return output_path

    def batch_generate_adversarial_attacks(
        self,
        image_path: str,
        attack_types: Optional[list] = None
    ) -> dict:
        """
        Generate multiple adversarial attacks from single image

        Args:
            image_path: Path to base image
            attack_types: List of attack types to generate

        Returns:
            dict: Dictionary of attack type to output path
        """
        if attack_types is None:
            attack_types = ['patch', 'fgsm', 'glasses', 'pixel']

        base_name = os.path.splitext(os.path.basename(image_path))[0]
        results = {}

        logger.info(f"Generating {len(attack_types)} adversarial attacks for {base_name}")

        for attack_type in attack_types:
            if attack_type == 'patch':
                path = self.generate_adversarial_patch(image_path, attack_name=f'{base_name}_patch')
                results['patch'] = path

            elif attack_type == 'fgsm':
                path = self.generate_fgsm_attack(image_path, attack_name=f'{base_name}_fgsm')
                results['fgsm'] = path

            elif attack_type == 'glasses':
                path = self.generate_glasses_attack(image_path, attack_name=f'{base_name}_glasses')
                results['glasses'] = path

            elif attack_type == 'pixel':
                path = self.generate_pixel_attack(image_path, attack_name=f'{base_name}_pixel')
                results['pixel'] = path

        logger.info(f"Generated {len(results)} adversarial attacks")
        return results
