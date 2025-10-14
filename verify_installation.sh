#!/bin/bash
# Installation verification script

echo "=========================================="
echo "Biometric Security System - Installation Check"
echo "=========================================="
echo ""

# Check Python version
echo "[*] Checking Python version..."
python3 --version || { echo "[-] Python 3 not found!"; exit 1; }
echo ""

# Check if virtual environment exists
echo "[*] Checking for virtual environment..."
if [ -d "venv" ]; then
    echo "[+] Virtual environment found"
else
    echo "[!] No virtual environment found"
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
    echo "[+] Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate || { echo "[-] Failed to activate venv"; exit 1; }
echo "[+] Virtual environment activated"
echo ""

# Check/install requirements
echo "[*] Checking Python packages..."
pip install -q -r requirements.txt
echo "[+] Dependencies installed"
echo ""

# Check key imports
echo "[*] Testing imports..."
python3 << EOF
import sys
errors = []

try:
    import cv2
    print("[+] OpenCV imported successfully")
except ImportError:
    errors.append("opencv-python")
    print("[-] OpenCV import failed")

try:
    from deepface import DeepFace
    print("[+] DeepFace imported successfully")
except ImportError:
    errors.append("deepface")
    print("[-] DeepFace import failed")

try:
    import numpy
    print("[+] NumPy imported successfully")
except ImportError:
    errors.append("numpy")
    print("[-] NumPy import failed")

try:
    import matplotlib
    print("[+] Matplotlib imported successfully")
except ImportError:
    errors.append("matplotlib")
    print("[-] Matplotlib import failed")

if errors:
    print(f"\n[-] Missing packages: {', '.join(errors)}")
    print("[*] Run: pip install " + " ".join(errors))
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "[-] Import test failed. Please install missing packages."
    exit 1
fi
echo ""

# Check directory structure
echo "[*] Checking directory structure..."
dirs=("biometric" "attacks" "defenses" "evaluation" "reporting" "data")
all_good=true

for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "[+] $dir/ exists"
    else
        echo "[-] $dir/ missing!"
        all_good=false
    fi
done
echo ""

# Check main files
echo "[*] Checking main files..."
files=("main.py" "requirements.txt" "README.md" "QUICKSTART.md")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "[+] $file exists"
    else
        echo "[-] $file missing!"
        all_good=false
    fi
done
echo ""

# Check for dlib model (optional)
echo "[*] Checking for optional dlib model..."
if [ -f "biometric/models/shape_predictor_68_face_landmarks.dat" ]; then
    echo "[+] dlib facial landmarks model found"
else
    echo "[!] dlib model not found (optional - improves blink detection)"
    echo "[*] Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
fi
echo ""

# Test CLI
echo "[*] Testing CLI interface..."
python3 main.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "[+] CLI interface working"
else
    echo "[-] CLI test failed"
    all_good=false
fi
echo ""

# Final summary
echo "=========================================="
if [ "$all_good" = true ]; then
    echo "✓ Installation verification PASSED"
    echo ""
    echo "Next steps:"
    echo "1. Generate test data: python3 generate_test_data.py"
    echo "2. Read QUICKSTART.md for usage examples"
    echo "3. Run: python3 main.py --help"
else
    echo "✗ Installation verification FAILED"
    echo "Please fix the errors above and try again."
    exit 1
fi
echo "=========================================="
