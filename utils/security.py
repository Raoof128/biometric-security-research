"""
Security utilities for input validation, encryption, and secure operations.
Implements defense-in-depth security measures.
"""

import os
import hashlib
import hmac
import secrets
import time
from pathlib import Path
from typing import Optional, Tuple, Union
from collections import defaultdict
from datetime import datetime, timedelta
import base64

from utils.logger import get_logger

logger = get_logger(__name__)


class InputValidator:
    """
    Input validation for security-critical operations
    """

    def __init__(self, config=None):
        """
        Initialize input validator

        Args:
            config: SecurityConfig instance
        """
        if config is None:
            from config import get_config
            config = get_config().security

        self.config = config

    def validate_file_path(self, filepath: Union[str, Path]) -> Tuple[bool, Optional[str]]:
        """
        Validate file path for security issues

        Args:
            filepath: Path to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            filepath = Path(filepath).resolve()

            # Check if file exists
            if not filepath.exists():
                return False, f"File does not exist: {filepath}"

            # Check if it's a file (not directory)
            if not filepath.is_file():
                return False, f"Path is not a file: {filepath}"

            # Check file extension
            if filepath.suffix.lower() not in self.config.allowed_extensions:
                return False, f"File extension not allowed: {filepath.suffix}. Allowed: {self.config.allowed_extensions}"

            # Check file size
            file_size_mb = filepath.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.max_file_size_mb:
                return False, f"File too large: {file_size_mb:.2f}MB (max: {self.config.max_file_size_mb}MB)"

            # Check for path traversal attempts
            try:
                filepath.relative_to(Path.cwd())
            except ValueError:
                # File is outside project directory - check if it's in /tmp or user-allowed paths
                allowed_dirs = ['/tmp', str(Path.home())]
                if not any(str(filepath).startswith(allowed_dir) for allowed_dir in allowed_dirs):
                    logger.warning(f"File path outside project directory: {filepath}")

            return True, None

        except Exception as e:
            logger.error(f"Error validating file path: {e}")
            return False, f"Invalid file path: {str(e)}"

    def validate_user_id(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user ID for security

        Args:
            user_id: User identifier to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        # Check length
        if not user_id or len(user_id) == 0:
            return False, "User ID cannot be empty"

        if len(user_id) > 64:
            return False, "User ID too long (max 64 characters)"

        # Check for valid characters (alphanumeric, underscore, hyphen)
        if not all(c.isalnum() or c in ('_', '-') for c in user_id):
            return False, "User ID contains invalid characters (only alphanumeric, _, - allowed)"

        # Prevent reserved names
        reserved_names = ['admin', 'root', 'system', 'anonymous', 'guest', 'test']
        if user_id.lower() in reserved_names:
            return False, f"User ID '{user_id}' is reserved"

        return True, None

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent security issues

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        # Remove path components
        filename = os.path.basename(filename)

        # Replace dangerous characters
        dangerous_chars = ['/', '\\', '..', '\x00', '\n', '\r', '\t']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Limit length
        max_length = 255
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext

        return filename


class RateLimiter:
    """
    Rate limiting to prevent abuse and DoS attacks
    """

    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        """
        Initialize rate limiter

        Args:
            max_attempts: Maximum attempts allowed in window
            window_seconds: Time window in seconds
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = defaultdict(list)

    def is_allowed(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """
        Check if action is allowed for identifier

        Args:
            identifier: Unique identifier (e.g., user_id, IP)

        Returns:
            tuple: (is_allowed, retry_after_seconds)
        """
        now = time.time()
        cutoff = now - self.window_seconds

        # Remove old attempts
        self.attempts[identifier] = [
            timestamp for timestamp in self.attempts[identifier]
            if timestamp > cutoff
        ]

        # Check if limit exceeded
        if len(self.attempts[identifier]) >= self.max_attempts:
            oldest_attempt = min(self.attempts[identifier])
            retry_after = int(oldest_attempt + self.window_seconds - now)
            logger.warning(f"Rate limit exceeded for {identifier}. Retry after {retry_after}s")
            return False, retry_after

        # Record this attempt
        self.attempts[identifier].append(now)
        return True, None

    def reset(self, identifier: str):
        """Reset rate limit for identifier"""
        if identifier in self.attempts:
            del self.attempts[identifier]


class SecureDataHandler:
    """
    Secure data handling with encryption and secure deletion
    """

    def __init__(self, config=None):
        """
        Initialize secure data handler

        Args:
            config: SecurityConfig instance
        """
        if config is None:
            from config import get_config
            config = get_config().security

        self.config = config

    def generate_key(self, length: int = 32) -> bytes:
        """
        Generate cryptographically secure random key

        Args:
            length: Key length in bytes (default 32 for AES-256)

        Returns:
            bytes: Random key
        """
        return secrets.token_bytes(length)

    def hash_data(self, data: Union[str, bytes], salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        Hash data using SHA-256 with salt

        Args:
            data: Data to hash
            salt: Optional salt (generates new if None)

        Returns:
            tuple: (hash_hex, salt_hex)
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        if salt is None:
            salt = secrets.token_bytes(32)

        hash_obj = hashlib.pbkdf2_hmac('sha256', data, salt, 100000)
        return hash_obj.hex(), salt.hex()

    def verify_hash(self, data: Union[str, bytes], hash_hex: str, salt_hex: str) -> bool:
        """
        Verify hashed data

        Args:
            data: Data to verify
            hash_hex: Expected hash (hex)
            salt_hex: Salt (hex)

        Returns:
            bool: True if hash matches
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        salt = bytes.fromhex(salt_hex)
        computed_hash = hashlib.pbkdf2_hmac('sha256', data, salt, 100000)

        return hmac.compare_digest(computed_hash.hex(), hash_hex)

    def secure_delete(self, filepath: Union[str, Path], passes: int = 3):
        """
        Securely delete file by overwriting before deletion

        Args:
            filepath: Path to file
            passes: Number of overwrite passes
        """
        if not self.config.secure_delete:
            # Just delete normally if secure delete disabled
            Path(filepath).unlink(missing_ok=True)
            return

        filepath = Path(filepath)

        if not filepath.exists():
            return

        try:
            file_size = filepath.stat().st_size

            with open(filepath, 'ba+') as f:
                for i in range(passes):
                    f.seek(0)
                    # Overwrite with random data
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())

            # Finally delete the file
            filepath.unlink()
            logger.info(f"Securely deleted file: {filepath}")

        except Exception as e:
            logger.error(f"Error securely deleting file {filepath}: {e}")
            # Fall back to normal deletion
            filepath.unlink(missing_ok=True)

    def constant_time_compare(self, a: Union[str, bytes], b: Union[str, bytes]) -> bool:
        """
        Constant-time comparison to prevent timing attacks

        Args:
            a: First value
            b: Second value

        Returns:
            bool: True if equal
        """
        if isinstance(a, str):
            a = a.encode('utf-8')
        if isinstance(b, str):
            b = b.encode('utf-8')

        return hmac.compare_digest(a, b)


class AuditLogger:
    """
    Audit logging for compliance and security monitoring
    """

    def __init__(self, log_file: str = 'logs/audit.log'):
        """
        Initialize audit logger

        Args:
            log_file: Path to audit log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger('audit')

    def log_authentication_attempt(
        self,
        user_id: str,
        success: bool,
        method: str,
        details: Optional[dict] = None
    ):
        """
        Log authentication attempt

        Args:
            user_id: User identifier
            success: Whether authentication succeeded
            method: Authentication method (face, fingerprint)
            details: Additional details
        """
        timestamp = datetime.now().isoformat()
        result = "SUCCESS" if success else "FAILURE"

        log_entry = {
            'timestamp': timestamp,
            'event_type': 'authentication',
            'user_id': user_id,
            'result': result,
            'method': method,
            'details': details or {}
        }

        self.logger.audit_log(
            action='authenticate',
            user=user_id,
            resource=method,
            result=result
        )

        self._write_audit_entry(log_entry)

    def log_enrollment(self, user_id: str, success: bool, method: str):
        """
        Log user enrollment

        Args:
            user_id: User identifier
            success: Whether enrollment succeeded
            method: Enrollment method
        """
        timestamp = datetime.now().isoformat()
        result = "SUCCESS" if success else "FAILURE"

        log_entry = {
            'timestamp': timestamp,
            'event_type': 'enrollment',
            'user_id': user_id,
            'result': result,
            'method': method
        }

        self.logger.audit_log(
            action='enroll',
            user=user_id,
            resource=method,
            result=result
        )

        self._write_audit_entry(log_entry)

    def log_attack_detection(self, attack_type: str, detected: bool, details: dict):
        """
        Log attack detection event

        Args:
            attack_type: Type of attack
            detected: Whether attack was detected
            details: Attack details
        """
        timestamp = datetime.now().isoformat()
        result = "DETECTED" if detected else "MISSED"

        log_entry = {
            'timestamp': timestamp,
            'event_type': 'attack_detection',
            'attack_type': attack_type,
            'result': result,
            'details': details
        }

        self.logger.security_event('attack_detection', details)

        self._write_audit_entry(log_entry)

    def _write_audit_entry(self, entry: dict):
        """Write audit entry to file"""
        try:
            with open(self.log_file, 'a') as f:
                import json
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing audit entry: {e}")


# Global instances
_validator = None
_rate_limiter = None
_secure_handler = None
_audit_logger = None


def get_validator() -> InputValidator:
    """Get global input validator instance"""
    global _validator
    if _validator is None:
        _validator = InputValidator()
    return _validator


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        from config import get_config
        config = get_config().security
        _rate_limiter = RateLimiter(
            max_attempts=config.rate_limit_attempts,
            window_seconds=config.rate_limit_window_seconds
        )
    return _rate_limiter


def get_secure_handler() -> SecureDataHandler:
    """Get global secure data handler instance"""
    global _secure_handler
    if _secure_handler is None:
        _secure_handler = SecureDataHandler()
    return _secure_handler


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
