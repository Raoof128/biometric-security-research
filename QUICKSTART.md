# Quick Start Guide

Get up and running with the Biometric Security Research System in 10 minutes.

## 1. Installation (2 minutes)

```bash
cd biometric-security-research

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Download Models (Optional - 1 minute)

For improved blink detection:

```bash
# Download dlib facial landmarks
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
mkdir -p biometric/models
mv shape_predictor_68_face_landmarks.dat biometric/models/
```

## 3. Prepare Sample Images (2 minutes)

Create test images:

```bash
# Create directories
mkdir -p data/alice
mkdir -p data/test_samples

# Add 3-5 photos of yourself to data/alice/
# Take photos from slightly different angles
# Ensure good lighting and clear face visibility

# Copy one test image to data/test_samples/
```

## 4. Enroll a User (1 minute)

```bash
# Enroll yourself as "alice"
python main.py enroll --user-id alice --modality face --image-dir data/alice/
```

Expected output:
```
[+] FaceAuthenticator initialized with Facenet model
[*] Enrolling user alice...
    [+] Processed: photo1.jpg
    [+] Processed: photo2.jpg
    [+] Processed: photo3.jpg
[+] User alice enrolled with 3 samples
[+] Model saved to data/enrolled_users/face_auth.pkl
```

## 5. Test Authentication (1 minute)

```bash
# Test with genuine image
python main.py authenticate --modality face --image data/test_samples/alice_test.jpg
```

Expected output:
```
[+] AUTHENTICATED: alice (confidence: 85.3%)
```

## 6. Generate Attacks (2 minutes)

```bash
# Generate presentation attacks
python main.py attack --image data/alice/photo1.jpg --attack-types photo,mask,degraded
```

Expected output:
```
[+] Photo attack generated: data/attack_samples/photo1_photo.jpg
[+] Mask attack simulation generated: data/attack_samples/photo1_mask.jpg
[+] Degraded quality attack generated: data/attack_samples/photo1_degraded.jpg
```

## 7. Test Liveness Detection (1 minute)

```bash
# Test anti-spoofing on attack image
python main.py liveness --test-type comprehensive \
    --image data/attack_samples/photo1_photo.jpg
```

Expected output:
```
[*] Running comprehensive anti-spoofing check...
    [*] Texture analysis: SPOOF (entropy: 4.23)
    [*] Depth analysis: 2D (edge density: 0.087)
    [*] Color diversity: SPOOF (score: 12.4)

[*] Final decision: SPOOF (confidence: 73.5%)
```

## 8. Real-time Demo (Optional)

```bash
# Start webcam authentication
python main.py realtime

# Look at camera, move your face
# Press 'q' to quit
```

## 9. Run Security Assessment (3 minutes)

```bash
# Full vulnerability test
python main.py vulnerability-test \
    --test-dir data/test_samples \
    --attack-source-dir data/alice/
```

This will:
- Test genuine authentication
- Generate and test attacks
- Calculate security metrics
- Generate HTML report

## 10. View Report

```bash
# Open the generated report
firefox data/results/security_report.html
# or
google-chrome data/results/security_report.html
# or
open data/results/security_report.html  # macOS
```

## Next Steps

### Explore Advanced Features

**Generate Deepfakes:**
```bash
python main.py deepfake \
    --source data/alice/photo1.jpg \
    --target data/bob/photo1.jpg \
    --output data/attack_samples/deepfake.jpg
```

**Test Blink Detection:**
```bash
python main.py liveness --test-type blink --use-webcam
```

**Enroll Multiple Users:**
```bash
python main.py enroll --user-id bob --modality face --image-dir data/bob/
python main.py enroll --user-id carol --modality face --image-dir data/carol/
```

**Test Fingerprints:**
```bash
# Generate synthetic fingerprints
python main.py attack --image data/fingerprints/sample.jpg --attack-types synthetic
```

## Troubleshooting

### "No module named 'cv2'"
```bash
pip install opencv-python
```

### "No module named 'deepface'"
```bash
pip install deepface
```

### "Webcam not detected"
```bash
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL')"
```

### "Low memory errors"
- Close other applications
- Use smaller images (resize to 640x480)
- Process fewer images at once

## Command Reference

```bash
# Enrollment
python main.py enroll --user-id <name> --modality face --image-dir <dir>

# Authentication
python main.py authenticate --modality face --image <path>

# Real-time
python main.py realtime

# Attacks
python main.py attack --image <path> --attack-types photo,mask,degraded

# Liveness
python main.py liveness --test-type comprehensive --image <path>

# Assessment
python main.py vulnerability-test --test-dir <dir>

# Report
python main.py report --results-file <json> --output <html>
```

## Getting Help

```bash
# View all commands
python main.py --help

# View command-specific help
python main.py enroll --help
python main.py attack --help
```

## What to Expect

### First Run
- DeepFace will download models (~100MB)
- Takes 30-60 seconds for first face processing
- Subsequent runs are faster (cached models)

### Performance
- Face enrollment: 5-10 seconds per image
- Authentication: 2-3 seconds per image
- Attack generation: 1-2 seconds per attack
- Full assessment: 2-5 minutes (depends on sample count)

### Memory Usage
- Idle: ~500MB
- Processing: 2-3GB
- Peak: 3-4GB

## Example Workflow

```bash
# 1. Setup
pip install -r requirements.txt

# 2. Enroll
python main.py enroll --user-id alice --modality face --image-dir data/alice/

# 3. Test
python main.py authenticate --modality face --image data/test_samples/alice.jpg

# 4. Attack
python main.py attack --image data/alice/photo1.jpg --attack-types photo,mask

# 5. Defend
python main.py liveness --test-type comprehensive --image data/attack_samples/photo1_photo.jpg

# 6. Assess
python main.py vulnerability-test --test-dir data/test_samples

# 7. Report
firefox data/results/security_report.html
```

## Success! 🎉

You now have a working biometric security research system. Check out README.md for advanced features and detailed documentation.
