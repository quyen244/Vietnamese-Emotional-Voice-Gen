#!/bin/bash
# setup.sh

echo "=================================="
echo " Vn-EmoVoice Setup Script (Linux/Mac) "
echo "=================================="

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment .venv..."
    python3 -m venv .venv
else
    echo "[*] Virtual environment .venv already exists."
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "[*] Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p models
mkdir -p data/outputs

# Prompt to download models
read -p "Do you want to download the model weights now? (y/n): " download_ans
if [ "$download_ans" = "y" ]; then
    echo "[*] Triggering model downloader..."
    python tools/download_models.py
else
    echo "[*] Skipping model download. You can run 'python tools/download_models.py' later."
fi

echo "[+] Setup complete! Run 'source .venv/bin/activate' to activate the environment."
echo "[+] Starting server: 'python scripts/start_server.py' (or 'uvicorn src.api:app')"
