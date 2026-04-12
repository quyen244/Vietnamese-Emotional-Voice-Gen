"""
Vn-EmoVoice Model Downloader

This script utilizes huggingface_hub to download the required VibeVoice/GPT-SoVITS
models to the local models directory.
"""
import os
import argparse
from huggingface_hub import snapshot_download

# Default repository indicating where the Vietnamese fine-tuned VibeVoice checkpoints reside
DEFAULT_REPO = "microsoft/vibe-voice-v1"  # Placeholder
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

def download_models(repo_id: str, local_dir: str):
    """
    Download model files from Hugging Face Hub.
    """
    print(f"[*] Downloading models from '{repo_id}' to '{local_dir}'...")
    os.makedirs(local_dir, exist_ok=True)
    
    try:
        # We download specific patterns or the whole repo
        # Here we download the whole repo snapshot
        snapshot_path = snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            # Uncomment if you only want specific files
            # allow_patterns=["*.pt", "*.json", "*.yaml", "*.bin"] 
        )
        print(f"[+] Successfully downloaded models to: {snapshot_path}")
    except Exception as e:
        print(f"[-] Failed to download models: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download VibeVoice Models")
    parser.add_argument(
        "--repo", 
        type=str, 
        default=DEFAULT_REPO,
        help="Hugging Face Repository ID to download from"
    )
    args = parser.parse_args()
    
    print("=== Vn-EmoVoice Model Downloader ===")
    download_models(args.repo, MODELS_DIR)
