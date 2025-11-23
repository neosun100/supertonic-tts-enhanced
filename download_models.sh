#!/bin/bash

# Supertonic Model Download Script
# This script downloads the ONNX models and preset voices from Hugging Face

set -e  # Exit on error

echo "=========================================="
echo "Supertonic Model Download Script"
echo "=========================================="

# Check if git-lfs is installed
if ! command -v git-lfs &> /dev/null; then
    echo "Error: git-lfs is not installed."
    echo "Please install it first:"
    echo "  Ubuntu/Debian: sudo apt-get install git-lfs"
    echo "  macOS: brew install git-lfs"
    echo "  Then run: git lfs install"
    exit 1
fi

# Initialize git-lfs if not already done
echo "Initializing git-lfs..."
git lfs install

# Check if assets directory already exists
if [ -d "assets" ]; then
    echo "Warning: assets directory already exists."
    read -p "Do you want to remove it and re-download? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing assets directory..."
        rm -rf assets
    else
        echo "Keeping existing assets. Exiting..."
        exit 0
    fi
fi

# Download models from Hugging Face
echo "Downloading models from Hugging Face..."
echo "This may take a while depending on your internet connection..."

git clone https://huggingface.co/Supertone/supertonic assets

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Models downloaded successfully!"
    echo "=========================================="
    echo ""
    echo "Downloaded files are in the 'assets' directory:"
    ls -lh assets/
    echo ""
    echo "You can now run the Docker container."
else
    echo ""
    echo "=========================================="
    echo "❌ Failed to download models."
    echo "=========================================="
    echo ""
    echo "Please check your internet connection and try again."
    exit 1
fi
