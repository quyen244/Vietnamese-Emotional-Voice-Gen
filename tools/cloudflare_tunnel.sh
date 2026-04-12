#!/bin/bash
# Mock Deployment via Cloudflare Tunnel
# This quickly exposes your local Port 8000/80 (from Docker) to the world.

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "[-] cloudflared could not be found. Please install it first:"
    echo "    Linux/macOS: brew install cloudflare/cloudflare/cloudflared or equivalent"
    echo "    Windows: choco install cloudflared"
    exit 1
fi

echo "[*] Launching Cloudflare Tunnel for Vn-EmoVoice..."
echo "[!] Ensure your Docker container / Uvicorn server is running locally on Port 8000!"
echo ""

# Expose port 8000. Alternatively expose port 80 if utilizing nginx.
cloudflared tunnel --url http://localhost:8000
