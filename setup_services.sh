#!/bin/bash
"""
Create macOS Services for GRINGO
Adds right-click context menu options in Finder
"""

echo "🛠️  Creating macOS Services for GRINGO..."

GRINGO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICES_DIR="$HOME/Library/Services"

# Create Services directory if it doesn't exist
mkdir -p "$SERVICES_DIR"

# Create Automator services
create_service() {
    local service_name="$1"
    local action="$2"
    local service_path="$SERVICES_DIR/${service_name}.workflow"
    
    echo "📋 Creating service: $service_name"
    
    # Create the workflow directory
    mkdir -p "$service_path/Contents"
    
    # Create Info.plist
    cat > "$service_path/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSServices</key>
    <array>
        <dict>
            <key>NSMenuItem</key>
            <dict>
                <key>default</key>
                <string>GRINGO: $service_name</string>
            </dict>
            <key>NSMessage</key>
            <string>runWorkflowAsService</string>
            <key>NSRequiredContext</key>
            <array>
                <dict>
                    <key>NSApplicationIdentifier</key>
                    <string>com.apple.finder</string>
                </dict>
            </array>
            <key>NSSendFileTypes</key>
            <array>
                <string>public.item</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
EOF

    # Create the workflow
    mkdir -p "$service_path/Contents/document.wflow/Contents"
    
    cat > "$service_path/Contents/document.wflow/Contents/document.wflow" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>512</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <true/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>2.0.3</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <dict>
                        <key>tokenizedValue</key>
                        <array>
                            <string>cd "$GRINGO_DIR" && source venv/bin/activate && for f in "\$@"; do ./gringo file $action "\$f"; done</string>
                        </array>
                    </dict>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.string</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>cd "$GRINGO_DIR" && source venv/bin/activate && for f in "\$@"; do ./gringo file $action "\$f"; done</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                </dict>
                <key>BundleIdentifier</key>
                <string>com.apple.RunShellScript</string>
                <key>CFBundleVersion</key>
                <string>2.0.3</string>
                <key>CanShowSelectedItemsWhenRun</key>
                <false/>
                <key>CanShowWhenRun</key>
                <true/>
                <key>Category</key>
                <array>
                    <string>AMCategoryUtilities</string>
                </array>
                <key>Class Name</key>
                <string>RunShellScriptAction</string>
                <key>InputUUID</key>
                <string>12345678-1234-1234-1234-123456789ABC</string>
                <key>Keywords</key>
                <array>
                    <string>Shell</string>
                    <string>Script</string>
                    <string>Command</string>
                    <string>Run</string>
                    <string>Unix</string>
                </array>
                <key>OutputUUID</key>
                <string>12345678-1234-1234-1234-123456789DEF</string>
                <key>UUID</key>
                <string>12345678-1234-1234-1234-123456789GHI</string>
                <key>UnlocalizedApplications</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>arguments</key>
                <dict>
                    <key>0</key>
                    <dict>
                        <key>default value</key>
                        <string>cd "$GRINGO_DIR" && source venv/bin/activate && for f in "\$@"; do ./gringo file $action "\$f"; done</string>
                        <key>name</key>
                        <string>COMMAND_STRING</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>0</string>
                    </dict>
                </dict>
                <key>isViewVisible</key>
                <true/>
                <key>location</key>
                <string>449.000000:316.000000</string>
                <key>nibPath</key>
                <string>/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib</string>
            </dict>
            <key>isViewVisible</key>
            <true/>
        </dict>
    </array>
    <key>connectors</key>
    <dict/>
    <key>workflowMetaData</key>
    <dict>
        <key>serviceInputTypeIdentifier</key>
        <string>com.apple.Automator.fileSystemObject</string>
        <key>serviceOutputTypeIdentifier</key>
        <string>com.apple.Automator.nothing</string>
        <key>serviceApplicationBundleIdentifier</key>
        <string>com.apple.finder</string>
        <key>workflowTypeIdentifier</key>
        <string>com.apple.Automator.servicesMenu</string>
    </dict>
</dict>
</plist>
EOF
}

# Create services for common actions
create_service "Review File" "review"
create_service "Summarize File" "summarize" 

echo "✅ macOS Services created successfully!"
echo ""
echo "🔄 To activate the services:"
echo "   1. Go to System Preferences > Keyboard > Shortcuts > Services"
echo "   2. Look for 'GRINGO: Review File' and 'GRINGO: Summarize File'"
echo "   3. Check the boxes to enable them"
echo "   4. Optionally assign keyboard shortcuts"
echo ""
echo "📁 Right-click any file in Finder and look for GRINGO options in the Services menu"
