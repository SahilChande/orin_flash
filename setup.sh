#!/bin/bash
set -e

source "./scripts/utils.sh"
source "./scripts/pre_flash_orin.sh"

cd ${HOME}/nvidia-jetson/Linux_for_Tegra

log "Checking USB connection..."
lsusb | grep -i nvidia || log "Jetson not detected. Make sure it's in Force Recovery mode."

log "Flashing AGX Orin..."
chmod +x flash_agx_orin_maxn_nvme.sh
./flash_agx_orin_maxn_nvme.sh

log "Flashing complete. Now switch to Jetson Orin for post-flash configuration."
