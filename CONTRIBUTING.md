# Contributing to Biometric Security Research System

First off, thank you for considering contributing to the Biometric Security Research System! It's people like you that make this a great tool for security research and education.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the problem
- **Expected behavior** vs **actual behavior**
- **System information** (OS, Python version, etc.)
- **Error messages** and stack traces
- **Screenshots** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - why is this enhancement useful?
- **Proposed solution** - how should it work?
- **Alternatives considered**
- **Additional context** - mockups, examples, etc.

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if you've added functionality
4. **Update documentation** as needed
5. **Ensure tests pass** - run `pytest`
6. **Submit a pull request**

## Development Setup

### 1. Clone and Setup

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/biometric-security-research.git
cd biometric-security-research

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 2. Install Pre-commit Hooks (Optional but Recommended)

```bash
pip install pre-commit
pre-commit install
```

### 3. Verify Setup

```bash
# Run tests
pytest

# Check code style
black --check .
pylint biometric attacks defenses

# Type checking
mypy .
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Formatting**: Use `black` for automatic formatting
- **Imports**: Use `isort` for import sorting
- **Type hints**: Required for all public functions
- **Docstrings**: Google style docstrings

### Code Formatting

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
pylint biometric attacks defenses evaluation reporting utils
```

### Type Hints

All public functions must include type hints:

```python
from typing import List, Optional, Tuple

def process_image(image_path: str, threshold: float = 0.5) -> Tuple[bool, float]:
    """
    Process image and return results.

    Args:
        image_path: Path to image file
        threshold: Detection threshold (default: 0.5)

    Returns:
        Tuple of (success, confidence_score)
    """
    pass
```

### Documentation

- **Docstrings**: All modules, classes, and functions must have docstrings
- **Comments**: Use comments for complex logic
- **README**: Update README.md for user-facing changes
- **Changelog**: Add entry to CHANGELOG.md

### Testing

- **Unit tests**: Required for new functionality
- **Test coverage**: Aim for >80% coverage
- **Test naming**: `test_<functionality>_<scenario>`
- **Fixtures**: Use pytest fixtures for reusable test data

```python
def test_validate_file_path_valid_file(sample_image):
    """Test file validation with valid file"""
    validator = InputValidator()
    is_valid, error = validator.validate_file_path(sample_image)

    assert is_valid is True
    assert error is None
```

## Project Structure

```
biometric-security-research/
├── biometric/          # Biometric authentication modules
├── attacks/            # Attack simulation modules
├── defenses/           # Anti-spoofing defenses
├── evaluation/         # Vulnerability testing
├── reporting/          # Report generation
├── utils/              # Utility modules
├── tests/              # Test suite
├── docs/               # Documentation
└── examples/           # Example scripts
```

## Submitting Changes

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`
- Refactoring: `refactor/description`

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(attacks): add adversarial patch attack method

fix(security): resolve path traversal vulnerability

docs(readme): update installation instructions

test(config): add configuration validation tests
```

### Pull Request Process

1. **Update documentation** - README, docstrings, CHANGELOG
2. **Add tests** - Ensure >80% coverage for new code
3. **Run full test suite** - `pytest` must pass
4. **Update CHANGELOG.md** - Add entry under "Unreleased"
5. **Link related issues** - Reference issues in PR description
6. **Wait for review** - Address feedback from maintainers

### Pull Request Template

PRs should include:

- **Description**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Testing**: How was this tested?
- **Screenshots**: If UI changes
- **Checklist**: Tests pass, docs updated, etc.

## Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- Additional biometric modalities (iris, voice, gait)
- More attack methods and defense techniques
- Performance optimizations
- Better visualization and reporting
- Mobile/edge device support

### Medium Priority
- Additional test coverage
- Documentation improvements
- Example scripts and tutorials
- Internationalization (i18n)
- Better error messages

### Good First Issues
- Documentation typos and clarifications
- Adding type hints to existing code
- Writing additional unit tests
- Improving code comments
- Creating example scripts

Look for issues labeled `good first issue` or `help wanted`.

## Security Vulnerability Reporting

**DO NOT** open a public issue for security vulnerabilities.

Instead, please email security concerns to the maintainers or use GitHub's private vulnerability reporting feature.

See [SECURITY.md](SECURITY.md) for details.

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Acknowledged in project documentation

## Questions?

- **Issues**: Open a GitHub issue for bugs or features
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check docs/ directory

## License

By contributing, you agree that your contributions will be licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Thank you for contributing to the Biometric Security Research System! 🎉
