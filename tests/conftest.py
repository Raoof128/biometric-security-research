"""
Pytest configuration and fixtures for testing
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import numpy as np
import cv2


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_image(temp_dir):
    """Create a sample test image"""
    # Create a simple 200x200 color image
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)

    # Add a simple "face-like" pattern
    cv2.rectangle(img, (50, 50), (150, 150), (255, 200, 180), -1)  # Face
    cv2.circle(img, (80, 80), 10, (0, 0, 0), -1)  # Eye
    cv2.circle(img, (120, 80), 10, (0, 0, 0), -1)  # Eye
    cv2.ellipse(img, (100, 120), (20, 10), 0, 0, 180, (200, 100, 100), -1)  # Mouth

    img_path = os.path.join(temp_dir, 'sample.jpg')
    cv2.imwrite(img_path, img)

    return img_path


@pytest.fixture
def sample_images(temp_dir):
    """Create multiple sample images"""
    images = []

    for i in range(3):
        img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (150, 150), (255, 200, 180), -1)
        cv2.circle(img, (80, 80), 10, (0, 0, 0), -1)
        cv2.circle(img, (120, 80), 10, (0, 0, 0), -1)

        img_path = os.path.join(temp_dir, f'sample_{i}.jpg')
        cv2.imwrite(img_path, img)
        images.append(img_path)

    return images


@pytest.fixture
def config():
    """Get test configuration"""
    from config import SystemConfig

    # Create test config
    config = SystemConfig()
    config.environment = 'testing'
    config.logging.level = 'DEBUG'

    return config


@pytest.fixture
def mock_embedding():
    """Create mock face embedding"""
    return np.random.rand(128).astype(np.float32)


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, temp_dir):
    """Setup test environment for all tests"""
    # Set environment to testing
    monkeypatch.setenv('ENVIRONMENT', 'testing')

    # Use temp dir for data
    monkeypatch.setenv('DATA_DIR', temp_dir)

    # Disable GPU for tests
    monkeypatch.setenv('ENABLE_GPU', 'false')

    # Lower log level for tests
    monkeypatch.setenv('LOG_LEVEL', 'WARNING')
