"""Tests for security utilities"""

import pytest
import os
import time
from pathlib import Path
from utils.security import (
    InputValidator,
    RateLimiter,
    SecureDataHandler,
    get_validator,
    get_rate_limiter
)


class TestInputValidator:
    """Test input validation"""

    def test_valid_file_path(self, sample_image):
        """Test validation of valid file path"""
        validator = InputValidator()

        is_valid, error = validator.validate_file_path(sample_image)

        assert is_valid is True
        assert error is None

    def test_nonexistent_file(self, temp_dir):
        """Test validation of non-existent file"""
        validator = InputValidator()
        fake_path = os.path.join(temp_dir, 'nonexistent.jpg')

        is_valid, error = validator.validate_file_path(fake_path)

        assert is_valid is False
        assert 'does not exist' in error.lower()

    def test_invalid_extension(self, temp_dir):
        """Test validation of invalid file extension"""
        validator = InputValidator()

        # Create file with invalid extension
        invalid_file = os.path.join(temp_dir, 'test.txt')
        Path(invalid_file).touch()

        is_valid, error = validator.validate_file_path(invalid_file)

        assert is_valid is False
        assert 'extension not allowed' in error.lower()

    def test_file_too_large(self, temp_dir, monkeypatch):
        """Test validation of oversized file"""
        from config import SystemConfig

        validator = InputValidator()

        # Set low file size limit
        config = SystemConfig()
        config.security.max_file_size_mb = 0.001  # 1KB
        validator.config = config.security

        # Create file larger than limit
        large_file = os.path.join(temp_dir, 'large.jpg')
        with open(large_file, 'wb') as f:
            f.write(b'x' * 2048)  # 2KB

        is_valid, error = validator.validate_file_path(large_file)

        assert is_valid is False
        assert 'too large' in error.lower()

    def test_valid_user_id(self):
        """Test validation of valid user ID"""
        validator = InputValidator()

        valid_ids = ['alice', 'user123', 'test-user', 'user_name']

        for user_id in valid_ids:
            is_valid, error = validator.validate_user_id(user_id)
            assert is_valid is True, f"Failed for {user_id}"
            assert error is None

    def test_invalid_user_id(self):
        """Test validation of invalid user ID"""
        validator = InputValidator()

        invalid_ids = [
            '',  # Empty
            'a' * 100,  # Too long
            'user@name',  # Invalid character
            'admin',  # Reserved
            'root',  # Reserved
        ]

        for user_id in invalid_ids:
            is_valid, error = validator.validate_user_id(user_id)
            assert is_valid is False, f"Should fail for {user_id}"
            assert error is not None

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        validator = InputValidator()

        dangerous_names = [
            '../../../etc/passwd',
            'file\x00name.jpg',
            'file\nname.jpg',
            '/absolute/path/file.jpg'
        ]

        for dangerous_name in dangerous_names:
            sanitized = validator.sanitize_filename(dangerous_name)

            # Should not contain dangerous characters
            assert '../' not in sanitized
            assert '\x00' not in sanitized
            assert '\n' not in sanitized
            assert not os.path.isabs(sanitized)

    def test_singleton_validator(self):
        """Test validator singleton"""
        validator1 = get_validator()
        validator2 = get_validator()

        assert validator1 is validator2


class TestRateLimiter:
    """Test rate limiting"""

    def test_allows_under_limit(self):
        """Test that requests under limit are allowed"""
        limiter = RateLimiter(max_attempts=3, window_seconds=1)

        for i in range(3):
            allowed, retry_after = limiter.is_allowed('user1')
            assert allowed is True
            assert retry_after is None

    def test_blocks_over_limit(self):
        """Test that requests over limit are blocked"""
        limiter = RateLimiter(max_attempts=3, window_seconds=10)

        # Make 3 requests (allowed)
        for i in range(3):
            limiter.is_allowed('user1')

        # 4th request should be blocked
        allowed, retry_after = limiter.is_allowed('user1')

        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0

    def test_resets_after_window(self):
        """Test that limit resets after time window"""
        limiter = RateLimiter(max_attempts=2, window_seconds=1)

        # Make 2 requests
        limiter.is_allowed('user1')
        limiter.is_allowed('user1')

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        allowed, retry_after = limiter.is_allowed('user1')
        assert allowed is True

    def test_per_user_limits(self):
        """Test that limits are per-user"""
        limiter = RateLimiter(max_attempts=2, window_seconds=10)

        # User1 makes 2 requests
        limiter.is_allowed('user1')
        limiter.is_allowed('user1')

        # User2 should still be allowed
        allowed, retry_after = limiter.is_allowed('user2')
        assert allowed is True

    def test_reset(self):
        """Test manual rate limit reset"""
        limiter = RateLimiter(max_attempts=2, window_seconds=10)

        # Make 2 requests
        limiter.is_allowed('user1')
        limiter.is_allowed('user1')

        # Reset
        limiter.reset('user1')

        # Should be allowed again
        allowed, retry_after = limiter.is_allowed('user1')
        assert allowed is True


class TestSecureDataHandler:
    """Test secure data handling"""

    def test_generate_key(self):
        """Test cryptographic key generation"""
        handler = SecureDataHandler()

        key1 = handler.generate_key(32)
        key2 = handler.generate_key(32)

        assert len(key1) == 32
        assert len(key2) == 32
        assert key1 != key2  # Should be random

    def test_hash_data(self):
        """Test data hashing"""
        handler = SecureDataHandler()

        data = "test password"
        hash_hex, salt_hex = handler.hash_data(data)

        assert len(hash_hex) > 0
        assert len(salt_hex) > 0

    def test_verify_hash(self):
        """Test hash verification"""
        handler = SecureDataHandler()

        data = "test password"
        hash_hex, salt_hex = handler.hash_data(data)

        # Correct data should verify
        assert handler.verify_hash(data, hash_hex, salt_hex) is True

        # Wrong data should not verify
        assert handler.verify_hash("wrong password", hash_hex, salt_hex) is False

    def test_constant_time_compare(self):
        """Test constant-time comparison"""
        handler = SecureDataHandler()

        # Equal strings
        assert handler.constant_time_compare("abc", "abc") is True

        # Different strings
        assert handler.constant_time_compare("abc", "def") is False

        # Bytes
        assert handler.constant_time_compare(b"abc", b"abc") is True

    def test_secure_delete(self, temp_dir):
        """Test secure file deletion"""
        handler = SecureDataHandler()

        # Create test file
        test_file = os.path.join(temp_dir, 'secret.txt')
        with open(test_file, 'w') as f:
            f.write('sensitive data')

        assert os.path.exists(test_file)

        # Securely delete
        handler.secure_delete(test_file)

        assert not os.path.exists(test_file)

    def test_secure_delete_nonexistent(self, temp_dir):
        """Test secure delete of non-existent file"""
        handler = SecureDataHandler()

        fake_file = os.path.join(temp_dir, 'nonexistent.txt')

        # Should not raise exception
        handler.secure_delete(fake_file)
