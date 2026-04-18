#!/bin/bash
echo "Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    echo ""
    echo "Python 3 is not installed."
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Install it from: https://www.python.org/downloads/"
        echo "Or via Homebrew: brew install python"
    else
        echo "Install it with: sudo apt install python3"
        echo "Or:              sudo dnf install python3"
    fi
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Python found. Starting KAIROS installer..."
echo ""
python3 install.py