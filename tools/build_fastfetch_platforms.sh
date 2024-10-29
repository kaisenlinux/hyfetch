#!/bin/bash

set -e

# Path to store extracted binaries
output_dir="dist/binaries"

# Ensure output directory exists
mkdir -p "$output_dir"

build_platform() {
    container=$1
    platform=$2

    echo "Running build in $container for $platform"

    # Create a unique name for the container instance
    container_name="build_$platform"

    # Run the build script inside the Docker container
    docker run -it --name "$container_name" -v "$PWD/tools:/tools" -w "/w" "$container" bash /tools/build_fastfetch.sh

    # Extract binaries or packages produced by the build
    # Assuming binaries are in a specific directory, e.g., ./dist
    if docker cp "$container_name:/w/dist" "$output_dir/$platform"; then
        echo "Successfully extracted binaries for $platform"
    else
        echo "Failed to extract binaries for $platform"
    fi

    # Cleanup: Remove the container after the build
    docker rm "$container_name"
}

# Build for different platforms
build_platform "amd64/debian:10-slim" "manylinux_2_28_x86_64"
# build_platform "arm64v8/debian:10-slim" "manylinux_2_28_aaarch64"
# build_platform "arm32v7/debian:10-slim" "manylinux_2_28_armv7l"
# build_platform "riscv64/debian:sid-slim" "manylinux_2_37_riscv64"

echo "Build and extraction process completed."
