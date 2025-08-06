#!/bin/bash

# GRINGO AI OS - macOS App Bundle Creator
# Creates a proper macOS application with your logo

echo "🛠️ Creating GRINGO AI OS App Bundle..."

# Create app bundle structure
APP_NAME="GRINGO AI OS"
APP_DIR="$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Clean up existing bundle
rm -rf "$APP_DIR"

# Create directories
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>gringo_launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.gringo.ai-os</string>
    <key>CFBundleName</key>
    <string>GRINGO AI OS</string>
    <key>CFBundleDisplayName</key>
    <string>GRINGO AI OS</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>GRNG</string>
    <key>CFBundleIconFile</key>
    <string>company_icon</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
</dict>
</plist>
EOF

# Create launcher script
cat > "$MACOS_DIR/gringo_launcher" << 'EOF'
#!/bin/bash
# Get the directory of this script (inside the app bundle)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$(dirname "$(dirname "$DIR")")"
PROJECT_DIR="$(dirname "$APP_DIR")"

# Change to project directory and run launcher
cd "$PROJECT_DIR"
python3 gringo_launcher.py
EOF

# Make launcher executable
chmod +x "$MACOS_DIR/gringo_launcher"

# Copy your logo (you'll need to save your logo as gringo_icon.icns in the Resources folder)
echo "📁 App bundle structure created!"
echo "📋 Next steps:"
echo "1. Save your logo image as 'gringo_icon.icns' in: $RESOURCES_DIR/"
echo "2. Or save as PNG and we'll convert it: $RESOURCES_DIR/gringo_icon.png"
echo "3. Double-click '$APP_DIR' to launch GRINGO AI OS"

# Create instructions for logo conversion
cat > "convert_logo.sh" << 'EOF'
#!/bin/bash
# Convert PNG logo to macOS icon format

if [ -f "assets/company_logo.png" ]; then
    echo "🎨 Converting company logo to macOS icon format..."
    
    # Create iconset directory
    mkdir -p company_icon.iconset
    
    # Generate different sizes from your company logo
    sips -z 16 16 assets/company_logo.png --out company_icon.iconset/icon_16x16.png
    sips -z 32 32 assets/company_logo.png --out company_icon.iconset/icon_16x16@2x.png
    sips -z 32 32 assets/company_logo.png --out company_icon.iconset/icon_32x32.png
    sips -z 64 64 assets/company_logo.png --out company_icon.iconset/icon_32x32@2x.png
    sips -z 128 128 assets/company_logo.png --out company_icon.iconset/icon_128x128.png
    sips -z 256 256 assets/company_logo.png --out company_icon.iconset/icon_128x128@2x.png
    sips -z 256 256 assets/company_logo.png --out company_icon.iconset/icon_256x256.png
    sips -z 512 512 assets/company_logo.png --out company_icon.iconset/icon_256x256@2x.png
    sips -z 512 512 assets/company_logo.png --out company_icon.iconset/icon_512x512.png
    sips -z 1024 1024 assets/company_logo.png --out company_icon.iconset/icon_512x512@2x.png
    
    # Convert to icns
    iconutil -c icns company_icon.iconset
    
    # Copy to app bundle
    cp company_icon.icns "GRINGO AI OS.app/Contents/Resources/"
    
    # Clean up
    rm -rf company_icon.iconset
    
    echo "✅ Icon created and installed!"
else
    echo "❌ Please save your logo as 'assets/company_logo.png' first"
fi
EOF

chmod +x convert_logo.sh

echo ""
echo "🎨 Logo Integration Instructions:"
echo "1. Save your logo image as: assets/company_logo.png"
echo "2. Run: ./convert_logo.sh"
echo "3. Launch: open 'GRINGO AI OS.app'"
echo ""
echo "✅ GRINGO AI OS app bundle created successfully!"
