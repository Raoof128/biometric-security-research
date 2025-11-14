# Frequently Asked Questions (FAQ)

Complete FAQ and troubleshooting guide for the Biometric Security Research System.

## Table of Contents

- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage & Features](#usage--features)
- [Performance](#performance)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [General Questions](#general-questions)

---

## Installation & Setup

### Q: What Python versions are supported?

**A:** Python 3.8, 3.9, 3.10, and 3.11 are officially supported and tested via CI/CD. Python 3.12+ may work but is not officially tested.

```bash
# Check your Python version
python --version
```

### Q: Installation fails with "No module named 'cv2'"

**A:** OpenCV installation failed. Try:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install OpenCV separately
pip install opencv-python opencv-contrib-python

# Then install other dependencies
pip install -r requirements.txt
```

### Q: I get "CMake must be installed" error when installing dlib

**A:** dlib requires CMake for compilation. Install it:

**Ubuntu/Debian:**
```bash
sudo apt-get install build-essential cmake
pip install dlib
```

**macOS:**
```bash
brew install cmake
pip install dlib
```

**Windows:**
- Download CMake from https://cmake.org/download/
- Add to PATH
- Or use pre-built wheels: `pip install dlib-binary`

### Q: Installation script (install.sh) fails on Windows

**A:** The install.sh script is designed for Unix-like systems (Linux/macOS). On Windows, use manual installation:

```powershell
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir data\enrolled_users data\test_samples data\attack_samples data\results
mkdir biometric\models logs
```

### Q: How do I install GPU support?

**A:** For GPU acceleration with TensorFlow/PyTorch:

```bash
# CUDA-enabled TensorFlow
pip install tensorflow-gpu

# CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU availability
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

**Note:** Requires NVIDIA GPU and CUDA toolkit installed.

---

## Configuration

### Q: Where do I configure system settings?

**A:** Three ways to configure:

1. **Environment variables** (.env file):
```bash
cp .env.example .env
nano .env
```

2. **Config object** (programmatically):
```python
from config import get_config
config = get_config()
config.biometric.model_name = "Facenet512"
```

3. **Command-line arguments**:
```bash
python main.py --model Facenet512 --threshold 0.6
```

### Q: What's the difference between models (VGG-Face, Facenet, ArcFace)?

**A:** Performance comparison:

| Model | Speed | Accuracy | Memory | Use Case |
|-------|-------|----------|--------|----------|
| VGG-Face | Slow | Good | High | High accuracy needed |
| Facenet | Fast | Excellent | Medium | **Recommended default** |
| Facenet512 | Medium | Excellent | Medium | Best accuracy |
| ArcFace | Medium | Excellent | Medium | Research/testing |
| OpenFace | Very Fast | Fair | Low | Edge devices |
| DeepID | Fast | Good | Low | Legacy systems |

**Recommendation:** Use `Facenet` for most applications.

### Q: How do I tune the authentication threshold?

**A:** Lower threshold = more false accepts, Higher threshold = more false rejects

```python
# Conservative (more secure, fewer false accepts)
config.biometric.threshold = 0.5

# Balanced (recommended)
config.biometric.threshold = 0.6

# Lenient (more false accepts)
config.biometric.threshold = 0.7
```

**Best practice:** Use evaluation tools to find optimal threshold:

```bash
python main.py evaluate --find-optimal-threshold
```

### Q: Can I use multiple modalities (face + fingerprint)?

**A:** Currently, face and fingerprint are implemented separately. Multi-modal fusion is planned for v3.0. Current workaround:

```python
# Score-level fusion
face_score = face_auth.authenticate(face_img)
finger_score = finger_auth.authenticate(finger_img)

# Simple average fusion
combined_score = (face_score + finger_score) / 2

# Weighted fusion (trust face more)
combined_score = 0.7 * face_score + 0.3 * finger_score
```

---

## Usage & Features

### Q: How many images do I need to enroll a user?

**A:** **Minimum:** 1-3 images, **Recommended:** 5-10 images for better accuracy

Best practices:
- Multiple angles (front, left, right)
- Different lighting conditions
- Different expressions (neutral, smiling)
- Different times of day

```bash
python cli_enhanced.py enroll \
  --user-id alice \
  --modality face \
  --image-dir data/alice_photos/
```

### Q: How do I test against presentation attacks?

**A:** Use the built-in attack generation:

```bash
# Generate various attacks
python main.py attack \
  --type photo \
  --input data/enrolled_users/alice/face_1.jpg \
  --output data/attack_samples/alice_photo_attack.jpg

# Test all attack types
python main.py evaluate \
  --attack-types photo video mask degraded
```

### Q: What's the difference between liveness detection methods?

**A:**

| Method | Speed | Accuracy | Requirements | Limitations |
|--------|-------|----------|--------------|-------------|
| Blink Detection | Fast | Medium | Webcam video | Can be fooled by video replay |
| Texture Analysis (LBP) | Very Fast | Good | Single image | Needs training data |
| Depth Analysis | Medium | Excellent | Depth camera | Requires special hardware |
| Active Flash | Fast | Good | Camera with flash | User experience issue |
| Challenge-Response | Slow | Excellent | User interaction | Poor UX |

**Recommendation:** Use multiple methods for robust liveness detection.

### Q: Can I use this in real-time with a webcam?

**A:** Yes! Real-time authentication example:

```python
from biometric.face_recognition import FaceAuthenticator
import cv2

auth = FaceAuthenticator()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    # Save frame and authenticate
    cv2.imwrite('temp.jpg', frame)
    result = auth.authenticate('temp.jpg')

    if result['authenticated']:
        print(f"Welcome {result['user_id']}!")
        break

    cv2.imshow('Authentication', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Q: How do I generate reports?

**A:** Multiple report formats available:

```bash
# Basic text report
python main.py evaluate --report-format text

# HTML interactive dashboard
python main.py evaluate --report-format html

# JSON for integration
python main.py evaluate --report-format json

# Enhanced report with Plotly
python main.py evaluate --enhanced-report
```

---

## Performance

### Q: Why is the first authentication so slow?

**A:** Model loading and initialization. Subsequent authentications are cached:

- **First authentication:** ~2-5 seconds (model loading)
- **Cached authentications:** ~100-500ms

**Solution:** Pre-load models at startup:

```python
from biometric.face_recognition import FaceAuthenticator

# Initialize once at startup
auth = FaceAuthenticator()
auth.load_model('data/enrolled_users/face_model.pkl')

# Now all authentications are fast
```

### Q: How can I speed up batch processing?

**A:** Use batch processing mode:

```python
from biometric.face_recognition import FaceAuthenticator

auth = FaceAuthenticator()

# Process multiple images at once
images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
results = auth.authenticate_batch(images)

# 3x faster than processing individually
```

### Q: System is using too much memory

**A:** Memory optimization strategies:

```python
from utils.performance import optimize_memory, PerformanceMonitor

# Monitor memory usage
monitor = PerformanceMonitor()
print(f"Memory: {monitor.get_memory_usage()}")

# Optimize memory
optimize_memory()

# Reduce cache size
from config import get_config
config = get_config()
config.performance.cache_size = 500  # Default: 1000
```

**Also check:**
```bash
# Limit model size
export BIOMETRIC_MODEL=OpenFace  # Smaller model

# Disable embedding cache
export CACHE_EMBEDDINGS=false
```

### Q: How do I enable GPU acceleration?

**A:**

1. **Check GPU availability:**
```python
import tensorflow as tf
print("GPUs:", tf.config.list_physical_devices('GPU'))
```

2. **Enable in config:**
```bash
# .env file
ENABLE_GPU=true
GPU_MEMORY_LIMIT=4096  # MB
```

3. **Set environment variables:**
```bash
export CUDA_VISIBLE_DEVICES=0
export TF_FORCE_GPU_ALLOW_GROWTH=true
```

**Expected speedup:** 2-5x faster face recognition with GPU.

---

## Security

### Q: Is it safe to use in production?

**A:** This system is designed for **research and testing**. For production:

**Required additions:**
- Encrypted database for biometric templates
- Secure key management (HSM or KMS)
- Network security (TLS/SSL)
- Audit logging integration with SIEM
- Regular security audits
- Compliance verification (GDPR, CCPA, etc.)

**See:** [SECURITY.md](../SECURITY.md) for detailed security considerations.

### Q: How are biometric templates stored?

**A:** Templates are stored as NumPy arrays (embeddings) in pickle files:

```
data/enrolled_users/
├── alice/
│   ├── face_embedding.pkl  # 128-512 dimensional vector
│   └── metadata.json       # User info, enrollment date
```

**Security considerations:**
- Templates are **not encrypted** by default
- Enable encryption: `config.security.encrypt_templates = True`
- Templates cannot reconstruct original face (one-way transformation)

### Q: Can someone steal and reuse biometric templates?

**A:** Template attacks are a real threat. Mitigations:

1. **Enable template encryption:**
```python
config.security.encrypt_templates = True
config.security.encryption_key = "your-secret-key-32-bytes-long!!"
```

2. **Use secure deletion:**
```python
from utils.security import SecureDataHandler
handler = SecureDataHandler()
handler.secure_delete('data/enrolled_users/old_user/')
```

3. **Enable rate limiting:**
```python
config.security.enable_rate_limit = True
config.security.max_auth_attempts = 5
config.security.rate_limit_window = 60  # seconds
```

### Q: How do I audit authentication attempts?

**A:** Audit logging is enabled by default:

```bash
# View audit log
tail -f logs/audit.log

# Search for specific user
grep "user_id: alice" logs/audit.log

# Check failed attempts
grep "authenticated: false" logs/audit.log
```

**Audit log format:**
```json
{
  "timestamp": "2024-11-14T10:30:45",
  "event_type": "authentication_attempt",
  "user_id": "alice",
  "authenticated": true,
  "confidence": 0.87,
  "source_ip": "192.168.1.100"
}
```

### Q: What about GDPR compliance?

**A:** GDPR considerations for biometric data:

**Required actions:**
1. **Obtain explicit consent** before collecting biometric data
2. **Implement data retention policies:**
```python
# Auto-delete after 90 days
config.security.data_retention_days = 90
```
3. **Enable right to erasure:**
```bash
python cli_enhanced.py delete-user --user-id alice --secure
```
4. **Data portability:**
```bash
python cli_enhanced.py export-user --user-id alice --format json
```
5. **Document processing activities** (ROPA)

**See:** [SECURITY.md](../SECURITY.md) for full compliance guidance.

---

## Troubleshooting

### Q: "No face detected in image" error

**A:** Common causes and solutions:

1. **Image too small:**
```python
# Minimum recommended: 640x480
img = cv2.imread('image.jpg')
print(f"Size: {img.shape}")  # Should be (height, width, 3)
```

2. **Face too small in frame:**
```python
# Try different detector backends
auth = FaceAuthenticator(detector='retinaface')  # More sensitive
# Options: opencv, ssd, dlib, mtcnn, retinaface
```

3. **Poor lighting:**
```python
# Enhance image first
import cv2
img = cv2.imread('dark_image.jpg')
img = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
cv2.imwrite('enhanced.jpg', img)
```

### Q: Authentication failing for valid users

**A:** Troubleshooting steps:

1. **Check threshold:**
```python
# Lower threshold if too strict
config.biometric.threshold = 0.65  # From 0.6
```

2. **Check image quality:**
```bash
python cli_enhanced.py verify-images --user-id alice
```

3. **Re-enroll with more images:**
```bash
python cli_enhanced.py enroll \
  --user-id alice \
  --image-dir new_photos/ \
  --update  # Add to existing enrollment
```

4. **Check for template corruption:**
```bash
python cli_enhanced.py validate-templates
```

### Q: "Rate limit exceeded" error

**A:** Too many authentication attempts:

```python
# Increase rate limit
config.security.max_auth_attempts = 10  # From 5

# Or disable temporarily for testing
config.security.enable_rate_limit = False
```

**Reset rate limits:**
```bash
python cli_enhanced.py reset-rate-limits --user-id alice
```

### Q: High memory usage / Out of memory

**A:** Solutions:

1. **Reduce cache size:**
```python
config.performance.cache_size = 100  # From 1000
```

2. **Use smaller model:**
```python
config.biometric.model_name = "OpenFace"  # Smallest
```

3. **Disable embedding cache:**
```python
config.performance.cache_embeddings = False
```

4. **Process in batches:**
```python
# Instead of loading all at once
for batch in image_batches:
    process_batch(batch)
    optimize_memory()  # Clear cache between batches
```

### Q: Docker container crashes with "Killed"

**A:** Out of memory (OOM killer). Solutions:

1. **Increase container memory:**
```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G  # From 4G
```

2. **Or reduce memory usage:**
```bash
# In container
export BIOMETRIC_MODEL=OpenFace
export CACHE_EMBEDDINGS=false
```

### Q: Tests failing on CI/CD

**A:** Common CI issues:

1. **Model download timeout:**
```yaml
# .github/workflows/ci.yml
- name: Download models
  run: |
    python -c "from deepface import DeepFace; DeepFace.build_model('Facenet')"
  timeout-minutes: 10
```

2. **Insufficient memory:**
```yaml
# Use smaller test datasets
- name: Test
  run: pytest tests/test_basic.py  # Not full suite
```

### Q: "ImportError: cannot import name 'DeepFace'" error

**A:** DeepFace installation issue:

```bash
# Reinstall DeepFace
pip uninstall deepface
pip install deepface

# Or specific version
pip install deepface==0.0.79
```

---

## Development

### Q: How do I contribute?

**A:** See [CONTRIBUTING.md](../CONTRIBUTING.md) for full guide. Quick start:

```bash
# Fork and clone
git clone https://github.com/yourusername/biometric-security-research.git
cd biometric-security-research

# Create branch
git checkout -b feature/my-feature

# Install dev dependencies
pip install -r requirements-dev.txt

# Make changes and test
pytest
make lint

# Commit and push
git commit -m "feat: add new feature"
git push origin feature/my-feature
```

### Q: How do I run tests?

**A:** Multiple test commands:

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_security.py

# Specific test
pytest tests/test_security.py::test_rate_limiter

# Verbose
pytest -v

# Stop on first failure
pytest -x
```

### Q: How do I add a new biometric model?

**A:** Implement the authenticator interface:

```python
# biometric/new_model.py
from biometric.base import BiometricAuthenticator

class NewModelAuthenticator(BiometricAuthenticator):
    def enroll_user(self, user_id: str, samples: List[str]) -> bool:
        # Implementation
        pass

    def authenticate(self, sample: str) -> dict:
        # Implementation
        pass

    def extract_features(self, sample: str) -> np.ndarray:
        # Implementation
        pass
```

**Then register in config:**
```python
SUPPORTED_MODELS.append('NewModel')
```

### Q: How do I add a new attack type?

**A:** Extend the attack generator:

```python
# attacks/presentation_attacks.py
class PresentationAttackGenerator:
    def generate_new_attack(self, image_path: str) -> np.ndarray:
        """
        Generate new attack type

        Args:
            image_path: Path to original image

        Returns:
            Attack image as numpy array
        """
        img = cv2.imread(image_path)
        # Apply attack transformation
        return attacked_img
```

**Register in CLI:**
```python
# cli_enhanced.py
ATTACK_TYPES = ['photo', 'video', 'mask', 'new_attack']
```

### Q: How do I add pre-commit hooks?

**A:**

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

**Hooks configured:** black, isort, flake8, mypy, bandit, yamllint

---

## General Questions

### Q: What's the difference between this and commercial solutions?

**A:**

| Feature | This System | Commercial (e.g., AWS Rekognition) |
|---------|-------------|-----------------------------------|
| Purpose | Research/Education | Production |
| Cost | Free | Pay-per-use |
| Customization | Full control | Limited |
| Attack Testing | Built-in | Not available |
| Anti-spoofing | Research-grade | Enterprise-grade |
| Support | Community | Professional |
| Compliance | DIY | Certified |

**Use this for:** Research, learning, testing, prototyping
**Use commercial for:** Production deployments, regulated industries

### Q: Can I use this for my research paper?

**A:** Yes! This is designed for research. Please cite:

```bibtex
@software{biometric_security_research,
  author = {Your Name},
  title = {Biometric Authentication \& Anti-Spoofing Security Research System},
  year = {2024},
  version = {2.0.0},
  url = {https://github.com/yourusername/biometric-security-research}
}
```

**See:** [CITATION.cff](../CITATION.cff) for citation details.

### Q: What's the roadmap for v3.0?

**A:** Planned features:

- Multi-modal fusion (face + fingerprint + iris)
- Deep learning anti-spoofing
- Real-time video authentication
- Web API (REST/GraphQL)
- Mobile SDK (iOS/Android)
- Federated learning support
- Blockchain-based audit trails
- FIDO2/WebAuthn integration

### Q: Is there a Docker Hub image?

**A:** Not yet. Build locally:

```bash
docker build -t biometric-security:2.0.0 .
docker run -it biometric-security:2.0.0
```

### Q: Can I use this commercially?

**A:** Yes, MIT license allows commercial use. **However:**

- No warranty provided
- Ensure compliance with biometric data laws
- Add production-grade security
- Consider liability insurance
- Get legal review

**Recommended:** Use for prototyping, then upgrade to commercial solution.

### Q: Where can I get help?

**A:** Multiple channels:

1. **Documentation:** Start with [README.md](../README.md)
2. **Issues:** [GitHub Issues](https://github.com/yourusername/biometric-security-research/issues)
3. **Discussions:** [GitHub Discussions](https://github.com/yourusername/biometric-security-research/discussions)
4. **Security:** [security@example.com](mailto:security@example.com) (private)

### Q: How often is this updated?

**A:**

- **Dependency updates:** Weekly (automated via Dependabot)
- **Security patches:** As needed (high priority)
- **Feature releases:** Quarterly
- **Major versions:** Yearly

**Stay updated:**
```bash
# Watch repository on GitHub
# Star repository for notifications
# Follow release notes
```

---

## Still Have Questions?

- Check [README.md](../README.md) for general information
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- See [API_REFERENCE.md](API_REFERENCE.md) for API documentation
- Read [SECURITY.md](../SECURITY.md) for security guidelines
- Open an [issue](https://github.com/yourusername/biometric-security-research/issues) if your question isn't answered

---

*Last updated: November 2024 | v2.0.0*
