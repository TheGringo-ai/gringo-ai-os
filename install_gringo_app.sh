#!/bin/bash

# GRINGO AI OS - Easy Installation Script
# This creates a proper macOS app with your company logo as the icon

echo "🚀 Installing GRINGO AI OS with your company logo as the app icon..."

# Check if logo exists
if [ ! -f "assets/company_logo.png" ]; then
    echo "❌ Company logo not found at assets/company_logo.png"
    echo "Please ensure your logo file is in the correct location."
    exit 1
fi

# Create the app bundle with your logo
./create_app_bundle.sh

# Check if app was created successfully
if [ -d "GRINGO AI OS.app" ]; then
    echo "✅ GRINGO AI OS app created successfully!"
    echo ""
    echo "📱 Your company logo is now the app icon"
    echo "🖥️  The app interface remains clean and professional"
    echo ""
    echo "To install:"
    echo "1. Drag 'GRINGO AI OS.app' to your Applications folder"
    echo "2. Click the app icon (your company logo) to launch"
    echo ""
    echo "Or double-click the app now to test it:"
    open "GRINGO AI OS.app"
else
    echo "❌ Failed to create app bundle"
    echo "Please check the create_app_bundle.sh script"
fi
