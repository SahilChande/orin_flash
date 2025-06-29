#!/bin/bash
set -e

source "$(dirname "$0")/utils.sh"

log "Creating firmware download directory..."
mkdir -p firmware
cd firmware

log "Downloading NVIDIA files..."
wget -nc https://developer.nvidia.com/downloads/embedded/l4t/r36_release_v4.3/release/Jetson_Linux_r36.4.3_aarch64.tbz2
wget -nc https://developer.nvidia.com/downloads/embedded/l4t/r36_release_v4.3/release/Tegra_Linux_Sample-Root-Filesystem_r36.4.3_aarch64.tbz2

log "Extracting NVIDIA files..."
mkdir -p ${HOME}/nvidia-jetson
tar xf Jetson_Linux_r36.4.3_aarch64.tbz2 -C ${HOME}/nvidia-jetson/
sudo tar xpf Tegra_Linux_Sample-Root-Filesystem_r36.4.3_aarch64.tbz2 -C ${HOME}/nvidia-jetson/Linux_for_Tegra/rootfs

log "Applying binaries..."
cd ${HOME}/nvidia-jetson/Linux_for_Tegra
sudo ./apply_binaries.sh
sudo ./tools/l4t_flash_prerequisites.sh

log "Please manually extract and copy Auvidea kernel_out contents into Linux_for_Tegra folder."
