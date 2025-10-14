"""
Biometric authentication module for face and fingerprint recognition.
"""

from .face_recognition import FaceAuthenticator, RealtimeFaceAuth
from .fingerprint_matcher import FingerprintMatcher

__all__ = ['FaceAuthenticator', 'RealtimeFaceAuth', 'FingerprintMatcher']
