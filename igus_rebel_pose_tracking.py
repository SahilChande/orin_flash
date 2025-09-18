#!/usr/bin/env python3
"""
igus Rebel Pose Tracking System
===============================

A comprehensive pose tracking system for igus Rebel collaborative robot arms
running on NVIDIA Jetson Orin AGX with CUDA acceleration.

This module provides:
- Real-time pose detection using computer vision
- Robot communication interface for igus Rebel
- Pose visualization and logging
- Integration with Jetson Orin's GPU acceleration

Author: Generated for Jetson Orin AGX Setup
License: MIT
"""

import cv2
import numpy as np
import mediapipe as mp
import time
import json
import logging
import threading
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import deque
import socket


@dataclass
class RobotPose:
    """Data class for robot pose information"""
    timestamp: float
    joint_angles: List[float]
    end_effector_position: Tuple[float, float, float]
    end_effector_orientation: Tuple[float, float, float, float]  # quaternion
    confidence: float


@dataclass
class DetectedPose:
    """Data class for detected human pose information"""
    timestamp: float
    landmarks: List[Tuple[float, float, float]]  # x, y, z coordinates
    visibility: List[float]
    confidence: float


class PoseDetector:
    """
    Computer vision-based pose detection using MediaPipe
    Optimized for NVIDIA Jetson Orin AGX with CUDA acceleration
    """
    
    def __init__(self, model_complexity: int = 1, min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize the pose detector
        
        Args:
            model_complexity: Model complexity (0-2), higher = more accurate but slower
            min_detection_confidence: Minimum confidence for pose detection
            min_tracking_confidence: Minimum confidence for pose tracking
        """
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.pose = self.mp_pose.Pose(
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.logger = logging.getLogger(__name__)
        
    def detect_pose(self, image: np.ndarray) -> Optional[DetectedPose]:
        """
        Detect pose in the given image
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            DetectedPose object if pose detected, None otherwise
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.pose.process(rgb_image)
        
        if results.pose_landmarks:
            landmarks = []
            visibility = []
            
            for landmark in results.pose_landmarks.landmark:
                landmarks.append((landmark.x, landmark.y, landmark.z))
                visibility.append(landmark.visibility)
            
            return DetectedPose(
                timestamp=time.time(),
                landmarks=landmarks,
                visibility=visibility,
                confidence=np.mean(visibility)  # Use average visibility as confidence
            )
        
        return None
    
    def draw_pose(self, image: np.ndarray, detected_pose: DetectedPose) -> np.ndarray:
        """
        Draw pose landmarks on the image
        
        Args:
            image: Input image
            detected_pose: Detected pose to draw
            
        Returns:
            Image with pose landmarks drawn
        """
        # Convert back to RGB for MediaPipe drawing
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe landmarks object
        pose_landmarks = self.mp_pose.PoseLandmark
        connections = self.mp_pose.POSE_CONNECTIONS
        
        # Draw the pose landmarks
        self.mp_drawing.draw_landmarks(
            rgb_image,
            results.pose_landmarks if hasattr(self, '_last_results') else None,
            connections,
            self.mp_drawing_styles.get_default_pose_landmarks_style()
        )
        
        # Convert back to BGR
        return cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)


class IgusRebelCommunicator:
    """
    Communication interface for igus Rebel robot
    Handles TCP/IP communication and command protocols
    """
    
    def __init__(self, robot_ip: str = "192.168.1.100", robot_port: int = 3920):
        """
        Initialize robot communicator
        
        Args:
            robot_ip: IP address of the igus Rebel robot
            robot_port: Port number for communication
        """
        self.robot_ip = robot_ip
        self.robot_port = robot_port
        self.socket = None
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """
        Establish connection to the robot
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # 5 second timeout
            self.socket.connect((self.robot_ip, self.robot_port))
            self.connected = True
            self.logger.info(f"Connected to igus Rebel at {self.robot_ip}:{self.robot_port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to robot: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the robot"""
        if self.socket:
            self.socket.close()
            self.connected = False
            self.logger.info("Disconnected from robot")
    
    def get_current_pose(self) -> Optional[RobotPose]:
        """
        Get current robot pose
        
        Returns:
            RobotPose object if successful, None otherwise
        """
        if not self.connected:
            return None
            
        try:
            # Send command to get current pose
            command = b"GET_POSE\n"
            self.socket.send(command)
            
            # Receive response
            response = self.socket.recv(1024).decode('utf-8')
            
            # Parse response (format: joint1,joint2,joint3,joint4,joint5,joint6,x,y,z,qw,qx,qy,qz)
            values = [float(x) for x in response.strip().split(',')]
            
            if len(values) >= 13:
                return RobotPose(
                    timestamp=time.time(),
                    joint_angles=values[:6],
                    end_effector_position=tuple(values[6:9]),
                    end_effector_orientation=tuple(values[9:13]),
                    confidence=1.0
                )
        except Exception as e:
            self.logger.error(f"Failed to get robot pose: {e}")
            
        return None
    
    def move_to_pose(self, target_pose: RobotPose) -> bool:
        """
        Move robot to target pose
        
        Args:
            target_pose: Target pose to move to
            
        Returns:
            True if command sent successfully, False otherwise
        """
        if not self.connected:
            return False
            
        try:
            # Format command
            joint_str = ','.join([str(angle) for angle in target_pose.joint_angles])
            command = f"MOVE_JOINTS {joint_str}\n".encode('utf-8')
            
            self.socket.send(command)
            self.logger.info(f"Sent move command: {joint_str}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send move command: {e}")
            return False


class PoseTrackingSystem:
    """
    Main pose tracking system that coordinates detection, robot communication, and visualization
    """
    
    def __init__(self, config_file: str = "pose_tracking_config.json"):
        """
        Initialize the pose tracking system
        
        Args:
            config_file: Path to configuration file
        """
        self.config = self._load_config(config_file)
        
        # Initialize components
        self.pose_detector = PoseDetector(
            model_complexity=self.config.get('model_complexity', 1),
            min_detection_confidence=self.config.get('min_detection_confidence', 0.5),
            min_tracking_confidence=self.config.get('min_tracking_confidence', 0.5)
        )
        
        self.robot_communicator = IgusRebelCommunicator(
            robot_ip=self.config.get('robot_ip', '192.168.1.100'),
            robot_port=self.config.get('robot_port', 3920)
        )
        
        # Data storage
        self.pose_history = deque(maxlen=self.config.get('history_length', 1000))
        self.robot_pose_history = deque(maxlen=self.config.get('history_length', 1000))
        
        # Camera setup
        self.camera = None
        self.camera_index = self.config.get('camera_index', 0)
        
        # Control flags
        self.running = False
        self.recording = False
        
        # Setup logging
        self._setup_logging()
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_file} not found, using defaults")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing config file: {e}")
            return {}
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=self.config.get('log_level', 'INFO'),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pose_tracking.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_camera(self) -> bool:
        """
        Initialize camera for pose detection
        
        Returns:
            True if camera initialized successfully, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties for optimal performance on Jetson
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.get('camera_width', 640))
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.get('camera_height', 480))
            self.camera.set(cv2.CAP_PROP_FPS, self.config.get('camera_fps', 30))
            
            if not self.camera.isOpened():
                raise RuntimeError("Failed to open camera")
                
            self.logger.info(f"Camera initialized: {self.camera_index}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def start_tracking(self):
        """Start the pose tracking system"""
        if not self.initialize_camera():
            return False
            
        if not self.robot_communicator.connect():
            self.logger.warning("Failed to connect to robot, continuing without robot control")
        
        self.running = True
        self.logger.info("Starting pose tracking system")
        
        try:
            while self.running:
                ret, frame = self.camera.read()
                if not ret:
                    self.logger.error("Failed to read camera frame")
                    break
                
                # Detect pose
                detected_pose = self.pose_detector.detect_pose(frame)
                if detected_pose:
                    self.pose_history.append(detected_pose)
                    
                    # Draw pose on frame
                    frame_with_pose = self.pose_detector.draw_pose(frame, detected_pose)
                else:
                    frame_with_pose = frame
                
                # Get robot pose if connected
                if self.robot_communicator.connected:
                    robot_pose = self.robot_communicator.get_current_pose()
                    if robot_pose:
                        self.robot_pose_history.append(robot_pose)
                
                # Display frame
                cv2.imshow('igus Rebel Pose Tracking', frame_with_pose)
                
                # Check for key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.recording = not self.recording
                    self.logger.info(f"Recording: {'ON' if self.recording else 'OFF'}")
                elif key == ord('s'):
                    self.save_session_data()
                
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            self.stop_tracking()
    
    def stop_tracking(self):
        """Stop the pose tracking system"""
        self.running = False
        
        if self.camera:
            self.camera.release()
        
        cv2.destroyAllWindows()
        self.robot_communicator.disconnect()
        self.logger.info("Pose tracking system stopped")
    
    def save_session_data(self, filename: Optional[str] = None):
        """
        Save session data to file
        
        Args:
            filename: Output filename, auto-generated if None
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"pose_tracking_session_{timestamp}.json"
        
        session_data = {
            'timestamp': time.time(),
            'config': self.config,
            'detected_poses': [
                {
                    'timestamp': pose.timestamp,
                    'landmarks': pose.landmarks,
                    'visibility': pose.visibility,
                    'confidence': pose.confidence
                }
                for pose in self.pose_history
            ],
            'robot_poses': [
                {
                    'timestamp': pose.timestamp,
                    'joint_angles': pose.joint_angles,
                    'end_effector_position': pose.end_effector_position,
                    'end_effector_orientation': pose.end_effector_orientation,
                    'confidence': pose.confidence
                }
                for pose in self.robot_pose_history
            ]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(session_data, f, indent=2)
            self.logger.info(f"Session data saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")


def main():
    """Main function to run the pose tracking system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='igus Rebel Pose Tracking System')
    parser.add_argument('--config', '-c', default='pose_tracking_config.json',
                        help='Configuration file path')
    parser.add_argument('--camera', type=int, default=0,
                        help='Camera index')
    parser.add_argument('--robot-ip', default='192.168.1.100',
                        help='Robot IP address')
    
    args = parser.parse_args()
    
    # Create pose tracking system
    system = PoseTrackingSystem(config_file=args.config)
    
    # Override config with command line arguments
    system.config['camera_index'] = args.camera
    system.config['robot_ip'] = args.robot_ip
    
    print("igus Rebel Pose Tracking System")
    print("================================")
    print("Controls:")
    print("  'q' - Quit")
    print("  'r' - Toggle recording")
    print("  's' - Save session data")
    print()
    
    try:
        system.start_tracking()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())