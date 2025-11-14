"""
Setup script for Biometric Security Research System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [
            line.strip() for line in f
            if line.strip() and not line.startswith('#') and not line.startswith('dlib')
        ]

setup(
    name="biometric-security-research",
    version="2.0.0",
    author="Security Researcher",
    description="Comprehensive biometric authentication security research system with advanced attack methods and defenses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/biometric-security-research",
    packages=find_packages(exclude=["tests", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.12.0',
            'pylint>=3.0.0',
            'mypy>=1.7.0',
        ],
        'dlib': [
            'dlib>=19.24.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'biometric-security=main:main',
            'biometric-security-v2=cli_enhanced:main',
        ],
    },
    include_package_data=True,
    package_data={
        'biometric': ['models/*'],
        'reporting': ['templates/*'],
    },
    keywords='biometric security face-recognition fingerprint liveness-detection anti-spoofing adversarial-attacks',
    project_urls={
        'Documentation': 'https://github.com/yourusername/biometric-security-research/docs',
        'Source': 'https://github.com/yourusername/biometric-security-research',
        'Bug Reports': 'https://github.com/yourusername/biometric-security-research/issues',
    },
)
