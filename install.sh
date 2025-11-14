#!/bin/bash
# Installation script for Biometric Security Research System v2.0

set -e

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║   Biometric Security Research System v2.0 - Installation            ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ is required"
    exit 1
fi
echo "✅ Python version OK"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install requirements
echo "📥 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies may have failed to install"
    echo "   You can install them manually with: pip install -r requirements.txt"
fi
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/enrolled_users
mkdir -p data/test_samples
mkdir -p data/attack_samples
mkdir -p data/results
mkdir -p biometric/models
mkdir -p logs
echo "✅ Directories created"
echo ""

# Optional: Download dlib model
echo "📥 Optional: Download dlib facial landmarks model?"
echo "   This improves liveness detection but requires ~100MB download"
read -p "   Download? (y/N): " download_dlib

if [ "$download_dlib" = "y" ] || [ "$download_dlib" = "Y" ]; then
    echo "   Downloading shape_predictor_68_face_landmarks.dat..."

    if command -v wget &> /dev/null; then
        wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 -P biometric/models/
        bunzip2 biometric/models/shape_predictor_68_face_landmarks.dat.bz2
        echo "✅ dlib model downloaded"
    elif command -v curl &> /dev/null; then
        curl -L http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 -o biometric/models/shape_predictor_68_face_landmarks.dat.bz2
        bunzip2 biometric/models/shape_predictor_68_face_landmarks.dat.bz2
        echo "✅ dlib model downloaded"
    else
        echo "⚠️  wget or curl not found. Please download manually:"
        echo "   http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    fi
else
    echo "   Skipped dlib model download"
fi
echo ""

# Run tests
echo "🧪 Running tests..."
pytest --tb=short -q
if [ $? -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "⚠️  Some tests failed, but installation can continue"
fi
echo ""

# Show system status
echo "ℹ️  System Status:"
python3 cli_enhanced.py status 2>/dev/null || echo "   CLI ready to use"
echo ""

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║   ✅ Installation Complete!                                          ║"
echo "║                                                                      ║"
echo "║   Quick Start:                                                       ║"
echo "║   1. Activate venv: source venv/bin/activate                        ║"
echo "║   2. Check status: python cli_enhanced.py status                    ║"
echo "║   3. View help: python main.py --help                               ║"
echo "║   4. Read docs: cat docs/FEATURES_V2.md                             ║"
echo "║                                                                      ║"
echo "║   Examples:                                                          ║"
echo "║   - python main.py enroll --user-id alice --modality face ...       ║"
echo "║   - python cli_enhanced.py attack --image face.jpg ...              ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
