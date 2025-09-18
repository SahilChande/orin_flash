#!/usr/bin/env python3
"""
Example usage of the igus Rebel Pose Tracking System
====================================================

This script demonstrates basic usage of the pose tracking system
for controlling an igus Rebel robot based on human pose detection.

Usage:
    python3 example_pose_tracking.py
    
Controls:
    'q' - Quit the application
    'r' - Toggle recording of pose data
    's' - Save current session data
    'c' - Calibrate robot to current pose
    't' - Toggle robot tracking mode
"""

import sys
import os
import time
import numpy as np

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from igus_rebel_pose_tracking import PoseTrackingSystem, RobotPose
import cv2
import logging


class ExamplePoseTracker:
    """
    Example implementation showing how to use the pose tracking system
    for specific applications like gesture control or pose mirroring
    """
    
    def __init__(self):
        """Initialize the example tracker"""
        self.system = PoseTrackingSystem()
        self.tracking_enabled = False
        self.calibration_pose = None
        self.logger = logging.getLogger(__name__)
        
        # Example gesture definitions
        self.gestures = {
            'wave': self._detect_wave_gesture,
            'point': self._detect_point_gesture,
            'stop': self._detect_stop_gesture
        }
        
    def _detect_wave_gesture(self, pose_landmarks) -> bool:
        """
        Detect a waving gesture
        
        Args:
            pose_landmarks: List of pose landmarks
            
        Returns:
            True if wave gesture detected
        """
        if not pose_landmarks or len(pose_landmarks) < 16:
            return False
            
        # Get right wrist and elbow positions
        right_wrist = pose_landmarks[16]  # RIGHT_WRIST
        right_elbow = pose_landmarks[14]  # RIGHT_ELBOW
        
        # Simple wave detection: wrist higher than elbow
        return right_wrist[1] < right_elbow[1]  # y-coordinate decreases upward
    
    def _detect_point_gesture(self, pose_landmarks) -> bool:
        """
        Detect a pointing gesture
        
        Args:
            pose_landmarks: List of pose landmarks
            
        Returns:
            True if pointing gesture detected
        """
        if not pose_landmarks or len(pose_landmarks) < 16:
            return False
            
        # Get arm positions
        right_shoulder = pose_landmarks[12]  # RIGHT_SHOULDER
        right_elbow = pose_landmarks[14]    # RIGHT_ELBOW
        right_wrist = pose_landmarks[16]    # RIGHT_WRIST
        
        # Check if arm is extended (roughly straight)
        shoulder_to_elbow = np.array(right_elbow[:2]) - np.array(right_shoulder[:2])
        elbow_to_wrist = np.array(right_wrist[:2]) - np.array(right_elbow[:2])
        
        # Calculate angle between arm segments
        dot_product = np.dot(shoulder_to_elbow, elbow_to_wrist)
        magnitude1 = np.linalg.norm(shoulder_to_elbow)
        magnitude2 = np.linalg.norm(elbow_to_wrist)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return False
            
        angle = np.arccos(np.clip(dot_product / (magnitude1 * magnitude2), -1.0, 1.0))
        
        # If angle is close to 180 degrees (straight arm), it's pointing
        return abs(angle - np.pi) < 0.3  # ~17 degrees tolerance
    
    def _detect_stop_gesture(self, pose_landmarks) -> bool:
        """
        Detect a stop gesture (hand up like a stop sign)
        
        Args:
            pose_landmarks: List of pose landmarks
            
        Returns:
            True if stop gesture detected
        """
        if not pose_landmarks or len(pose_landmarks) < 16:
            return False
            
        # Get hand and shoulder positions
        right_wrist = pose_landmarks[16]    # RIGHT_WRIST
        right_shoulder = pose_landmarks[12] # RIGHT_SHOULDER
        
        # Hand should be raised above shoulder level
        return right_wrist[1] < right_shoulder[1] - 0.1  # Some threshold
    
    def pose_to_robot_angles(self, pose_landmarks) -> list:
        """
        Convert human pose to robot joint angles
        This is a simplified mapping - real applications would need
        more sophisticated inverse kinematics
        
        Args:
            pose_landmarks: List of pose landmarks
            
        Returns:
            List of joint angles for the robot
        """
        if not pose_landmarks or len(pose_landmarks) < 16:
            return [0.0] * 6  # Return neutral pose
        
        # Get key landmarks
        right_shoulder = pose_landmarks[12]
        right_elbow = pose_landmarks[14]
        right_wrist = pose_landmarks[16]
        
        # Simple mapping (this is very basic and would need refinement)
        # Map arm position to robot joints
        
        # Joint 1 (base rotation) - based on body orientation
        joint1 = (right_shoulder[0] - 0.5) * 180  # -90 to +90 degrees
        
        # Joint 2 (shoulder) - based on arm elevation
        shoulder_height = right_shoulder[1]
        joint2 = (0.5 - shoulder_height) * 90  # -45 to +45 degrees
        
        # Joint 3 (elbow) - based on elbow angle
        shoulder_to_elbow = np.array(right_elbow[:2]) - np.array(right_shoulder[:2])
        elbow_to_wrist = np.array(right_wrist[:2]) - np.array(right_elbow[:2])
        
        # Calculate elbow angle
        dot_product = np.dot(shoulder_to_elbow, elbow_to_wrist)
        magnitude1 = np.linalg.norm(shoulder_to_elbow)
        magnitude2 = np.linalg.norm(elbow_to_wrist)
        
        if magnitude1 > 0 and magnitude2 > 0:
            elbow_angle = np.arccos(np.clip(dot_product / (magnitude1 * magnitude2), -1.0, 1.0))
            joint3 = np.degrees(elbow_angle) - 90  # Convert to robot joint space
        else:
            joint3 = 0.0
        
        # Joints 4-6 (wrist and end effector) - simplified
        joint4 = (right_wrist[0] - right_elbow[0]) * 180
        joint5 = (right_wrist[1] - right_elbow[1]) * 180
        joint6 = 0.0  # Keep end effector orientation neutral
        
        # Clamp values to safe ranges
        joints = [joint1, joint2, joint3, joint4, joint5, joint6]
        clamped_joints = []
        
        joint_limits = [
            (-180, 180),  # Joint 1
            (-90, 90),    # Joint 2
            (-180, 180),  # Joint 3
            (-90, 90),    # Joint 4
            (-90, 90),    # Joint 5
            (-180, 180)   # Joint 6
        ]
        
        for i, (joint_val, (min_val, max_val)) in enumerate(zip(joints, joint_limits)):
            clamped_joints.append(max(min_val, min(max_val, joint_val)))
        
        return clamped_joints
    
    def run_example(self):
        """Run the example pose tracking application"""
        print("igus Rebel Pose Tracking Example")
        print("=================================")
        print()
        print("This example demonstrates:")
        print("1. Real-time pose detection")
        print("2. Gesture recognition (wave, point, stop)")
        print("3. Pose-to-robot mapping")
        print("4. Robot control integration")
        print()
        print("Controls:")
        print("  'q' - Quit")
        print("  'r' - Toggle recording")
        print("  's' - Save session data")
        print("  'c' - Calibrate robot pose")
        print("  't' - Toggle robot tracking")
        print("  'space' - Emergency stop")
        print()
        input("Press Enter to start...")
        
        # Initialize the tracking system
        if not self.system.initialize_camera():
            print("Failed to initialize camera!")
            return False
        
        if not self.system.robot_communicator.connect():
            print("Warning: Could not connect to robot. Continuing in simulation mode.")
        
        self.system.running = True
        
        try:
            while self.system.running:
                ret, frame = self.system.camera.read()
                if not ret:
                    print("Failed to read camera frame")
                    break
                
                # Detect pose
                detected_pose = self.system.pose_detector.detect_pose(frame)
                
                if detected_pose:
                    # Store pose in history
                    self.system.pose_history.append(detected_pose)
                    
                    # Check for gestures
                    gestures_detected = []
                    for gesture_name, gesture_func in self.gestures.items():
                        if gesture_func(detected_pose.landmarks):
                            gestures_detected.append(gesture_name)
                    
                    # Display detected gestures
                    if gestures_detected:
                        gesture_text = f"Gestures: {', '.join(gestures_detected)}"
                        cv2.putText(frame, gesture_text, (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Robot tracking mode
                    if self.tracking_enabled and self.system.robot_communicator.connected:
                        # Convert pose to robot angles
                        robot_angles = self.pose_to_robot_angles(detected_pose.landmarks)
                        
                        # Create robot pose command
                        target_pose = RobotPose(
                            timestamp=time.time(),
                            joint_angles=robot_angles,
                            end_effector_position=(0, 0, 0),  # Will be calculated by robot
                            end_effector_orientation=(0, 0, 0, 1),  # Neutral orientation
                            confidence=detected_pose.confidence
                        )
                        
                        # Send to robot (with safety checks)
                        if detected_pose.confidence > 0.7:  # Only track high-confidence poses
                            self.system.robot_communicator.move_to_pose(target_pose)
                    
                    # Draw pose on frame
                    frame_with_pose = self.system.pose_detector.draw_pose(frame, detected_pose)
                else:
                    frame_with_pose = frame
                
                # Add status information
                status_y = frame.shape[0] - 60
                status_text = f"Recording: {'ON' if self.system.recording else 'OFF'}"
                cv2.putText(frame_with_pose, status_text, (10, status_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                tracking_text = f"Robot Tracking: {'ON' if self.tracking_enabled else 'OFF'}"
                cv2.putText(frame_with_pose, tracking_text, (10, status_y + 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display frame
                cv2.imshow('igus Rebel Pose Tracking Example', frame_with_pose)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.system.recording = not self.system.recording
                    print(f"Recording: {'ON' if self.system.recording else 'OFF'}")
                elif key == ord('s'):
                    self.system.save_session_data()
                    print("Session data saved")
                elif key == ord('c'):
                    self.calibrate_robot()
                elif key == ord('t'):
                    self.tracking_enabled = not self.tracking_enabled
                    print(f"Robot tracking: {'ON' if self.tracking_enabled else 'OFF'}")
                elif key == ord(' '):  # Spacebar - emergency stop
                    self.emergency_stop()
                
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            self.system.stop_tracking()
        
        return True
    
    def calibrate_robot(self):
        """Calibrate robot to current pose"""
        if self.system.robot_communicator.connected:
            current_pose = self.system.robot_communicator.get_current_pose()
            if current_pose:
                self.calibration_pose = current_pose
                print(f"Robot calibrated to current pose: {current_pose.joint_angles}")
            else:
                print("Failed to get current robot pose for calibration")
        else:
            print("Robot not connected - cannot calibrate")
    
    def emergency_stop(self):
        """Emergency stop for robot"""
        self.tracking_enabled = False
        print("EMERGENCY STOP - Robot tracking disabled")
        # In a real application, you would send an emergency stop command to the robot


def main():
    """Main function"""
    try:
        example = ExamplePoseTracker()
        return 0 if example.run_example() else 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())