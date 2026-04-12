# Vn-EmoVoice Deployment Guide

This document outlines how to deploy the Vn-EmoVoice TTS system across various environments, from a local machine mock deployment to a full AWS production setup.

## 1. Local Development Setup

To run the system locally for development or testing:

1. **Clone & Setup Environment**
   ```bash
   git clone <your-repo-url>
   cd Voice-Gen
   # Windows:
   setup.bat
   # Linux/Mac:
   chmod +x setup.sh && ./setup.sh
   ```

2. **Download Models**
   The setup scripts prompt to download models. Alternatively, run:
   ```bash
   python tools/download_models.py --repo "microsoft/vibe-voice-v1"
   ```

3. **Start the Server**
   ```bash
   uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
   ```
   *The Gradio interface will be automatically mounted and available at `http://localhost:8000`.*

---

## 2. Mock Public Deployment (Cloudflare Tunnel)

To quickly share your local model instance with others or test webhook integrations without setting up a cloud server:

1. **Install Cloudflared**
   Follow the [official Cloudflare instructions](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) to install the `cloudflared` daemon.

2. **Launch the Application**
   Ensure your local FastAPI server is running on port 8000.

3. **Establish Tunnel**
   ```bash
   # Windows (Git Bash/WSL) or Linux/Mac
   chmod +x tools/cloudflare_tunnel.sh
   ./tools/cloudflare_tunnel.sh
   ```
   *Cloudflare will provide a `.trycloudflare.com` URL that exposes your local port 8000 to the public internet securely.*

---

## 3. AWS Production Deployment (EC2 GPU)

For a highly available, performant deployment using Docker and Nginx on AWS:

### Step 3.1: Provision AWS EC2 Instance
1. Go to your AWS EC2 Console.
2. Launch a **G4dn** or **G5** instance type (e.g., `g4dn.xlarge` for basic T4 GPU).
3. Select an **Ubuntu Deep Learning AMI** (these come pre-configured with CUDA drivers).
4. Assign at least **100GB EBS storage** (models are large).
5. Ensure your Security Group allows inbound traffic on **Port 80 (HTTP)**, **Port 443 (HTTPS)**, and **Port 22 (SSH)**.

### Step 3.2: Prepare Instance
SSH into the instance:
```bash
ssh -i your-key.pem ubuntu@<ec2-public-ip>
```

Install Docker and Docker Compose (if not included in AMI):
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
# Log out and log back in to apply group changes
```

### Step 3.3: Deploy Code & Models
Clone the repository to the EC2 instance:
```bash
git clone <your-repo-url> vn-emovoice
cd vn-emovoice
```

*(Optional)* Download models using the script as detailed in the local setup. To avoid redownloading models on every container redeploy, it is recommended to keep them in a mounted volume `./models`.

### Step 3.4: Configure Docker & GPU
Enable GPU support in `docker-compose.yml`. Uncomment the lines under `deploy -> resources`:
```yaml
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Build and bring up the containerized stack:
```bash
docker-compose up --build -d
```

### Step 3.5: Verify Deployment
Nginx will be routing traffic from Port 80 to the FastAPI/Gradio backend.
You can now access your server via its public IPv4 address: `http://<ec2-public-ip>/`.

### Step 3.6: SSL and HTTPS (Certbot)
To secure the WebSocket connection (crucial for streaming!) and enable HTTPS, use Let's Encrypt.
```bash
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Ensure your domain (e.g., ai.yourdomain.com) points to your EC2 IP.
sudo certbot --nginx -d ai.yourdomain.com
```
*Certbot will automatically modify your Nginx config. Restart docker-compose services afterwards.*
