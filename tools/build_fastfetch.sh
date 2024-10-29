#!/usr/bin/env bash
# This script is used to build fastfetch inside a docker container.
# The docker container tested is debian 10.

set -e

# Install required packages
echo "Installing required packages..."
apt-get update
apt-get install --ignore-missing --no-install-recommends --no-install-suggests -y libvulkan-dev libwayland-dev libxrandr-dev libxcb-randr0-dev libdconf-dev libdbus-1-dev libmagickcore-dev libxfconf-0-dev libsqlite3-dev librpm-dev libosmesa6-dev ocl-icd-opencl-dev libnm-dev libpulse-dev libdrm-dev git build-essential cmake imagemagick chafa libchafa-dev ddcutil

# Check if we're on debian 10
apt-get install -y lsb-release
if [ "$(lsb_release -cs)" != "buster" ]; then
    apt-get install --ignore-missing -y libegl-dev libglx-dev directx-headers-dev
# else
    # echo "Backporting pacakges for debian 10"

    # # Add Debian 11 "Bullseye" repository
    echo "deb http://deb.debian.org/debian/ bullseye main" > /etc/apt/sources.list.d/bullseye.list

    # # Set package priorities to prefer Debian 10 (Buster) except for libegl-dev and its dependencies
    # echo 'Package: *
    # Pin: release n=buster
    # Pin-Priority: 900
    
    # Package: libegl-dev
    # Pin: release n=bullseye
    # Pin-Priority: 990' > /etc/apt/preferences.d/priority

    # apt-get update
fi

# Clone repo
echo "Cloning fastfetch..."
git clone "https://github.com/fastfetch-cli/fastfetch"
cd fastfetch

# Checkout the latest release tag
latest_tag=$(git describe --tags "$(git rev-list --tags --max-count=1)")
echo "Checking out latest tag: $latest_tag"
git checkout "$latest_tag"

# Backward compatibility
# cmake 3.13: replace "NAME_WLE" with "NAME_WE"
sed -i 's/NAME_WLE/NAME_WE/g' CMakeLists.txt

# Display system information
echo "System Information:"
uname -a

# Install linuxbrew packages
# echo "Installing Linuxbrew..."
# bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# /home/linuxbrew/.linuxbrew/bin/brew install imagemagick chafa ddcutil --ignore-dependencies

# Configure project
echo "Configuring project..."
export PKG_CONFIG_PATH=/home/linuxbrew/.linuxbrew/lib/pkgconfig:$PKG_CONFIG_PATH
cmake -DSET_TWEAK=Off -DBUILD_TESTS=On -DCMAKE_INSTALL_PREFIX=/usr .

# Build project
echo "Building project..."
cmake --build . --target package -j 32

# List features of fastfetch
echo "Listing features of fastfetch:"
./fastfetch --list-features

# Run fastfetch
echo "Running fastfetch:"
time ./fastfetch -c presets/ci.jsonc

# Run fastfetch with JSON format
echo "Running fastfetch with JSON format:"
time ./fastfetch -c presets/ci.jsonc --format json

# Run flashfetch
echo "Running flashfetch:"
time ./flashfetch

# Print dependencies of fastfetch
echo "Dependencies of fastfetch:"
ldd fastfetch

# Run tests
echo "Running tests..."
ctest