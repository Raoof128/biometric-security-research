"""
Face recognition and authentication system using DeepFace.
Optimized for 8GB RAM systems with lightweight models.
"""

import cv2
import numpy as np
from deepface import DeepFace
import pickle
import os
import warnings
warnings.filterwarnings('ignore')


class FaceAuthenticator:
    """
    Lightweight face authentication system using DeepFace.
    Uses Facenet model for optimal memory efficiency.
    """

    def __init__(self, model_name='Facenet', detector='opencv'):
        """
        Initialize face authenticator with lightweight models

        Args:
            model_name: 'Facenet' (lightweight), 'VGG-Face', 'OpenFace'
            detector: 'opencv' (fastest), 'ssd', 'mtcnn'
        """
        self.model_name = model_name
        self.detector = detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.enrolled_users = {}
        self.threshold = 0.6  # Similarity threshold
        print(f"[+] FaceAuthenticator initialized with {model_name} model")

    def detect_face(self, image):
        """Detect faces in image using Haar Cascade (fastest)"""
        if isinstance(image, str):
            image = cv2.imread(image)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        return faces

    def extract_face_embedding(self, image_path, enforce_detection=False):
        """Extract face embedding using lightweight model"""
        try:
            embedding = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                detector_backend=self.detector,
                enforce_detection=enforce_detection
            )

            # DeepFace returns a list of embeddings, get the first one
            if isinstance(embedding, list) and len(embedding) > 0:
                return np.array(embedding[0]['embedding'])
            elif isinstance(embedding, dict):
                return np.array(embedding['embedding'])
            else:
                return np.array(embedding)

        except Exception as e:
            print(f"[-] Error extracting embedding: {e}")
            return None

    def enroll_user(self, user_id, image_paths):
        """
        Enroll new user with multiple reference images

        Args:
            user_id: Unique identifier for user
            image_paths: List of image paths for enrollment

        Returns:
            bool: True if enrollment successful
        """
        if isinstance(image_paths, str):
            image_paths = [image_paths]

        embeddings = []

        print(f"[*] Enrolling user {user_id}...")
        for img_path in image_paths:
            if not os.path.exists(img_path):
                print(f"[-] Image not found: {img_path}")
                continue

            embedding = self.extract_face_embedding(img_path)
            if embedding is not None:
                embeddings.append(embedding)
                print(f"    [+] Processed: {os.path.basename(img_path)}")

        if embeddings:
            # Store average embedding for user
            self.enrolled_users[user_id] = {
                'embeddings': embeddings,
                'average': np.mean(embeddings, axis=0)
            }
            print(f"[+] User {user_id} enrolled with {len(embeddings)} samples")
            return True

        print(f"[-] Failed to enroll user {user_id} - no valid embeddings")
        return False

    def authenticate(self, image_path):
        """
        Authenticate user by comparing face embedding

        Args:
            image_path: Path to image for authentication

        Returns:
            tuple: (user_id, similarity_score) or (None, score) if not authenticated
        """
        if not os.path.exists(image_path):
            print(f"[-] Image not found: {image_path}")
            return None, 0.0

        query_embedding = self.extract_face_embedding(image_path)

        if query_embedding is None:
            return None, 0.0

        if not self.enrolled_users:
            print("[-] No enrolled users in database")
            return None, 0.0

        best_match = None
        best_score = float('inf')

        for user_id, data in self.enrolled_users.items():
            # Calculate distance to average embedding
            distance = np.linalg.norm(query_embedding - data['average'])

            if distance < best_score:
                best_score = distance
                best_match = user_id

        # Convert distance to similarity score (inverse relationship)
        similarity = 1 / (1 + best_score)

        if similarity >= self.threshold:
            return best_match, similarity
        return None, similarity

    def save_model(self, filepath):
        """Save enrolled users database"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self.enrolled_users, f)
        print(f"[+] Model saved to {filepath}")

    def load_model(self, filepath):
        """Load enrolled users database"""
        if not os.path.exists(filepath):
            print(f"[-] Model file not found: {filepath}")
            return False

        with open(filepath, 'rb') as f:
            self.enrolled_users = pickle.load(f)
        print(f"[+] Model loaded from {filepath} ({len(self.enrolled_users)} users)")
        return True


class RealtimeFaceAuth:
    """
    Real-time face authentication using webcam.
    """

    def __init__(self, authenticator):
        """
        Initialize real-time authentication

        Args:
            authenticator: FaceAuthenticator instance
        """
        self.auth = authenticator
        self.cap = None
        self.temp_face_path = '/tmp/temp_face.jpg'

    def run(self):
        """Run real-time face authentication"""
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("[-] Error: Could not open webcam")
            return

        print("[*] Starting real-time authentication. Press 'q' to quit.")
        print("[*] Press 's' to save current frame for enrollment")

        frame_count = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[-] Error reading frame")
                break

            # Detect faces every 5 frames to reduce CPU usage
            frame_count += 1
            if frame_count % 5 == 0:
                faces = self.auth.detect_face(frame)

                for (x, y, w, h) in faces:
                    # Draw rectangle
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                    # Save temporary face crop
                    face_crop = frame[y:y+h, x:x+w]
                    cv2.imwrite(self.temp_face_path, face_crop)

                    # Authenticate
                    user_id, score = self.auth.authenticate(self.temp_face_path)

                    # Display result
                    if user_id:
                        text = f"{user_id}: {score:.2f}"
                        color = (0, 255, 0)
                        status = "AUTHENTICATED"
                    else:
                        text = f"Unknown: {score:.2f}"
                        color = (0, 0, 255)
                        status = "REJECTED"

                    cv2.putText(frame, text, (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    cv2.putText(frame, status, (x, y+h+20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # Display instructions
            cv2.putText(frame, "Press 'q' to quit, 's' to save frame", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow('Face Authentication', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = cv2.getTickCount()
                save_path = f'captured_frame_{timestamp}.jpg'
                cv2.imwrite(save_path, frame)
                print(f"[+] Frame saved: {save_path}")

        self.cap.release()
        cv2.destroyAllWindows()

        # Cleanup
        if os.path.exists(self.temp_face_path):
            os.remove(self.temp_face_path)
