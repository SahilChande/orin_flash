## 6.2
(as we are flashing orin AGX via CLI we do not need Nvidia SDKManager for installation)

_**prerequisite:**_
Host PC with ubuntu 22.04 good internet connection, usb 2.0 cable 

1. Download Jetson Firmware from Auvidia (https://auvidea.eu/firmware/)
X230D, X231, X230 (45KB) firmware for Jetpack 6.2

2. go to the downloads folder and open terminal

```bash
cd ~/Downloads
tar -xvf Jetpack_6_2_AGX_Orin_v1.tar.xz
tar -xvf kernel_out.tar.xz
```

3. Download some required files from nvidia
```bash
wget https://developer.nvidia.com/downloads/embedded/l4t/r36_release_v4.3/release/Jetson_Linux_r36.4.3_aarch64.tbz2
wget https://developer.nvidia.com/downloads/embedded/l4t/r36_release_v4.3/release/Tegra_Linux_Sample-Root-Filesystem_r36.4.3_aarch64.tbz2
```

4. Extract content into another directory
```bash
mkdir -p ${HOME}/nvidia-jetson
tar xf Jetson_Linux_r36.4.3_aarch64.tbz2 -C ${HOME}/nvidia-jetson/
sudo tar xpf Tegra_Linux_Sample-Root-Filesystem_r36.4.3_aarch64.tbz2 -C ${HOME}/nvidia-jetson/Linux_for_Tegra/rootfs
```

5. Apply Binaries and Flash Prerequisites
```bash
cd ${HOME}/nvidia-jetson/Linux_for_Tegra
sudo ./apply_binaries.sh
sudo ./tools/l4t_flash_prerequisites.sh
```

6. copy the Auvidea Kernels

A. Copy all scripts and individual files from kernel_out folder and paste it to Linux_for_Tegra folder along with other scripts and files

B. ~/Downloads/kernel_out/kernel/dtb
copy all .dtb files inside dtb folder and paste it in the reciprocal folder in Linux_for_Tegra folder with other .dtb files 

C. ~/Downloads/kernel_out/bootloader/generic/BCT
 copy all the files inside this folder and paste it to reciprocal folder in Linux_for_Tegra folder with other files


7. Flashing the orin

* Connect a USB 2 micro-USB cable to the Jetson before powering it up

* After connecting to the host PC, power up your Jetson. This will put the system in to flashing mode (also called force recovery mode) with a connected Host PC. In some cases, you will have to manually press the force recovery mode button or short pins to enter force recovery mode. For example, with the JN30D you will need to short Pins 7 & 8 of J32 to enter force recovery. A simple way is to use tweezers or jumpers. Please see the Technical Reference Manual for a detailed pin description.

* Check that the connection is established with the lsusb command. You should find one entry with Nvidia Corp.
```bash
lsusb | grep -i nvidia
```
8. Go to flashing folder
```bash
cd ${HOME}/nvidia-jetson/Linux_for_Tegra/
```
9. Flash NVMe SSD with "MAXN" Power Mode
```bash
chmod +x flash_agx_orin_maxn_nvme.sh
./flash_agx_orin_maxn_nvme.sh
```
This will take some time depending on the PC, (around 10-20 minutes)
when you see success message in terminal then we can say the setup is successful.
Now we have to activate all the packages which are provided with 6.2 version on orin.

Now power off the orin.
remove usb from orin and host PC.
Add mouse and keyboard to orin. LAN cable , HDMI cable for display.
After all the required cables attach now we can power on the orin with power cable.

After that we wait to orin to boot and install setup.

10. Complete the OEM setup on orin 
(just follow setup instruction which are popup on screen)

11. Open terminal in home directory
```bash
sudo apt update
sudo apt upgrade -Y
```

12. install python
```bash
sudo apt install python3-pip
```
13. install json-stats 
```bash
sudo pip3 install -U jetson-stats
```
(ignore the warning at end.)

14. install nvidia-jetpack
```bash
sudo apt install nvidia-jetpack
```
(this process will take 10 minutes)

15. first check the cuda location is correct
```bash
ls /usr/local/ | grep cuda
```
here you will see cuda and cuda-12.6

16. update .bashrc
go to .bashrc folder and here we have to set the path for out CUDA , so we can use nvcc from terminal and CUDA is discoverable all the time.

Manually add following lines at the end of .bashrc file ('ctrl + h' to see hidden foolders inclusing .bashrc in home directory)
```bash
export PATH=/usr/local/cuda-12.6/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.6/lib64:$LD_LIBRARY_PATH
```
17. reboot orin to apply changes.
```bash
sudo reboot
```
Setup complete with all required libraries and CUDA

## igus Rebel Pose Tracking Setup

After completing the basic Jetson Orin setup above, you can install the igus Rebel pose tracking system:

### Prerequisites for Pose Tracking
- Completed Jetson Orin AGX setup (steps 1-17 above)
- USB camera or CSI camera connected to Jetson
- igus Rebel robot connected to the same network
- Python 3.8 or higher (already installed in step 12)

### Installation

18. Install the pose tracking system
```bash
cd ~/
git clone https://github.com/SahilChande/orin_flash.git
cd orin_flash
./install_pose_tracking.sh
```

This script will:
- Install required Python packages (OpenCV, MediaPipe, etc.)
- Create a virtual environment
- Configure CUDA paths for GPU acceleration
- Set up camera access
- Create launch scripts

### Configuration

19. Configure the robot connection
```bash
nano pose_tracking_config.json
```

Update the robot IP address and other settings:
```json
{
  "robot_ip": "192.168.1.100",
  "robot_port": 3920,
  "camera_index": 0
}
```

### Usage

20. Launch the pose tracking system
```bash
# Run the example with gesture recognition
./launch_pose_tracking.sh example

# Or run the main pose tracking system
./launch_pose_tracking.sh
```

### Controls
- **'q'** - Quit the application
- **'r'** - Toggle recording of pose data
- **'s'** - Save current session data
- **'c'** - Calibrate robot to current pose
- **'t'** - Toggle robot tracking mode
- **'space'** - Emergency stop

### Features
- **Real-time pose detection** using MediaPipe with GPU acceleration
- **Gesture recognition** (wave, point, stop gestures)
- **Robot communication** via TCP/IP to igus Rebel
- **Pose-to-robot mapping** with safety constraints
- **Data recording** and session playback
- **Visualization** with pose landmarks overlay

### Safety Features
- Joint limit checking
- Confidence thresholds for pose tracking
- Emergency stop functionality
- Collision detection boundaries
- Smooth motion interpolation

### Troubleshooting

**Camera not detected:**
```bash
# Check available cameras
ls /dev/video*

# Test camera manually
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera:', cap.isOpened()); cap.release()"
```

**Robot connection issues:**
```bash
# Check network connectivity
ping 192.168.1.100

# Verify robot IP and port in config file
cat pose_tracking_config.json | grep -E "(robot_ip|robot_port)"
```

**CUDA acceleration not working:**
```bash
# Check CUDA installation
nvcc --version

# Verify GPU availability in Python
python3 -c "import cv2; print('CUDA devices:', cv2.cuda.getCudaEnabledDeviceCount())"
```

### Advanced Usage

**Custom gesture recognition:**
Edit `example_pose_tracking.py` to add your own gesture detection functions.

**Robot calibration:**
Use the 'c' key during operation to calibrate the robot's current pose as the reference position.

**Data analysis:**
Session data is saved in JSON format and can be analyzed with:
```bash
python3 -c "
import json
with open('pose_tracking_session_YYYYMMDD_HHMMSS.json', 'r') as f:
    data = json.load(f)
    print(f'Session duration: {len(data[\"detected_poses\"])} frames')
    print(f'Robot poses recorded: {len(data[\"robot_poses\"])} poses')
"
```