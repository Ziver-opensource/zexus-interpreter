#!/bin/bash
echo "🚀 Installing Zexus Syntax Highlighting for VS Code..."

# Detect VS Code extensions directory
if [ -d "$HOME/.vscode/extensions" ]; then
    EXT_DIR="$HOME/.vscode/extensions"
elif [ -d "$HOME/.vscode-oss/extensions" ]; then
    EXT_DIR="$HOME/.vscode-oss/extensions"  
else
    echo "❌ Could not find VS Code extensions directory"
    echo "Please install manually by copying this folder to your VS Code extensions directory"
    exit 1
fi

# Copy syntax highlighting
ZEXUS_SYNTAX_DIR="$EXT_DIR/zexus-language-0.1.0"
mkdir -p "$ZEXUS_SYNTAX_DIR"
cp -r . "$ZEXUS_SYNTAX_DIR/"

echo "✅ Zexus syntax highlighting installed!"
echo "📁 Location: $ZEXUS_SYNTAX_DIR"
echo "🔧 Restart VS Code to activate the syntax highlighting"
echo ""
echo "💡 Create a test file with .zx extension to see the syntax highlighting!"
