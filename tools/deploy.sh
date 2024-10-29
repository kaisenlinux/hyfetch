#!/usr/bin/env bash

# Stop on error
set -e

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Run build_pkg
"$DIR/build_pkg.sh"

# Check built files
twine check dist/*
twine upload dist/*
