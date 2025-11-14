# API Reference

Complete API documentation for the Biometric Security Research System v2.0.

## Table of Contents

- [Configuration](#configuration)
- [Biometric Authentication](#biometric-authentication)
- [Attacks](#attacks)
- [Defenses](#defenses)
- [Evaluation](#evaluation)
- [Reporting](#reporting)
- [Utilities](#utilities)

---

## Configuration

### `config.SystemConfig`

Main system configuration class.

```python
from config import SystemConfig, get_config

# Get global configuration
config = get_config()

# Create custom configuration
custom_config = SystemConfig()
custom_config.biometric.model_name = 'VGG-Face'
custom_config.biometric.similarity_threshold = 0.75

# Validate configuration
is_valid, errors = config.validate()

# Save configuration
config.to_json('config.json')

# Load configuration
config = SystemConfig.from_json('config.json')
```

**Key Methods:**
- `validate()` → `Tuple[bool, List[str]]`: Validate configuration
- `to_dict()` → `Dict`: Convert to dictionary
- `to_json(filepath)` → `str`: Export to JSON
- `from_json(filepath)` → `SystemConfig`: Load from JSON

**Configuration Sections:**
- `biometric`: Face/fingerprint settings
- `liveness`: Anti-spoofing parameters
- `attack`: Attack generation settings
- `security`: Security policies
- `performance`: Performance tuning
- `logging`: Logging configuration
- `paths`: File paths

---

## Biometric Authentication

### `biometric.face_recognition.FaceAuthenticator`

Face recognition and authentication.

```python
from biometric.face_recognition import FaceAuthenticator

# Initialize
auth = FaceAuthenticator(
    model_name='Facenet',  # Options: Facenet, VGG-Face, OpenFace
    detector='opencv'       # Options: opencv, ssd, mtcnn
)

# Enroll user
images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
success = auth.enroll_user('alice', images)

# Save model
auth.save_model('face_auth.pkl')

# Load model
auth.load_model('face_auth.pkl')

# Authenticate
user_id, score = auth.authenticate('test_image.jpg')
if user_id:
    print(f"Authenticated as {user_id} with confidence {score:.2%}")
```

**Methods:**

#### `__init__(model_name, detector)`
Initialize face authenticator.
- **Parameters:**
  - `model_name` (str): Model to use
  - `detector` (str): Face detector backend
- **Returns:** FaceAuthenticator instance

#### `enroll_user(user_id, image_paths)`
Enroll a new user.
- **Parameters:**
  - `user_id` (str): Unique user identifier
  - `image_paths` (Union[str, List[str]]): Image path(s)
- **Returns:** bool - Success status

#### `authenticate(image_path)`
Authenticate user from image.
- **Parameters:**
  - `image_path` (str): Path to test image
- **Returns:** Tuple[Optional[str], float] - (user_id, similarity_score)

#### `save_model(filepath)`
Save enrolled users database.
- **Parameters:**
  - `filepath` (str): Save path
- **Returns:** None

#### `load_model(filepath)`
Load enrolled users database.
- **Parameters:**
  - `filepath` (str): Model path
- **Returns:** bool - Success status

### `biometric.face_recognition.RealtimeFaceAuth`

Real-time webcam authentication.

```python
from biometric.face_recognition import RealtimeFaceAuth

realtime = RealtimeFaceAuth(auth)
realtime.run()  # Press 'q' to quit, 's' to save frame
```

### `biometric.fingerprint_matcher.FingerprintMatcher`

Fingerprint matching system.

```python
from biometric.fingerprint_matcher import FingerprintMatcher

matcher = FingerprintMatcher()

# Enroll fingerprint
success = matcher.enroll_fingerprint('bob', 'fingerprint.jpg')

# Match fingerprint
user_id, score = matcher.match_fingerprint('test_fingerprint.jpg')

# Save/load database
matcher.save_database('fingerprint_db.pkl')
matcher.load_database('fingerprint_db.pkl')
```

---

## Attacks

### `attacks.presentation_attacks.PresentationAttacks`

Standard presentation attack generation.

```python
from attacks.presentation_attacks import PresentationAttacks

attacks = PresentationAttacks(output_dir='data/attacks')

# Generate photo attack
photo_path = attacks.photo_attack('genuine.jpg', 'photo_attack')

# Generate mask attack
mask_path = attacks.mask_attack_simulation('genuine.jpg', 'mask_attack')

# Generate degraded quality attack
degraded_path = attacks.degraded_quality_attack('genuine.jpg')

# Batch generation
results = attacks.batch_generate_attacks(
    'genuine.jpg',
    attack_types=['photo', 'mask', 'degraded']
)
```

**Attack Types:**
- `photo_attack()`: Printed photo with texture/glare
- `video_replay_attack()`: Screen replay with artifacts
- `mask_attack_simulation()`: 3D mask simulation
- `degraded_quality_attack()`: Low quality/compression
- `synthetic_fingerprint()`: Generated fingerprint patterns

### `attacks.adversarial_attacks.AdversarialAttacker`

Advanced adversarial attacks.

```python
from attacks.adversarial_attacks import AdversarialAttacker

attacker = AdversarialAttacker()

# Adversarial patch
patch_path = attacker.generate_adversarial_patch(
    'face.jpg',
    patch_size=(50, 50),
    attack_name='patch_attack'
)

# FGSM attack
fgsm_path = attacker.generate_fgsm_attack(
    'face.jpg',
    epsilon=0.1,
    attack_name='fgsm_attack'
)

# Adversarial glasses
glasses_path = attacker.generate_glasses_attack('face.jpg')

# Pixel attack
pixel_path = attacker.generate_pixel_attack('face.jpg', num_pixels=100)

# Face morphing
morphed_path = attacker.generate_morphing_attack(
    'face1.jpg',
    'face2.jpg',
    alpha=0.5
)

# Batch generation
results = attacker.batch_generate_adversarial_attacks(
    'face.jpg',
    attack_types=['patch', 'fgsm', 'glasses', 'pixel']
)
```

### `attacks.deepfake_generator.LightweightDeepfake`

Deepfake generation.

```python
from attacks.deepfake_generator import LightweightDeepfake

deepfake = LightweightDeepfake()

result = deepfake.simple_face_swap(
    source='source.jpg',
    target='target.jpg',
    output='deepfake.jpg'
)
```

---

## Defenses

### `defenses.liveness_detection.LivenessDetector`

Multi-method liveness detection.

```python
from defenses.liveness_detection import LivenessDetector

liveness = LivenessDetector(use_dlib=True)

# Blink detection (webcam)
is_live, annotated_frame = liveness.detect_blink(frame)

# Texture analysis
is_real, entropy = liveness.texture_analysis('image.jpg')

# Active flash test (webcam)
is_live, difference = liveness.active_flash_test()

# Depth analysis
is_3d, edge_density = liveness.depth_analysis('image.jpg')

# Color diversity
is_real, diversity_score = liveness.color_diversity_analysis('image.jpg')
```

**Methods:**

#### `detect_blink(frame)`
Detect eye blinks for liveness.
- **Parameters:** `frame` (np.ndarray): Video frame
- **Returns:** Tuple[bool, np.ndarray] - (is_live, annotated_frame)

#### `texture_analysis(image_path)`
Analyze texture using LBP.
- **Parameters:** `image_path` (str): Image path
- **Returns:** Tuple[bool, float] - (is_real, entropy_score)

#### `active_flash_test(duration)`
Test illumination response.
- **Parameters:** `duration` (float): Test duration in seconds
- **Returns:** Tuple[bool, float] - (is_live, mean_difference)

### `defenses.liveness_detection.AntiSpoofingSystem`

Comprehensive anti-spoofing.

```python
from defenses.liveness_detection import AntiSpoofingSystem

anti_spoof = AntiSpoofingSystem()

# Comprehensive check
results = anti_spoof.comprehensive_check(
    'image.jpg',
    use_webcam=False
)

print(f"Final decision: {results['final_decision']}")
print(f"Confidence: {results['confidence']:.2%}")

# Batch testing
results_list = anti_spoof.batch_test(['img1.jpg', 'img2.jpg'])
```

---

## Evaluation

### `evaluation.vulnerability_tester.VulnerabilityTester`

Security vulnerability testing.

```python
from evaluation.vulnerability_tester import VulnerabilityTester

tester = VulnerabilityTester(face_auth, fingerprint_auth)

# Run full assessment
results = tester.run_full_assessment(
    genuine_test_dir='data/test_samples',
    genuine_enroll_dir='data/enrolled_users'
)

# Calculate metrics
metrics = tester.calculate_metrics()
print(f"FAR: {metrics['FAR']:.2%}")
print(f"FRR: {metrics['FRR']:.2%}")
print(f"EER: {metrics['EER']:.2%}")

# Save results
tester.save_results('results.json')
```

**Key Metrics:**
- `FAR`: False Acceptance Rate
- `FRR`: False Rejection Rate
- `EER`: Equal Error Rate
- `Genuine_Accuracy`: Genuine user acceptance rate
- `Attack_Success_Rate`: Attack success percentage
- `AntiSpoof_Detection_Rate`: Spoof detection rate

---

## Reporting

### `reporting.enhanced_report.EnhancedReportGenerator`

Interactive security reports.

```python
from reporting.enhanced_report import EnhancedReportGenerator

# From results file
report_gen = EnhancedReportGenerator(results_file='results.json')

# Generate interactive dashboard
report_gen.generate_interactive_dashboard('report.html')

# From results data
report_gen = EnhancedReportGenerator(results_data=results_dict)
report_gen.generate_interactive_dashboard('report.html')
```

---

## Utilities

### Security Utilities

```python
from utils.security import (
    get_validator,
    get_rate_limiter,
    get_secure_handler,
    get_audit_logger
)

# Input validation
validator = get_validator()
is_valid, error = validator.validate_file_path('image.jpg')
is_valid, error = validator.validate_user_id('alice')
sanitized = validator.sanitize_filename('../../etc/passwd')

# Rate limiting
rate_limiter = get_rate_limiter()
allowed, retry_after = rate_limiter.is_allowed('user123')
rate_limiter.reset('user123')

# Secure data handling
secure_handler = get_secure_handler()
key = secure_handler.generate_key(32)
hash_hex, salt_hex = secure_handler.hash_data('password')
is_valid = secure_handler.verify_hash('password', hash_hex, salt_hex)
secure_handler.secure_delete('sensitive_file.txt')

# Audit logging
audit_logger = get_audit_logger()
audit_logger.log_authentication_attempt('alice', True, 'face')
audit_logger.log_enrollment('bob', True, 'fingerprint')
```

### Performance Utilities

```python
from utils.performance import (
    get_performance_monitor,
    get_embedding_cache,
    optimize_memory
)

# Performance monitoring
monitor = get_performance_monitor()
memory = monitor.get_memory_usage()
cpu = monitor.get_cpu_usage()
snapshot = monitor.log_performance_snapshot('checkpoint')

# Embedding cache
cache = get_embedding_cache()
embedding = cache.get_embedding('image.jpg')
cache.put_embedding('image.jpg', embedding_vector)
stats = cache.get_stats()

# Memory optimization
freed_mb = optimize_memory()
```

### Logging Utilities

```python
from utils.logger import get_logger, log_execution_time, LogContext

# Get logger
logger = get_logger(__name__)

# Basic logging
logger.info("Processing started")
logger.warning("Resource low")
logger.error("Operation failed")

# Execution time decorator
@log_execution_time()
def process_data():
    # ... processing ...
    pass

# Context manager
with LogContext('processing batch', logger) as ctx:
    ctx.add_data('batch_size', 100)
    # ... processing ...
```

---

## CLI Usage

### Standard CLI

```bash
# Enroll user
python main.py enroll --user-id alice --modality face --images img1.jpg,img2.jpg

# Authenticate
python main.py authenticate --modality face --image test.jpg

# Generate attacks
python main.py attack --image genuine.jpg --attack-types photo,mask

# Run vulnerability test
python main.py vulnerability-test --test-dir data/test_samples

# Generate report
python main.py report --results-file results.json --output report.html
```

### Enhanced CLI (v2.0)

```bash
# System status
python cli_enhanced.py status

# Enhanced enrollment
python cli_enhanced.py enroll --user-id alice --modality face --image-dir data/alice/

# Advanced attacks
python cli_enhanced.py attack --image face.jpg --attack-types patch,fgsm,glasses

# Interactive report
python cli_enhanced.py enhanced-report --results-file results.json --output dashboard.html
```

---

## Error Handling

All functions include proper error handling and logging. Typical error patterns:

```python
try:
    user_id, score = auth.authenticate('image.jpg')
except FileNotFoundError:
    logger.error("Image file not found")
except ValueError:
    logger.error("Invalid image format")
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
```

---

## Best Practices

1. **Always validate inputs** using `InputValidator`
2. **Use rate limiting** for authentication endpoints
3. **Enable audit logging** for compliance
4. **Monitor performance** with `PerformanceMonitor`
5. **Cache embeddings** for better performance
6. **Use context managers** for automatic cleanup
7. **Handle errors gracefully** with try-except blocks
8. **Log all operations** with appropriate levels

---

## Examples

See the `examples/` directory for complete usage examples:
- `01_simple_enrollment.py`: User enrollment
- `02_authentication.py`: User authentication
- `03_generate_attacks.py`: Attack generation

---

## Type Hints

All functions include type hints for better IDE support and type checking:

```python
def authenticate(self, image_path: str) -> Tuple[Optional[str], float]:
    """Authenticate user from image."""
    pass
```

---

For more information, see the source code docstrings and the main [README.md](../README.md).
