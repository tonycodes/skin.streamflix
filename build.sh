#!/bin/bash
# Build script for StreamFlix Kodi Skin

VERSION="1.0.3"
SKIN_NAME="skin.streamflix"

# Navigate to parent directory
cd "$(dirname "$0")/.."

# Create build directory
mkdir -p build

# Create zip file (excluding build artifacts and git files)
# Create both versioned and non-versioned zips
zip -r "build/${SKIN_NAME}-${VERSION}.zip" "${SKIN_NAME}" \
    -x "*.git*" \
    -x "*build.sh" \
    -x "*__pycache__*" \
    -x "*.DS_Store" \
    -x "*repository/*"

# Copy to non-versioned name for "latest" URL
cp "build/${SKIN_NAME}-${VERSION}.zip" "build/${SKIN_NAME}.zip"

# Create repository addon zip
zip -r "build/repository.streamflix-${VERSION}.zip" "repository.streamflix" \
    -x "*.git*" \
    -x "*.DS_Store"

echo ""
echo "Build complete!"
echo "Created: build/${SKIN_NAME}-${VERSION}.zip"
echo "Created: build/repository.streamflix-${VERSION}.zip"
echo ""
echo "To install in Kodi:"
echo "1. Copy ${SKIN_NAME}-${VERSION}.zip to your device"
echo "2. Settings → Add-ons → Install from zip file"
echo "3. Navigate to the zip and install"
