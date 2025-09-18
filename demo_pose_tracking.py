#!/usr/bin/env python3
"""
Demo script showing the igus Rebel pose tracking workflow
=========================================================

This script demonstrates the logical flow of the pose tracking system
without requiring camera or robot hardware. Useful for understanding
the system architecture and testing the workflow.
"""

import time
import json
import random
import math
from typing import List, Tuple

class MockPoseDetector:
    """Mock pose detector for demonstration"""
    
    def __init__(self):
        self.frame_count = 0
    
    def detect_pose(self, frame_data=None):
        """Simulate pose detection with realistic human pose landmarks"""
        self.frame_count += 1
        
        # Simulate occasional pose detection failures
        if random.random() < 0.1:
            return None
        
        # Generate mock landmarks for key body points
        # Using normalized coordinates (0-1)
        base_time = time.time()
        wave_motion = math.sin(base_time * 2)  # 2 Hz wave for arm movement
        
        landmarks = {
            'left_shoulder': (0.3 + wave_motion * 0.05, 0.3, 0.0),
            'right_shoulder': (0.7 - wave_motion * 0.05, 0.3, 0.0),
            'left_elbow': (0.25 + wave_motion * 0.1, 0.45, 0.0),
            'right_elbow': (0.75 - wave_motion * 0.1, 0.45, 0.0),
            'left_wrist': (0.2 + wave_motion * 0.15, 0.6, 0.0),
            'right_wrist': (0.8 - wave_motion * 0.15, 0.6, 0.0),
        }
        
        confidence = 0.7 + random.random() * 0.3  # 0.7 to 1.0
        
        return {
            'timestamp': time.time(),
            'landmarks': landmarks,
            'confidence': confidence,
            'frame_number': self.frame_count
        }

class MockRobotCommunicator:
    """Mock robot communicator for demonstration"""
    
    def __init__(self, robot_ip="192.168.1.100"):
        self.robot_ip = robot_ip
        self.connected = False
        self.current_joints = [0.0] * 6  # 6 joint angles
        self.target_joints = [0.0] * 6
        
    def connect(self):
        """Simulate robot connection"""
        print(f"Connecting to igus Rebel at {self.robot_ip}...")
        time.sleep(1)  # Simulate connection delay
        
        # Simulate connection success/failure
        if random.random() > 0.2:  # 80% success rate
            self.connected = True
            print("✓ Connected to robot")
            return True
        else:
            print("✗ Failed to connect to robot")
            return False
    
    def get_current_pose(self):
        """Get current robot joint angles"""
        if not self.connected:
            return None
        
        # Simulate gradual movement toward target
        for i in range(6):
            diff = self.target_joints[i] - self.current_joints[i]
            self.current_joints[i] += diff * 0.1  # 10% movement per step
        
        return {
            'timestamp': time.time(),
            'joint_angles': self.current_joints.copy(),
            'end_effector_position': (0.5, 0.3, 0.4),  # Example position
            'confidence': 1.0
        }
    
    def move_to_pose(self, target_joints):
        """Command robot to move to target pose"""
        if not self.connected:
            return False
        
        # Apply safety limits
        joint_limits = [(-180, 180), (-90, 90), (-180, 180), 
                       (-90, 90), (-90, 90), (-180, 180)]
        
        safe_joints = []
        for i, (joint_val, (min_val, max_val)) in enumerate(zip(target_joints, joint_limits)):
            safe_joints.append(max(min_val, min(max_val, joint_val)))
        
        self.target_joints = safe_joints
        print(f"Moving to pose: {[f'{j:.1f}°' for j in safe_joints]}")
        return True
    
    def disconnect(self):
        """Disconnect from robot"""
        self.connected = False
        print("Disconnected from robot")

class PoseTrackingDemo:
    """Demonstration of the pose tracking workflow"""
    
    def __init__(self):
        self.pose_detector = MockPoseDetector()
        self.robot_communicator = MockRobotCommunicator()
        self.pose_history = []
        self.running = False
        
        # Load configuration
        try:
            with open('pose_tracking_config.json', 'r') as f:
                self.config = json.load(f)
                print(f"✓ Loaded configuration: Robot IP {self.config['robot_ip']}")
        except FileNotFoundError:
            self.config = {'robot_ip': '192.168.1.100'}
            print("⚠ Using default configuration")
    
    def pose_to_robot_angles(self, landmarks):
        """Convert pose landmarks to robot joint angles"""
        if not landmarks:
            return [0.0] * 6
        
        # Get key positions
        left_shoulder = landmarks.get('left_shoulder', (0.3, 0.3, 0.0))
        right_shoulder = landmarks.get('right_shoulder', (0.7, 0.3, 0.0))
        left_wrist = landmarks.get('left_wrist', (0.2, 0.6, 0.0))
        right_wrist = landmarks.get('right_wrist', (0.8, 0.6, 0.0))
        
        # Simple mapping (this would be more sophisticated in real implementation)
        joint1 = (right_wrist[0] - 0.5) * 90  # Base rotation
        joint2 = (0.5 - right_wrist[1]) * 60  # Shoulder elevation
        joint3 = (right_shoulder[1] - right_wrist[1]) * 100  # Elbow angle
        joint4 = (right_wrist[0] - right_shoulder[0]) * 45  # Wrist rotation
        joint5 = 0.0  # Wrist pitch
        joint6 = 0.0  # End effector rotation
        
        return [joint1, joint2, joint3, joint4, joint5, joint6]
    
    def detect_gesture(self, landmarks):
        """Simple gesture detection"""
        if not landmarks:
            return None
        
        right_wrist = landmarks.get('right_wrist', (0.8, 0.6, 0.0))
        right_shoulder = landmarks.get('right_shoulder', (0.7, 0.3, 0.0))
        
        # Wave gesture: hand raised above shoulder
        if right_wrist[1] < right_shoulder[1] - 0.1:
            return "wave"
        
        # Point gesture: hand extended forward
        if right_wrist[0] > 0.85:
            return "point"
        
        return None
    
    def run_demo(self, duration=30):
        """Run the pose tracking demonstration"""
        print("\n" + "="*50)
        print("igus Rebel Pose Tracking Demo")
        print("="*50)
        print(f"Running for {duration} seconds...")
        print("Press Ctrl+C to stop early")
        print()
        
        # Connect to robot
        robot_connected = self.robot_communicator.connect()
        
        start_time = time.time()
        self.running = True
        frame_count = 0
        gesture_count = {'wave': 0, 'point': 0}
        
        try:
            while self.running and (time.time() - start_time) < duration:
                frame_count += 1
                
                # Simulate camera frame processing
                detected_pose = self.pose_detector.detect_pose()
                
                if detected_pose:
                    self.pose_history.append(detected_pose)
                    
                    # Detect gestures
                    gesture = self.detect_gesture(detected_pose['landmarks'])
                    if gesture:
                        gesture_count[gesture] += 1
                        print(f"Frame {frame_count:3d}: Detected '{gesture}' gesture!")
                    
                    # Robot control
                    if robot_connected and frame_count % 10 == 0:  # Update every 10 frames
                        robot_joints = self.pose_to_robot_angles(detected_pose['landmarks'])
                        self.robot_communicator.move_to_pose(robot_joints)
                        
                        # Get robot feedback
                        robot_pose = self.robot_communicator.get_current_pose()
                        if robot_pose:
                            print(f"Frame {frame_count:3d}: Robot position updated")
                
                else:
                    print(f"Frame {frame_count:3d}: No pose detected")
                
                # Show progress every 5 seconds
                elapsed = time.time() - start_time
                if frame_count % 150 == 0:  # Approximately every 5 seconds at 30 FPS
                    print(f"\nProgress: {elapsed:.1f}s elapsed, {len(self.pose_history)} poses detected")
                    print(f"Gestures: {gesture_count['wave']} waves, {gesture_count['point']} points")
                
                # Simulate 30 FPS
                time.sleep(1/30)
                
        except KeyboardInterrupt:
            print("\nDemo stopped by user")
        
        # Cleanup
        if robot_connected:
            self.robot_communicator.disconnect()
        
        # Results summary
        elapsed = time.time() - start_time
        print(f"\n" + "="*50)
        print("Demo Complete!")
        print("="*50)
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Frames processed: {frame_count}")
        print(f"Poses detected: {len(self.pose_history)}")
        print(f"Detection rate: {len(self.pose_history)/frame_count*100:.1f}%")
        print(f"Gestures detected: {sum(gesture_count.values())}")
        print(f"  - Wave gestures: {gesture_count['wave']}")
        print(f"  - Point gestures: {gesture_count['point']}")
        print(f"Robot connected: {'Yes' if robot_connected else 'No'}")
        
        # Save demo data
        demo_data = {
            'duration': elapsed,
            'frames_processed': frame_count,
            'poses_detected': len(self.pose_history),
            'gestures': gesture_count,
            'robot_connected': robot_connected,
            'pose_history': self.pose_history[-10:]  # Last 10 poses
        }
        
        filename = f"demo_session_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(demo_data, f, indent=2)
        
        print(f"Demo data saved to: {filename}")
        return True

def main():
    """Main function"""
    print("igus Rebel Pose Tracking - System Demo")
    print("This demo simulates the pose tracking workflow without requiring hardware")
    print()
    
    demo = PoseTrackingDemo()
    
    try:
        duration = 15  # Default 15 seconds
        if len(sys.argv) > 1:
            duration = int(sys.argv[1])
        
        demo.run_demo(duration)
        
    except Exception as e:
        print(f"Demo error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    exit(main())