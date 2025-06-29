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