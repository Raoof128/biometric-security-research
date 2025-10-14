"""
Liveness detection and anti-spoofing defenses.
Implements multiple techniques: blink detection, texture analysis, active flash, depth analysis.
"""

import cv2
import numpy as np
from scipy.spatial import distance as dist
import os
import time


class LivenessDetector:
    """
    Multi-method liveness detection system.
    Combines blink detection, texture analysis, and active tests.
    """

    def __init__(self, use_dlib=True):
        """
        Initialize liveness detector

        Args:
            use_dlib: Whether to use dlib for facial landmarks (more accurate)
        """
        self.use_dlib = use_dlib

        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )

        # Try to load dlib if available
        self.dlib_detector = None
        self.dlib_predictor = None

        if use_dlib:
            try:
                import dlib
                self.dlib_detector = dlib.get_frontal_face_detector()

                # Try to load shape predictor from multiple possible locations
                possible_paths = [
                    'biometric/models/shape_predictor_68_face_landmarks.dat',
                    os.path.join(os.path.dirname(__file__), '..', 'biometric', 'models', 'shape_predictor_68_face_landmarks.dat'),
                    os.path.expanduser('~/shape_predictor_68_face_landmarks.dat'),
                ]

                predictor_loaded = False
                for predictor_path in possible_paths:
                    if os.path.exists(predictor_path):
                        self.dlib_predictor = dlib.shape_predictor(predictor_path)
                        print(f"[+] Dlib facial landmarks loaded from {predictor_path}")
                        predictor_loaded = True
                        break

                if not predictor_loaded:
                    print("[!] Dlib predictor not found, using OpenCV fallback")
                    print("[*] Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
                    self.use_dlib = False
            except ImportError:
                print("[!] Dlib not available, using OpenCV fallback")
                self.use_dlib = False

        # Eye aspect ratio threshold
        self.EAR_THRESHOLD = 0.25
        self.BLINK_FRAMES = 2

        self.blink_counter = 0
        self.total_blinks = 0

        print(f"[+] LivenessDetector initialized (dlib: {self.use_dlib})")

    def eye_aspect_ratio(self, eye):
        """
        Calculate eye aspect ratio for blink detection

        Args:
            eye: List of (x, y) coordinates for eye landmarks

        Returns:
            float: Eye aspect ratio
        """
        # Compute distances between vertical eye landmarks
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # Compute distance between horizontal eye landmarks
        C = dist.euclidean(eye[0], eye[3])

        # Calculate EAR
        ear = (A + B) / (2.0 * C)
        return ear

    def detect_blink_dlib(self, frame):
        """
        Detect eye blinks using dlib facial landmarks

        Args:
            frame: Input frame

        Returns:
            tuple: (is_live, annotated_frame)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.dlib_detector(gray, 0)

        if len(faces) == 0:
            return False, frame

        face = faces[0]
        landmarks = self.dlib_predictor(gray, face)

        # Extract eye coordinates
        left_eye = []
        right_eye = []

        for n in range(36, 42):  # Left eye landmarks
            left_eye.append((landmarks.part(n).x, landmarks.part(n).y))
        for n in range(42, 48):  # Right eye landmarks
            right_eye.append((landmarks.part(n).x, landmarks.part(n).y))

        # Calculate EAR for both eyes
        left_ear = self.eye_aspect_ratio(left_eye)
        right_ear = self.eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        # Check for blink
        if ear < self.EAR_THRESHOLD:
            self.blink_counter += 1
        else:
            if self.blink_counter >= self.BLINK_FRAMES:
                self.total_blinks += 1
            self.blink_counter = 0

        # Draw eye contours
        for pt in left_eye + right_eye:
            cv2.circle(frame, pt, 2, (0, 255, 0), -1)

        # Display info
        cv2.putText(frame, f"Blinks: {self.total_blinks}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        is_live = self.total_blinks > 0
        return is_live, frame

    def detect_blink_opencv(self, frame):
        """
        Detect blinks using OpenCV (fallback method)

        Args:
            frame: Input frame

        Returns:
            tuple: (is_live, annotated_frame)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return False, frame

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)

            # Simple blink detection: if eyes disappear temporarily
            if len(eyes) < 2:
                self.blink_counter += 1
            else:
                if self.blink_counter >= self.BLINK_FRAMES:
                    self.total_blinks += 1
                self.blink_counter = 0

            # Draw eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)

        cv2.putText(frame, f"Blinks: {self.total_blinks}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        is_live = self.total_blinks > 0
        return is_live, frame

    def detect_blink(self, frame):
        """
        Detect blink (uses dlib if available, else OpenCV)

        Args:
            frame: Input frame

        Returns:
            tuple: (is_live, annotated_frame)
        """
        if self.use_dlib and self.dlib_predictor is not None:
            return self.detect_blink_dlib(frame)
        else:
            return self.detect_blink_opencv(frame)

    def reset_blink_counter(self):
        """Reset blink counter for new session"""
        self.blink_counter = 0
        self.total_blinks = 0

    def texture_analysis(self, image_path):
        """
        Detect printed photo based on texture analysis using LBP

        Args:
            image_path: Path to image

        Returns:
            tuple: (is_real, entropy_score)
        """
        if not os.path.exists(image_path):
            return False, 0.0

        img = cv2.imread(image_path)
        if img is None:
            return False, 0.0

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Calculate Local Binary Pattern (LBP) for texture
        lbp = self.compute_lbp(gray)

        # Calculate histogram
        hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
        hist = hist.astype("float")
        hist /= (hist.sum() + 1e-6)

        # High entropy suggests real face, low entropy suggests printed photo
        entropy = -np.sum(hist * np.log2(hist + 1e-10))

        # Threshold determined empirically (adjust based on testing)
        is_real = entropy > 5.0

        return is_real, entropy

    def compute_lbp(self, image, radius=1, n_points=8):
        """
        Compute Local Binary Pattern for texture analysis

        Args:
            image: Grayscale image
            radius: Radius for sampling
            n_points: Number of sampling points

        Returns:
            numpy.ndarray: LBP image
        """
        h, w = image.shape
        lbp = np.zeros((h-2*radius, w-2*radius), dtype=np.uint8)

        for i in range(radius, h-radius):
            for j in range(radius, w-radius):
                center = image[i, j]
                code = 0

                # Sample neighbors in circular pattern
                for k in range(n_points):
                    angle = 2 * np.pi * k / n_points
                    x = int(i + radius * np.cos(angle))
                    y = int(j - radius * np.sin(angle))

                    # Ensure within bounds
                    x = max(0, min(h-1, x))
                    y = max(0, min(w-1, y))

                    if image[x, y] >= center:
                        code |= (1 << k)

                lbp[i-radius, j-radius] = code

        return lbp

    def active_flash_test(self, duration=2.0):
        """
        Perform active flash liveness test using webcam

        Args:
            duration: Duration of test in seconds

        Returns:
            tuple: (is_live, mean_difference)
        """
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("[-] Could not open webcam")
            return False, 0.0

        print("[*] Active flash liveness test")
        print("[*] Capturing frames with different illuminations...")

        frames = []

        # Capture frame with normal light
        time.sleep(0.5)
        ret, frame1 = cap.read()
        if ret:
            frames.append(cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY))
            cv2.imshow('Flash Test', frame1)
            cv2.waitKey(500)

        # Create white flash
        flash = np.ones((480, 640, 3), dtype=np.uint8) * 255
        cv2.imshow('Flash Test', flash)
        cv2.waitKey(200)

        # Capture frame during flash
        ret, frame2 = cap.read()
        if ret:
            frames.append(cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY))
            cv2.imshow('Flash Test', frame2)
            cv2.waitKey(500)

        cv2.destroyAllWindows()
        cap.release()

        if len(frames) == 2:
            # Detect faces in both frames
            face1_roi = self._extract_face_roi(frames[0])
            face2_roi = self._extract_face_roi(frames[1])

            if face1_roi is not None and face2_roi is not None:
                # Ensure same size
                h, w = min(face1_roi.shape[0], face2_roi.shape[0]), \
                       min(face1_roi.shape[1], face2_roi.shape[1])
                face1_roi = cv2.resize(face1_roi, (w, h))
                face2_roi = cv2.resize(face2_roi, (w, h))

                # Calculate pixel difference
                diff = cv2.absdiff(face1_roi, face2_roi)
                mean_diff = np.mean(diff)

                # Real faces show significant reflection difference
                # Photos/screens show minimal difference
                is_live = mean_diff > 10.0

                print(f"[*] Mean pixel difference: {mean_diff:.2f}")
                print(f"[*] Liveness result: {'LIVE' if is_live else 'SPOOF'}")

                return is_live, mean_diff

        return False, 0.0

    def _extract_face_roi(self, gray_image):
        """Extract face region from grayscale image"""
        faces = self.face_cascade.detectMultiScale(gray_image, 1.1, 5)

        if len(faces) > 0:
            x, y, w, h = faces[0]
            return gray_image[y:y+h, x:x+w]

        return None

    def depth_analysis(self, image_path):
        """
        Simulate depth analysis (2D vs 3D detection)

        Args:
            image_path: Path to image

        Returns:
            tuple: (is_3d, edge_density)
        """
        if not os.path.exists(image_path):
            return False, 0.0

        img = cv2.imread(image_path)
        if img is None:
            return False, 0.0

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Count edge pixels
        edge_density = np.sum(edges > 0) / edges.size

        # Real 3D faces have more complex depth, resulting in varied edges
        # 2D photos have more uniform edges
        is_3d = edge_density > 0.1 and edge_density < 0.3

        return is_3d, edge_density

    def color_diversity_analysis(self, image_path):
        """
        Analyze color diversity (real skin has micro-variations)

        Args:
            image_path: Path to image

        Returns:
            tuple: (is_real, diversity_score)
        """
        if not os.path.exists(image_path):
            return False, 0.0

        img = cv2.imread(image_path)
        if img is None:
            return False, 0.0

        # Detect face region
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

        if len(faces) == 0:
            return False, 0.0

        x, y, w, h = faces[0]
        face_roi = img[y:y+h, x:x+w]

        # Calculate color histogram in LAB space
        lab = cv2.cvtColor(face_roi, cv2.COLOR_BGR2LAB)

        # Calculate standard deviation for each channel
        l_std = np.std(lab[:,:,0])
        a_std = np.std(lab[:,:,1])
        b_std = np.std(lab[:,:,2])

        diversity_score = (l_std + a_std + b_std) / 3.0

        # Real faces have higher color diversity
        is_real = diversity_score > 15.0

        return is_real, diversity_score


class AntiSpoofingSystem:
    """
    Comprehensive anti-spoofing system combining multiple detection methods.
    """

    def __init__(self):
        """Initialize anti-spoofing system"""
        self.liveness = LivenessDetector()
        print("[+] AntiSpoofingSystem initialized")

    def comprehensive_check(self, image_path, use_webcam=False):
        """
        Run all anti-spoofing checks on an image

        Args:
            image_path: Path to image to test
            use_webcam: Whether to perform webcam-based tests

        Returns:
            dict: Results from all checks
        """
        results = {
            'image_path': image_path,
            'checks': {},
            'final_decision': False,
            'confidence': 0.0
        }

        print(f"[*] Running comprehensive anti-spoofing check on: {image_path}")

        # Texture analysis
        is_real_texture, entropy = self.liveness.texture_analysis(image_path)
        results['checks']['texture'] = {
            'is_real': is_real_texture,
            'entropy': float(entropy),
            'weight': 0.3
        }
        print(f"    [*] Texture analysis: {'REAL' if is_real_texture else 'SPOOF'} (entropy: {entropy:.2f})")

        # Depth analysis
        is_3d, edge_density = self.liveness.depth_analysis(image_path)
        results['checks']['depth'] = {
            'is_3d': is_3d,
            'edge_density': float(edge_density),
            'weight': 0.25
        }
        print(f"    [*] Depth analysis: {'3D' if is_3d else '2D'} (edge density: {edge_density:.3f})")

        # Color diversity
        is_real_color, diversity = self.liveness.color_diversity_analysis(image_path)
        results['checks']['color_diversity'] = {
            'is_real': is_real_color,
            'diversity_score': float(diversity),
            'weight': 0.25
        }
        print(f"    [*] Color diversity: {'REAL' if is_real_color else 'SPOOF'} (score: {diversity:.2f})")

        # Blink detection (if webcam)
        if use_webcam:
            print("    [*] Performing blink detection (look at camera and blink)...")
            cap = cv2.VideoCapture(0)
            self.liveness.reset_blink_counter()

            start_time = time.time()
            blink_detected = False

            while time.time() - start_time < 5.0:  # 5 second window
                ret, frame = cap.read()
                if not ret:
                    break

                is_live, annotated = self.liveness.detect_blink(frame)
                cv2.imshow('Blink Detection', annotated)

                if is_live:
                    blink_detected = True
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

            results['checks']['blink'] = {
                'is_live': blink_detected,
                'weight': 0.2
            }
            print(f"    [*] Blink detection: {'LIVE' if blink_detected else 'NO BLINK'}")

        # Calculate weighted score
        total_weight = sum(check['weight'] for check in results['checks'].values())
        weighted_score = 0.0

        for check_name, check_data in results['checks'].items():
            if 'is_real' in check_data:
                weighted_score += check_data['is_real'] * check_data['weight']
            elif 'is_3d' in check_data:
                weighted_score += check_data['is_3d'] * check_data['weight']
            elif 'is_live' in check_data:
                weighted_score += check_data['is_live'] * check_data['weight']

        confidence = weighted_score / total_weight
        results['confidence'] = confidence
        results['final_decision'] = confidence >= 0.5

        print(f"\n[*] Final decision: {'REAL' if results['final_decision'] else 'SPOOF'} (confidence: {confidence:.2%})")

        return results

    def batch_test(self, image_paths):
        """
        Test multiple images

        Args:
            image_paths: List of image paths

        Returns:
            list: Results for each image
        """
        results = []

        for image_path in image_paths:
            result = self.comprehensive_check(image_path, use_webcam=False)
            results.append(result)

        return results
