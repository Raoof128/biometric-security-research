"""
Lightweight deepfake generator using face swapping.
For research and security testing purposes only.
"""

import cv2
import numpy as np
import os


class LightweightDeepfake:
    """
    Simplified deepfake using face swapping techniques.
    This is a lightweight demonstration version for security research.

    Note: Production deepfakes would use advanced models like:
    - First Order Motion Model
    - Face2Face
    - DeepFaceLab
    """

    def __init__(self):
        """Initialize lightweight deepfake generator"""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        print("[+] LightweightDeepfake initialized")

    def detect_face_and_landmarks(self, image):
        """
        Detect face and key landmarks

        Args:
            image: Input image

        Returns:
            tuple: (face_rect, eyes) or (None, None)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
        )

        if len(faces) == 0:
            return None, None

        # Get the largest face
        face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = face

        # Detect eyes within face region
        face_roi_gray = gray[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(face_roi_gray)

        return face, eyes

    def simple_face_swap(self, source_img_path, target_img_path, output_path):
        """
        Simple face swap as lightweight deepfake demo

        Args:
            source_img_path: Path to source face image
            target_img_path: Path to target image
            output_path: Path to save result

        Returns:
            str: Path to generated deepfake or None
        """
        if not os.path.exists(source_img_path) or not os.path.exists(target_img_path):
            print("[-] Source or target image not found")
            return None

        source = cv2.imread(source_img_path)
        target = cv2.imread(target_img_path)

        if source is None or target is None:
            print("[-] Failed to read images")
            return None

        # Detect faces
        source_face, _ = self.detect_face_and_landmarks(source)
        target_face, _ = self.detect_face_and_landmarks(target)

        if source_face is None or target_face is None:
            print("[-] No faces detected in source or target")
            return None

        # Get coordinates
        sx, sy, sw, sh = source_face
        tx, ty, tw, th = target_face

        # Extract source face with margin
        margin = 10
        source_face_img = source[
            max(0, sy-margin):min(source.shape[0], sy+sh+margin),
            max(0, sx-margin):min(source.shape[1], sx+sw+margin)
        ]

        # Resize to target face size
        source_face_resized = cv2.resize(source_face_img, (tw, th))

        # Create mask for seamless cloning
        mask = 255 * np.ones(source_face_resized.shape, source_face_resized.dtype)

        # Center point for cloning
        center = (tx + tw // 2, ty + th // 2)

        # Seamless clone for blending
        try:
            output = cv2.seamlessClone(
                source_face_resized, target, mask, center, cv2.NORMAL_CLONE
            )
        except Exception as e:
            print(f"[-] Seamless cloning failed: {e}")
            # Fallback to simple overlay
            output = target.copy()
            output[ty:ty+th, tx:tx+tw] = source_face_resized

        cv2.imwrite(output_path, output)
        print(f"[+] Deepfake generated: {output_path}")

        return output_path

    def face_morph(self, img1_path, img2_path, output_path, alpha=0.5):
        """
        Morph between two faces

        Args:
            img1_path: First face image
            img2_path: Second face image
            output_path: Output path
            alpha: Morph ratio (0.0 = img1, 1.0 = img2)

        Returns:
            str: Path to morphed image
        """
        if not os.path.exists(img1_path) or not os.path.exists(img2_path):
            print("[-] Input images not found")
            return None

        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)

        if img1 is None or img2 is None:
            print("[-] Failed to read images")
            return None

        # Resize to same dimensions
        h, w = min(img1.shape[0], img2.shape[0]), min(img1.shape[1], img2.shape[1])
        img1 = cv2.resize(img1, (w, h))
        img2 = cv2.resize(img2, (w, h))

        # Simple alpha blending
        morphed = cv2.addWeighted(img1, 1-alpha, img2, alpha, 0)

        cv2.imwrite(output_path, morphed)
        print(f"[+] Face morph generated: {output_path}")

        return output_path

    def face_averaging(self, image_paths, output_path):
        """
        Create average face from multiple images

        Args:
            image_paths: List of face image paths
            output_path: Output path

        Returns:
            str: Path to average face
        """
        images = []
        valid_paths = []

        for path in image_paths:
            if os.path.exists(path):
                img = cv2.imread(path)
                if img is not None:
                    images.append(img)
                    valid_paths.append(path)

        if len(images) < 2:
            print("[-] Need at least 2 valid images for averaging")
            return None

        # Resize all to same size (use first image dimensions)
        h, w = images[0].shape[:2]
        resized = [cv2.resize(img, (w, h)) for img in images]

        # Calculate average
        average = np.mean(resized, axis=0).astype(np.uint8)

        cv2.imwrite(output_path, average)
        print(f"[+] Average face generated from {len(images)} images: {output_path}")

        return output_path

    def expression_transfer(self, neutral_face_path, expression_face_path, output_path):
        """
        Transfer expression from one face to another (simplified)

        Args:
            neutral_face_path: Neutral expression face
            expression_face_path: Face with target expression
            output_path: Output path

        Returns:
            str: Path to result
        """
        if not os.path.exists(neutral_face_path) or not os.path.exists(expression_face_path):
            print("[-] Input images not found")
            return None

        neutral = cv2.imread(neutral_face_path)
        expression = cv2.imread(expression_face_path)

        if neutral is None or expression is None:
            print("[-] Failed to read images")
            return None

        # Resize to same size
        h, w = neutral.shape[:2]
        expression = cv2.resize(expression, (w, h))

        # Convert to LAB color space
        neutral_lab = cv2.cvtColor(neutral, cv2.COLOR_BGR2LAB)
        expression_lab = cv2.cvtColor(expression, cv2.COLOR_BGR2LAB)

        # Transfer texture (high frequency) from expression
        # Keep color (low frequency) from neutral
        neutral_blur = cv2.GaussianBlur(neutral_lab, (21, 21), 0)
        expression_blur = cv2.GaussianBlur(expression_lab, (21, 21), 0)

        expression_detail = expression_lab.astype(np.float32) - expression_blur.astype(np.float32)
        result_lab = neutral_blur.astype(np.float32) + expression_detail * 0.7

        result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
        result = cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)

        cv2.imwrite(output_path, result)
        print(f"[+] Expression transfer result: {output_path}")

        return output_path

    def create_video_deepfake(self, source_face_path, target_video_path, output_video_path, max_frames=None):
        """
        Create deepfake video by swapping face in video frames

        Args:
            source_face_path: Source face to insert
            target_video_path: Target video
            output_video_path: Output video path
            max_frames: Maximum frames to process (None for all)

        Returns:
            str: Path to output video
        """
        if not os.path.exists(source_face_path):
            print(f"[-] Source face not found: {source_face_path}")
            return None

        if target_video_path == 'webcam':
            cap = cv2.VideoCapture(0)
        else:
            if not os.path.exists(target_video_path):
                print(f"[-] Target video not found: {target_video_path}")
                return None
            cap = cv2.VideoCapture(target_video_path)

        if not cap.isOpened():
            print("[-] Failed to open video")
            return None

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        # Read source face
        source_img = cv2.imread(source_face_path)
        source_face, _ = self.detect_face_and_landmarks(source_img)

        if source_face is None:
            print("[-] No face detected in source image")
            cap.release()
            return None

        sx, sy, sw, sh = source_face
        source_face_img = source_img[sy:sy+sh, sx:sx+sw]

        frame_count = 0
        print("[*] Processing video frames...")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if max_frames and frame_count >= max_frames:
                break

            # Detect face in frame
            target_face, _ = self.detect_face_and_landmarks(frame)

            if target_face is not None:
                tx, ty, tw, th = target_face

                # Resize source face
                source_resized = cv2.resize(source_face_img, (tw, th))

                # Create mask
                mask = 255 * np.ones(source_resized.shape, source_resized.dtype)
                center = (tx + tw // 2, ty + th // 2)

                # Seamless clone
                try:
                    frame = cv2.seamlessClone(
                        source_resized, frame, mask, center, cv2.NORMAL_CLONE
                    )
                except:
                    # Fallback
                    frame[ty:ty+th, tx:tx+tw] = source_resized

            out.write(frame)
            frame_count += 1

            if frame_count % 30 == 0:
                print(f"    Processed {frame_count} frames...")

        cap.release()
        out.release()

        print(f"[+] Deepfake video created: {output_video_path} ({frame_count} frames)")
        return output_video_path
