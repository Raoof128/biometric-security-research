# Examples

This directory contains example scripts demonstrating how to use the Biometric Security Research System.

## Available Examples

### 1. Basic Usage
- `01_simple_enrollment.py` - Enroll users with face and fingerprint
- `02_authentication.py` - Authenticate enrolled users
- `03_generate_attacks.py` - Generate presentation attacks

### 2. Advanced Features
- `04_advanced_attacks.py` - Generate adversarial attacks
- `05_liveness_detection.py` - Test anti-spoofing defenses
- `06_vulnerability_testing.py` - Run comprehensive vulnerability tests
- `07_generate_reports.py` - Create interactive security reports

### 3. Configuration and Security
- `08_custom_configuration.py` - Use custom configurations
- `09_security_features.py` - Demonstrate security features
- `10_performance_monitoring.py` - Monitor system performance

## Quick Start

```bash
# Run an example
python examples/01_simple_enrollment.py

# With custom data
python examples/02_authentication.py --image path/to/image.jpg
```

## Requirements

Make sure you have installed all dependencies:

```bash
pip install -r requirements.txt
```

## Data

Examples assume you have sample data in the `data/` directory. You can generate test data with:

```bash
python generate_test_data.py
```

## Notes

- These examples are for educational and testing purposes
- Modify paths and parameters according to your setup
- Always use virtual environments for Python projects
- Review SECURITY.md before processing real biometric data
