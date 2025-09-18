#!/bin/bash

# igus Rebel Pose Tracking Installation Script
# For NVIDIA Jetson Orin AGX with JetPack 6.2
# 
# This script installs the necessary dependencies and sets up
# the pose tracking system for igus Rebel robot control.

set -e

echo "======================================"
echo "igus Rebel Pose Tracking Setup"
echo "======================================"
echo ""

# Check if running on Jetson
if ! command -v jetson_release &> /dev/null; then
    echo "Warning: This script is optimized for NVIDIA Jetson devices."
    echo "Some optimizations may not be available on other platforms."
    echo ""
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python version check passed: $python_version"

# Update system packages
echo ""
echo "Updating system packages..."
sudo apt update

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libtiff5-dev \
    libjasper-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-serial-dev \
    libhdf5-dev \
    libhdf5-103 \
    python3-h5py \
    libqtgui4 \
    libqtwebkit4 \
    libqt4-test \
    python3-pyqt5 \
    libopenblas-base \
    libopenmpi-dev \
    zlib1g-dev \
    zip \
    libjpeg8-dev \
    liblapack-dev \
    libblas-dev \
    libhdf5-serial-dev \
    hdf5-tools \
    libhdf5-dev \
    zlib1g-dev \
    zip \
    libjpeg8-dev \
    liblapack-dev \
    libblas-dev

echo "✓ System dependencies installed"

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "✓ Virtual environment created and activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."

# Install numpy first (required by many other packages)
pip install numpy>=1.21.0

# Install OpenCV with optimizations for Jetson
echo "Installing OpenCV..."
if command -v jetson_release &> /dev/null; then
    # On Jetson, try to use pre-built OpenCV with CUDA support
    pip install opencv-python>=4.8.0
else
    # On other platforms, install standard OpenCV
    pip install opencv-python>=4.8.0
fi

# Install MediaPipe
echo "Installing MediaPipe..."
pip install mediapipe>=0.10.0

# Install other dependencies
echo "Installing additional dependencies..."
pip install -r requirements.txt

echo "✓ Python dependencies installed"

# Set up CUDA paths (if on Jetson)
if command -v jetson_release &> /dev/null; then
    echo ""
    echo "Configuring CUDA environment..."
    
    # Check if CUDA paths are already in bashrc
    if ! grep -q "CUDA" ~/.bashrc; then
        echo "Adding CUDA paths to ~/.bashrc..."
        cat >> ~/.bashrc << 'EOF'

# CUDA Environment for igus Rebel Pose Tracking
export PATH=/usr/local/cuda-12.6/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH
export CUDA_HOME=/usr/local/cuda-12.6
EOF
        echo "✓ CUDA paths added to ~/.bashrc"
        echo "Note: Run 'source ~/.bashrc' or restart terminal to apply CUDA settings"
    else
        echo "✓ CUDA paths already configured"
    fi
fi

# Test camera access
echo ""
echo "Testing camera access..."
if python3 -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); cap.release(); print('Camera test:', 'PASSED' if ret else 'FAILED')"; then
    echo "✓ Camera access test passed"
else
    echo "⚠ Camera access test failed - check camera connection"
fi

# Test MediaPipe installation
echo ""
echo "Testing MediaPipe installation..."
if python3 -c "import mediapipe as mp; print('MediaPipe version:', mp.__version__)"; then
    echo "✓ MediaPipe installation test passed"
else
    echo "✗ MediaPipe installation test failed"
    exit 1
fi

# Create launch script
echo ""
echo "Creating launch script..."
cat > launch_pose_tracking.sh << 'EOF'
#!/bin/bash

# Launch script for igus Rebel Pose Tracking

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run install_pose_tracking.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set CUDA environment if on Jetson
if command -v jetson_release &> /dev/null; then
    export PATH=/usr/local/cuda-12.6/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH
    export CUDA_HOME=/usr/local/cuda-12.6
fi

# Launch the pose tracking system
if [ "$1" = "example" ]; then
    echo "Launching example pose tracking..."
    python3 example_pose_tracking.py "${@:2}"
else
    echo "Launching main pose tracking system..."
    python3 igus_rebel_pose_tracking.py "$@"
fi
EOF

chmod +x launch_pose_tracking.sh
echo "✓ Launch script created: ./launch_pose_tracking.sh"

# Create desktop shortcut (if desktop environment available)
if [ ! -z "$DISPLAY" ] && command -v desktop-file-install &> /dev/null; then
    echo ""
    echo "Creating desktop shortcut..."
    
    cat > igus_rebel_pose_tracking.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=igus Rebel Pose Tracking
Comment=Pose tracking system for igus Rebel robot
Exec=$(pwd)/launch_pose_tracking.sh example
Icon=applications-engineering
Terminal=true
Categories=Development;Engineering;
EOF

    desktop-file-install --dir=$HOME/.local/share/applications igus_rebel_pose_tracking.desktop
    echo "✓ Desktop shortcut created"
    rm igus_rebel_pose_tracking.desktop
fi

# Final setup summary
echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Summary:"
echo "✓ System dependencies installed"
echo "✓ Python virtual environment created"
echo "✓ Python packages installed"
echo "✓ CUDA environment configured (if on Jetson)"
echo "✓ Launch script created"
echo ""
echo "Usage:"
echo "  ./launch_pose_tracking.sh          # Run main pose tracking system"
echo "  ./launch_pose_tracking.sh example  # Run example with gesture recognition"
echo ""
echo "Configuration:"
echo "  Edit 'pose_tracking_config.json' to customize settings"
echo "  Update robot IP address if different from 192.168.1.100"
echo ""
echo "Next steps:"
echo "1. Connect your camera and igus Rebel robot"
echo "2. Update robot IP in pose_tracking_config.json if needed"
echo "3. Run: ./launch_pose_tracking.sh example"
echo ""

# Deactivate virtual environment
deactivate

echo "Setup complete! The virtual environment has been deactivated."
echo "Use the launch script to run the pose tracking system."