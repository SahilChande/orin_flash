# igus Rebel Pose Tracking

Real-time pose tracking system for igus Rebel collaborative robot arms running on NVIDIA Jetson Orin AGX.

## Quick Start

1. **Install the system:**
   ```bash
   ./install_pose_tracking.sh
   ```

2. **Configure robot IP:**
   ```bash
   nano pose_tracking_config.json
   # Update "robot_ip": "YOUR_ROBOT_IP"
   ```

3. **Run the example:**
   ```bash
   ./launch_pose_tracking.sh example
   ```

## Features

- **Real-time pose detection** using MediaPipe with GPU acceleration
- **Gesture recognition** (wave, point, stop)
- **Robot communication** via TCP/IP
- **Safety features** with joint limits and emergency stop
- **Data recording** and session export
- **Visualization** with pose landmarks

## Controls

- `q` - Quit
- `r` - Toggle recording
- `s` - Save session data
- `c` - Calibrate robot
- `t` - Toggle robot tracking
- `space` - Emergency stop

## System Requirements

- NVIDIA Jetson Orin AGX with JetPack 6.2
- USB/CSI camera
- igus Rebel robot on same network
- Python 3.8+

## File Structure

- `igus_rebel_pose_tracking.py` - Main pose tracking system
- `example_pose_tracking.py` - Example with gesture recognition
- `pose_tracking_config.json` - Configuration settings
- `install_pose_tracking.sh` - Automated installation
- `test_pose_tracking.py` - System validation
- `requirements.txt` - Python dependencies

## Safety

- Joint limit checking
- Confidence thresholds
- Emergency stop (spacebar)
- Collision detection boundaries
- Smooth motion interpolation

For complete setup instructions, see the main README.md file.