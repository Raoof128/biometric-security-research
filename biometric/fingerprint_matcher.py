"""
Fingerprint matching system using ORB feature detection.
Simplified implementation for security research demonstration.
"""

import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_ubyte
import pickle
import os


class FingerprintMatcher:
    """
    Fingerprint authentication system using ORB feature matching.
    Note: This is a simplified implementation for research purposes.
    Production systems would use minutiae extraction and specialized algorithms.
    """

    def __init__(self, threshold=0.4):
        """
        Initialize fingerprint matcher

        Args:
            threshold: Matching threshold (0.0-1.0)
        """
        self.enrolled_fingerprints = {}
        self.threshold = threshold
        self.orb = cv2.ORB_create(nfeatures=500)
        print(f"[+] FingerprintMatcher initialized with threshold {threshold}")

    def preprocess_fingerprint(self, image_path):
        """
        Preprocess fingerprint image for feature extraction

        Args:
            image_path: Path to fingerprint image

        Returns:
            numpy.ndarray: Preprocessed fingerprint image
        """
        if not os.path.exists(image_path):
            print(f"[-] Image not found: {image_path}")
            return None

        # Read as grayscale
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            print(f"[-] Failed to read image: {image_path}")
            return None

        # Normalize
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)

        # Apply Gaussian blur to remove noise
        img = cv2.GaussianBlur(img, (5, 5), 0)

        # Adaptive thresholding for better edge detection
        img = cv2.adaptiveThreshold(
            img, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        # Morphological operations to enhance ridge structure
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

        # Skeletonize to extract ridge structure
        try:
            skeleton = skeletonize(img // 255)
            skeleton = img_as_ubyte(skeleton)
        except Exception as e:
            print(f"[-] Skeletonization failed: {e}")
            skeleton = img

        return skeleton

    def extract_features(self, preprocessed_img):
        """
        Extract features using ORB detector

        Args:
            preprocessed_img: Preprocessed fingerprint image

        Returns:
            tuple: (keypoints, descriptors)
        """
        if preprocessed_img is None:
            return None, None

        keypoints, descriptors = self.orb.detectAndCompute(preprocessed_img, None)

        return keypoints, descriptors

    def enroll_fingerprint(self, user_id, image_path):
        """
        Enroll fingerprint for a user

        Args:
            user_id: Unique identifier for user
            image_path: Path to fingerprint image

        Returns:
            bool: True if enrollment successful
        """
        print(f"[*] Enrolling fingerprint for {user_id}...")

        preprocessed = self.preprocess_fingerprint(image_path)
        if preprocessed is None:
            print(f"[-] Failed to preprocess fingerprint")
            return False

        keypoints, descriptors = self.extract_features(preprocessed)

        if descriptors is None or len(keypoints) == 0:
            print(f"[-] No features detected in fingerprint")
            return False

        self.enrolled_fingerprints[user_id] = {
            'keypoints': keypoints,
            'descriptors': descriptors,
            'num_features': len(keypoints)
        }

        print(f"[+] Fingerprint enrolled for {user_id} with {len(keypoints)} features")
        return True

    def match_fingerprint(self, image_path):
        """
        Match fingerprint against enrolled database

        Args:
            image_path: Path to fingerprint image to match

        Returns:
            tuple: (user_id, match_score) or (None, score)
        """
        if not self.enrolled_fingerprints:
            print("[-] No enrolled fingerprints in database")
            return None, 0.0

        preprocessed = self.preprocess_fingerprint(image_path)
        if preprocessed is None:
            return None, 0.0

        query_kp, query_desc = self.extract_features(preprocessed)

        if query_desc is None or len(query_kp) == 0:
            print("[-] No features detected in query fingerprint")
            return None, 0.0

        best_match = None
        best_score = 0

        # BFMatcher with Hamming distance for ORB
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        for user_id, data in self.enrolled_fingerprints.items():
            if data['descriptors'] is None:
                continue

            try:
                matches = bf.match(query_desc, data['descriptors'])
                matches = sorted(matches, key=lambda x: x.distance)

                # Calculate match score based on good matches
                good_matches = [m for m in matches if m.distance < 50]

                # Normalize by the maximum number of features
                max_features = max(len(query_kp), data['num_features'])
                score = len(good_matches) / max_features if max_features > 0 else 0

                if score > best_score:
                    best_score = score
                    best_match = user_id

            except Exception as e:
                print(f"[-] Error matching with {user_id}: {e}")
                continue

        if best_score >= self.threshold:
            return best_match, best_score
        return None, best_score

    def visualize_match(self, image1_path, image2_path, output_path='fingerprint_match.jpg'):
        """
        Visualize fingerprint matching for debugging

        Args:
            image1_path: Path to first fingerprint
            image2_path: Path to second fingerprint
            output_path: Path to save visualization
        """
        img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

        if img1 is None or img2 is None:
            print("[-] Failed to load images for visualization")
            return

        # Detect features
        kp1, desc1 = self.orb.detectAndCompute(img1, None)
        kp2, desc2 = self.orb.detectAndCompute(img2, None)

        if desc1 is None or desc2 is None:
            print("[-] No features to visualize")
            return

        # Match features
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(desc1, desc2)
        matches = sorted(matches, key=lambda x: x.distance)

        # Draw matches
        img_matches = cv2.drawMatches(
            img1, kp1, img2, kp2, matches[:50],
            None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )

        cv2.imwrite(output_path, img_matches)
        print(f"[+] Match visualization saved to {output_path}")

    def save_database(self, filepath):
        """Save enrolled fingerprints database"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Convert keypoints to serializable format
        save_data = {}
        for user_id, data in self.enrolled_fingerprints.items():
            save_data[user_id] = {
                'descriptors': data['descriptors'],
                'num_features': data['num_features'],
                # Store keypoint coordinates only
                'keypoint_coords': [(kp.pt, kp.size, kp.angle) for kp in data['keypoints']]
            }

        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)
        print(f"[+] Fingerprint database saved to {filepath}")

    def load_database(self, filepath):
        """Load enrolled fingerprints database"""
        if not os.path.exists(filepath):
            print(f"[-] Database file not found: {filepath}")
            return False

        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)

        # Reconstruct keypoints
        self.enrolled_fingerprints = {}
        for user_id, data in save_data.items():
            keypoints = []
            for pt, size, angle in data['keypoint_coords']:
                kp = cv2.KeyPoint(x=pt[0], y=pt[1], size=size, angle=angle)
                keypoints.append(kp)

            self.enrolled_fingerprints[user_id] = {
                'keypoints': keypoints,
                'descriptors': data['descriptors'],
                'num_features': data['num_features']
            }

        print(f"[+] Fingerprint database loaded from {filepath} ({len(self.enrolled_fingerprints)} users)")
        return True

    def get_stats(self):
        """Get statistics about enrolled fingerprints"""
        if not self.enrolled_fingerprints:
            return "No fingerprints enrolled"

        stats = []
        stats.append(f"Total enrolled users: {len(self.enrolled_fingerprints)}")
        stats.append("\nFeature counts:")

        for user_id, data in self.enrolled_fingerprints.items():
            stats.append(f"  {user_id}: {data['num_features']} features")

        return "\n".join(stats)
