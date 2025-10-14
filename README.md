# Biometric Authentication & Anti-Spoofing Security Research System

A comprehensive biometric security research platform that demonstrates both offensive (red team) and defensive (blue team) capabilities. This system implements face and fingerprint authentication, systematically tests it against presentation attacks (photo, video, 3D mask, deepfakes), and evaluates anti-spoofing defenses.

**Perfect for cybersecurity + AI/ML portfolio projects.**

## Overview

This project combines cutting-edge AI/ML with practical cybersecurity research to:
- Build production-quality biometric authentication systems
- Simulate realistic presentation attacks
- Implement and test anti-spoofing defenses
- Generate comprehensive security assessment reports

## Key Features

### Biometric Authentication
- **Face Recognition**: DeepFace with lightweight Facenet model
- **Fingerprint Matching**: ORB feature-based matching system
- **Real-time Authentication**: Webcam-based live recognition
- **Multi-user Support**: Enrollment and authentication workflows

### Presentation Attacks (Red Team)
- **Photo Attacks**: Printed photos with realistic texture/glare
- **Video Replay**: Screen display with digital artifacts
- **3D Mask Simulation**: Reduced micro-details and warping
- **Deepfake Generation**: Lightweight face swapping
- **Synthetic Fingerprints**: Generated arch/loop/whorl patterns
- **Degraded Quality**: Low resolution and compression artifacts

### Anti-Spoofing Defenses (Blue Team)
- **Blink Detection**: Eye aspect ratio (EAR) analysis with dlib
- **Texture Analysis**: Local Binary Pattern (LBP) entropy
- **Active Flash Test**: Illumination response detection
- **Depth Analysis**: 3D vs 2D discrimination
- **Color Diversity**: Micro-variation analysis
- **Comprehensive Scoring**: Multi-method weighted decision

### Vulnerability Assessment
- **Automated Testing**: Systematic attack simulation
- **Security Metrics**: FAR, FRR, EER calculation
- **Attack Success Rates**: Measurement for each attack type
- **Anti-Spoofing Effectiveness**: Detection rate analysis

### Security Reporting
- **HTML Reports**: Professional security assessment documents
- **Visualizations**: Matplotlib charts for metrics and trends
- **Executive Summary**: High-level findings and recommendations
- **Australian Compliance**: Privacy Act 1988 and OAIC guidelines

## System Architecture

```
biometric-security-research/
├── biometric/               # Authentication modules
│   ├── face_recognition.py  # DeepFace-based face auth
│   ├── fingerprint_matcher.py
│   └── models/              # Pre-trained models
├── attacks/                 # Presentation attack simulation
│   ├── presentation_attacks.py
│   └── deepfake_generator.py
├── defenses/                # Anti-spoofing defenses
│   └── liveness_detection.py
├── evaluation/              # Vulnerability testing
│   └── vulnerability_tester.py
├── reporting/               # Report generation
│   ├── report_generator.py
│   └── templates/
├── data/                    # Data storage
│   ├── enrolled_users/
│   ├── test_samples/
│   ├── attack_samples/
│   └── results/
└── main.py                  # CLI interface
```

## Installation

### Prerequisites
- Python 3.10+
- Webcam (for real-time testing)
- 8GB RAM minimum
- Linux/macOS/Windows

### Setup

```bash
# Clone or navigate to project directory
cd biometric-security-research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download dlib facial landmarks model (optional but recommended)
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
mv shape_predictor_68_face_landmarks.dat biometric/models/
```

## Quick Start

### 1. Enroll Users

```bash
# Enroll user with face images
python main.py enroll --user-id alice --modality face \
    --images data/alice/photo1.jpg,data/alice/photo2.jpg,data/alice/photo3.jpg

# Enroll fingerprint
python main.py enroll --user-id bob --modality fingerprint \
    --image data/bob/fingerprint.jpg
```

### 2. Authenticate

```bash
# Authenticate with face
python main.py authenticate --modality face --image data/test/alice_test.jpg

# Real-time authentication (webcam)
python main.py realtime
```

### 3. Generate Attacks

```bash
# Generate presentation attacks
python main.py attack --image data/alice/photo1.jpg \
    --attack-types photo,mask,degraded

# Generate deepfake
python main.py deepfake --source data/alice/photo1.jpg \
    --target data/bob/photo1.jpg --output data/attack_samples/deepfake.jpg
```

### 4. Test Anti-Spoofing

```bash
# Comprehensive liveness detection
python main.py liveness --test-type comprehensive \
    --image data/attack_samples/photo_attack.jpg

# Blink detection (webcam)
python main.py liveness --test-type blink --use-webcam

# Texture analysis
python main.py liveness --test-type texture --image data/test/sample.jpg
```

### 5. Run Vulnerability Assessment

```bash
# Full security assessment
python main.py vulnerability-test \
    --test-dir data/test_samples \
    --attack-source-dir data/enrolled_users \
    --output data/results/security_report.html
```

### 6. Generate Security Report

```bash
# Generate report from existing results
python main.py report \
    --results-file data/results/vulnerability_test.json \
    --output data/results/security_report.html
```

## Usage Examples

### Example 1: Complete Workflow

```bash
# Step 1: Enroll multiple users
python main.py enroll --user-id alice --modality face --image-dir data/alice/
python main.py enroll --user-id bob --modality face --image-dir data/bob/
python main.py enroll --user-id carol --modality face --image-dir data/carol/

# Step 2: Test genuine authentication
python main.py authenticate --modality face --image data/test/alice_genuine.jpg

# Step 3: Generate attacks for each user
python main.py attack --image data/alice/photo1.jpg --attack-types photo,mask,degraded
python main.py attack --image data/bob/photo1.jpg --attack-types photo,mask,degraded

# Step 4: Run full vulnerability assessment
python main.py vulnerability-test \
    --test-dir data/test_samples \
    --attack-source-dir data/enrolled_users

# Step 5: View the generated security report
firefox data/results/security_report.html
```

### Example 2: Real-time Demo

```bash
# Start real-time authentication with webcam
python main.py realtime

# Press 's' to save frames
# Press 'q' to quit
```

### Example 3: Research Workflow

```bash
# Test different liveness detection methods
python main.py liveness --test-type texture --image attack_sample.jpg
python main.py liveness --test-type comprehensive --image attack_sample.jpg --use-webcam

# Generate custom attacks
python main.py attack --image genuine.jpg --attack-types photo
python main.py deepfake --source attacker.jpg --target victim.jpg

# Evaluate effectiveness
python main.py vulnerability-test --test-dir data/test_samples
```

## Memory Optimization

This system is designed for 8GB RAM systems:
- Uses lightweight models (Facenet instead of VGG-Face)
- Sequential processing (one image at a time)
- Efficient OpenCV operations
- Inference-only mode (no training)
- Estimated memory: 3-4 GB including OS

## Security Metrics Explained

### False Acceptance Rate (FAR)
Percentage of imposters incorrectly accepted. Lower is better.
- Excellent: < 0.01%
- Good: 0.01% - 0.1%
- Acceptable: 0.1% - 1%
- Poor: > 1%

### False Rejection Rate (FRR)
Percentage of genuine users incorrectly rejected. Lower is better.
- Excellent: < 1%
- Good: 1% - 5%
- Acceptable: 5% - 10%
- Poor: > 10%

### Equal Error Rate (EER)
Point where FAR = FRR. Lower is better.
- Excellent: < 1%
- Good: 1% - 5%
- Acceptable: 5% - 10%
- Poor: > 10%

## Australian Privacy Compliance

### Privacy Act 1988
Biometric data is **sensitive information** requiring:
- Explicit, informed consent
- AES-256 encryption at rest
- TLS 1.3 for data in transit
- Secure deletion procedures
- Regular privacy impact assessments (PIAs)

### OAIC Guidelines
- Notifiable Data Breaches (NDB) scheme
- Report breaches within 30 days
- Document security measures
- Third-party vendor compliance

### References
- [Office of the Australian Information Commissioner](https://www.oaic.gov.au/)
- [Privacy Act 1988](https://www.legislation.gov.au/Series/C2004A03712)

## Research Applications

This system is ideal for:
- **Security Research**: Testing biometric vulnerabilities
- **Academic Projects**: ML + Cybersecurity thesis work
- **Portfolio Development**: Demonstrating red team + blue team skills
- **Education**: Teaching biometric security concepts
- **Proof-of-Concept**: Evaluating authentication systems

## Project Highlights for Portfolio

### Technical Skills Demonstrated
- **Machine Learning**: DeepFace, CNN models, feature extraction
- **Computer Vision**: OpenCV, facial landmarks, image processing
- **Security Testing**: Penetration testing, vulnerability assessment
- **Python Development**: CLI tools, modular architecture, OOP
- **Data Visualization**: Matplotlib, HTML reports, metrics analysis
- **Research**: Systematic evaluation, documentation, reporting

### Unique Value Proposition
- Combines AI/ML with offensive/defensive security
- Red team (attacks) + Blue team (defenses)
- Measurable results (FAR/FRR/EER metrics)
- Production-quality code and documentation
- Australian compliance awareness
- Portfolio-ready with professional reports

## Limitations & Disclaimers

### Research Limitations
- Simplified fingerprint matching (not production-grade minutiae extraction)
- Basic deepfake generation (not state-of-the-art GAN models)
- Limited training data (requires user-provided samples)
- Webcam-only liveness detection (no dedicated depth sensors)

### Ethical Use
This system is for:
- Security research and education
- Authorized penetration testing
- Academic study
- Personal learning

**NOT for:**
- Unauthorized access attempts
- Malicious use
- Privacy violations
- Production deployment without proper security review

## Future Enhancements

### Potential Improvements
- [ ] Neural network-based anti-spoofing (CNN classifier)
- [ ] Advanced deepfake detection models
- [ ] Multi-modal biometrics (face + fingerprint + voice)
- [ ] Cloud training support (Google Colab integration)
- [ ] Real-time depth sensing (Intel RealSense)
- [ ] Behavioral biometrics (typing patterns, gait)
- [ ] Automated adversarial testing framework
- [ ] Integration with MITRE ATT&CK framework

## Troubleshooting

### Common Issues

**ImportError: No module named 'deepface'**
```bash
pip install --upgrade deepface
```

**dlib installation fails**
```bash
# On Ubuntu/Debian
sudo apt-get install build-essential cmake
pip install dlib

# On macOS
brew install cmake
pip install dlib
```

**Webcam not detected**
```bash
# Check available cameras
ls /dev/video*

# Test with OpenCV
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

**Memory errors**
- Reduce image resolution
- Process fewer images at once
- Use swap space
- Close other applications

## Contributing

This is a research/educational project. Feel free to:
- Fork and experiment
- Add new attack methods
- Improve anti-spoofing techniques
- Enhance documentation
- Share findings (with proper credit)

## License

This project is for educational and research purposes. Use responsibly and ethically.

## References

### Academic Papers
1. Chingovska et al. (2012) - "On the Effectiveness of Local Binary Patterns in Face Anti-spoofing"
2. Patel et al. (2016) - "Secure Face Unlock: Spoof Detection on Smartphones"
3. Akhtar & Mian (2018) - "Threat of Adversarial Attacks on Deep Learning in Computer Vision"

### Tools & Libraries
- [DeepFace](https://github.com/serengil/deepface) - Face recognition framework
- [OpenCV](https://opencv.org/) - Computer vision library
- [dlib](http://dlib.net/) - Machine learning toolkit

### Security Resources
- [NIST Biometric Standards](https://www.nist.gov/programs-projects/biometric-standards-and-testing)
- [FIDO Alliance](https://fidoalliance.org/) - Authentication standards
- [OWASP](https://owasp.org/) - Web application security

## Contact & Support

For questions, issues, or collaboration:
- Open an issue on GitHub
- Review documentation in `/docs`
- Check troubleshooting section above

## Acknowledgments

- DeepFace library by Sefik Ilkin Serengil
- OpenCV community
- dlib by Davis King
- Australian privacy law resources by OAIC

---

**Built for security researchers, by security researchers.**

**Optimized for 8GB Linux systems. Tested on Ubuntu 20.04+**
