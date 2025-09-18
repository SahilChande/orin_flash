#!/usr/bin/env python3
"""
Test script for igus Rebel Pose Tracking System
===============================================

This script performs basic validation of the pose tracking installation
and checks if all components are working correctly.

Usage:
    python3 test_pose_tracking.py
"""

import sys
import os
import time
import json

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print(f"✓ MediaPipe: {mp.__version__}")
    except ImportError as e:
        print(f"✗ MediaPipe import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    return True

def test_camera():
    """Test camera access"""
    print("\nTesting camera access...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Camera not accessible")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print(f"✓ Camera working: {frame.shape}")
            return True
        else:
            print("✗ Camera not returning frames")
            return False
            
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def test_cuda():
    """Test CUDA availability"""
    print("\nTesting CUDA...")
    
    try:
        import cv2
        cuda_devices = cv2.cuda.getCudaEnabledDeviceCount()
        
        if cuda_devices > 0:
            print(f"✓ CUDA available: {cuda_devices} device(s)")
            return True
        else:
            print("⚠ CUDA not available (CPU-only mode)")
            return True  # Not critical for basic functionality
            
    except Exception as e:
        print(f"⚠ CUDA test failed: {e} (CPU-only mode)")
        return True  # Not critical

def test_mediapipe():
    """Test MediaPipe pose detection"""
    print("\nTesting MediaPipe pose detection...")
    
    try:
        import cv2
        import mediapipe as mp
        import numpy as np
        
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5
        )
        
        # Create a simple test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Convert to RGB
        rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = pose.process(rgb_image)
        
        pose.close()
        print("✓ MediaPipe pose detection initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ MediaPipe test failed: {e}")
        return False

def test_config_file():
    """Test configuration file"""
    print("\nTesting configuration file...")
    
    config_file = "pose_tracking_config.json"
    
    if not os.path.exists(config_file):
        print(f"✗ Configuration file not found: {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_keys = ['robot_ip', 'robot_port', 'camera_index']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"✗ Missing configuration keys: {missing_keys}")
            return False
        
        print(f"✓ Configuration file valid")
        print(f"  - Robot IP: {config['robot_ip']}")
        print(f"  - Robot Port: {config['robot_port']}")
        print(f"  - Camera Index: {config['camera_index']}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ Configuration file invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Configuration file test failed: {e}")
        return False

def test_pose_tracking_module():
    """Test the main pose tracking module"""
    print("\nTesting pose tracking module...")
    
    try:
        # Import the main module
        from igus_rebel_pose_tracking import PoseTrackingSystem, PoseDetector, IgusRebelCommunicator
        
        # Create a pose detector
        detector = PoseDetector()
        print("✓ PoseDetector created successfully")
        
        # Create a robot communicator (without connecting)
        communicator = IgusRebelCommunicator()
        print("✓ IgusRebelCommunicator created successfully")
        
        # Create the main system
        system = PoseTrackingSystem()
        print("✓ PoseTrackingSystem created successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Module test failed: {e}")
        return False

def test_example_module():
    """Test the example module"""
    print("\nTesting example module...")
    
    try:
        from example_pose_tracking import ExamplePoseTracker
        
        tracker = ExamplePoseTracker()
        print("✓ ExamplePoseTracker created successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Example module import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Example module test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("igus Rebel Pose Tracking - System Test")
    print("======================================")
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Camera Test", test_camera),
        ("CUDA Test", test_cuda),
        ("MediaPipe Test", test_mediapipe),
        ("Configuration Test", test_config_file),
        ("Pose Tracking Module Test", test_pose_tracking_module),
        ("Example Module Test", test_example_module),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name + ":"))
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary:")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The pose tracking system is ready to use.")
        print("\nNext steps:")
        print("1. Connect your camera and igus Rebel robot")
        print("2. Update robot IP in pose_tracking_config.json if needed")
        print("3. Run: ./launch_pose_tracking.sh example")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the installation.")
        print("\nTroubleshooting:")
        print("1. Run the installation script again: ./install_pose_tracking.sh")
        print("2. Check camera connection and permissions")
        print("3. Verify CUDA installation if needed")
        return 1

if __name__ == "__main__":
    exit(main())